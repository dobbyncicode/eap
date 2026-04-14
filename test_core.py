#!/usr/bin/env python3
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent))
import core


class TestFindProjectConfig(unittest.TestCase):
    def test_finds_config_in_current_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".eap.toml"
            config_path.write_text("[env]\nFOO=bar\n")
            with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                result = core.find_project_config()
                self.assertEqual(result, config_path)

    def test_finds_config_in_parent_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            config_path = Path(tmpdir) / ".eap.toml"
            config_path.write_text("[env]\nFOO=bar\n")
            with patch("pathlib.Path.cwd", return_value=Path(subdir)):
                result = core.find_project_config()
                self.assertEqual(result, config_path)

    def test_returns_none_when_no_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                result = core.find_project_config()
                self.assertIsNone(result)


class TestLoadConfig(unittest.TestCase):
    def test_loads_valid_toml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('[env]\nFOO = "bar"\n[path]\nadd = ["/tmp"]\n')
            f.flush()
            try:
                result = core.load_config(Path(f.name))
                self.assertEqual(result["env"]["FOO"], "bar")
                self.assertEqual(result["path"]["add"], ["/tmp"])
            finally:
                os.unlink(f.name)

    def test_returns_defaults_for_missing_file(self):
        result = core.load_config(None)
        self.assertEqual(result, {"env": {}, "path": {"add": []}})

    def test_returns_defaults_for_invalid_toml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("not valid toml [[\n")
            f.flush()
            try:
                with self.assertWarns(UserWarning):
                    result = core.load_config(Path(f.name))
                    self.assertEqual(result, {"env": {}, "path": {"add": []}})
            finally:
                os.unlink(f.name)


class TestMergeConfigs(unittest.TestCase):
    def test_merges_env_vars(self):
        a: core.Config = {"env": {"A": "1"}, "path": {"add": ["/a"]}}
        b: core.Config = {"env": {"B": "2"}, "path": {"add": ["/b"]}}
        result = core.merge_configs(a, b)
        self.assertEqual(result["env"], {"A": "1", "B": "2"})
        self.assertEqual(result["path"]["add"], ["/b", "/a"])

    def test_global_comes_first(self):
        a: core.Config = {"env": {"KEY": "global"}, "path": {"add": ["/global"]}}
        b: core.Config = {"env": {"KEY": "project"}, "path": {"add": ["/project"]}}
        result = core.merge_configs(a, b)
        self.assertEqual(result["env"]["KEY"], "project")
        self.assertEqual(result["path"]["add"], ["/project", "/global"])


class TestGenerateExports(unittest.TestCase):
    @patch("core.get_config")
    @patch("core.get_shell_templates")
    def test_generates_exports(self, mock_templates: MagicMock, mock_config: MagicMock):
        mock_config.return_value = {
            "env": {"FOO": "bar"},
            "path": {"add": ["/my/bin"]},
        }
        mock_templates.return_value = {
            "env": 'export {k}="{v}";',
            "path": 'export PATH="{p}:$PATH";',
        }
        result = core.generate_exports("bash")
        self.assertIn('export FOO="bar";', result)
        self.assertIn('export PATH="/my/bin:$PATH";', result)


class TestVersion(unittest.TestCase):
    def test_version_number_exists(self):
        self.assertIsNotNone(core.VERSION)
        self.assertTrue(core.VERSION.startswith("0."))


class TestCmdSync(unittest.TestCase):
    @patch("core.find_project_config")
    @patch("core.Path.exists", return_value=False)
    def test_cmd_sync_no_config(self, mock_exists, mock_find):
        with patch("sys.stdout", new=io.StringIO()) as mock_out:
            core.cmd_sync("bash", None)
            output = mock_out.getvalue()
            self.assertIn("EAP_LAST_MTIME", output)

    @patch("core.get_config")
    @patch("core.Path.exists", return_value=True)
    @patch("core.Path.stat")
    def test_cmd_sync_with_mtime_change(self, mock_stat, mock_exists, mock_get_config):
        mock_stat.return_value.st_mtime = 12345.0
        mock_get_config.return_value = {"env": {}, "path": {"add": []}}
        with patch("sys.stdout", new=io.StringIO()) as mock_out:
            core.cmd_sync("bash", "0")
            output = mock_out.getvalue()
            self.assertIn("EAP_LAST_MTIME", output)
            self.assertIn("12345.0", output)

    @patch("core.get_config")
    @patch("core.Path.exists", return_value=True)
    @patch("core.Path.stat")
    def test_cmd_sync_nushell_returns_json(
        self, mock_stat, mock_exists, mock_get_config
    ):
        mock_stat.return_value.st_mtime = 12345.0
        mock_get_config.return_value = {
            "env": {"FOO": "bar"},
            "path": {"add": ["/bin"]},
        }
        with patch("sys.stdout", new=io.StringIO()) as mock_out:
            core.cmd_sync("nu", "0")
            output = mock_out.getvalue()
            import json

            result = json.loads(output)
            self.assertEqual(result["FOO"], "bar")
            self.assertIn("/bin", result["PATH"])

    @patch("core.get_config")
    @patch("core.Path.exists", return_value=True)
    @patch("core.Path.stat")
    def test_cmd_sync_nushell_empty_path(self, mock_stat, mock_exists, mock_get_config):
        mock_stat.return_value.st_mtime = 12345.0
        mock_get_config.return_value = {"env": {}, "path": {"add": []}}
        with patch("sys.stdout", new=io.StringIO()):
            with patch.dict(os.environ, {"PATH": ""}):
                core.cmd_sync("nu", "0")


class TestCmdHelp(unittest.TestCase):
    def test_cmd_help_output(self):
        with patch("sys.stdout", new=io.StringIO()) as mock_out:
            core.cmd_help()
            output = mock_out.getvalue()
            self.assertIn("eap:", output)
            self.assertIn("activate", output)
            self.assertIn("sync", output)
            self.assertIn("version", output)
            self.assertIn("help", output)


class TestCmdActivate(unittest.TestCase):
    @patch("subprocess.run")
    def test_cmd_activate_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="export FOO=bar\n", stderr=""
        )
        with patch("sys.stdout", new=io.StringIO()) as mock_out:
            core.cmd_activate("bash")
            self.assertIn("export FOO=bar", mock_out.getvalue())

    @patch("subprocess.run")
    def test_cmd_activate_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        with self.assertRaises(SystemExit) as ctx:
            core.cmd_activate("bash")
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()

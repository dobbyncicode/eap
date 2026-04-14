#!/usr/bin/env python3
import os
import sys
import warnings
from pathlib import Path

VERSION = "0.1.0"

try:
    import tomllib
except ImportError:
    import tomli as tomllib


from typing import Any, TypeAlias

Config: TypeAlias = dict[str, Any]


def find_project_config() -> Path | None:
    cwd = Path.cwd()
    while cwd != cwd.parent:
        cfg = cwd / ".eap.toml"
        if cfg.exists():
            return cfg
        cwd = cwd.parent
    return None


def load_config(path: Path | None) -> Config:
    if not path or not path.exists():
        return {"env": {}, "path": {"add": []}}
    try:
        with open(path, "rb") as f:
            result: Config = tomllib.load(f)
            return result
    except Exception as e:
        warnings.warn(f"Failed to parse config at {path}: {e}", stacklevel=2)
        return {"env": {}, "path": {"add": []}}


def merge_configs(global_cfg: Config, project_cfg: Config) -> Config:
    # De-duplicate paths while preserving order (project paths first)
    project_paths = project_cfg.get("path", {}).get("add", [])
    global_paths = global_cfg.get("path", {}).get("add", [])

    # Preserve order: project first, then global (excluding duplicates)
    seen: set[str] = set()
    unique_paths: list[str] = []
    for p in project_paths + global_paths:
        expanded = os.path.expanduser(p)
        if expanded not in seen:
            seen.add(expanded)
            unique_paths.append(p)

    return {
        "env": {**global_cfg.get("env", {}), **project_cfg.get("env", {})},
        "path": {"add": unique_paths},
    }


def get_config() -> Config:
    global_path = Path("~/.config/eap/config.toml").expanduser()
    project_path = find_project_config()
    return merge_configs(
        load_config(global_path),
        load_config(project_path),
    )


def get_shell_templates(shell: str) -> dict[str, str]:
    config_path = Path("~/.config/eap/shells.toml").expanduser()
    try:
        with open(config_path, "rb") as f:
            templates: Config = tomllib.load(f)
            result = templates.get(shell) or templates.get("default")
            if result:
                return result
    except Exception:
        pass

    return {
        "env": 'export {k}="{v}";',
        "path": 'export PATH="{p}:$PATH";',
    }


def generate_exports(shell: str) -> str:
    cfg = get_config()
    tmpl = get_shell_templates(shell)

    env_tmpl = tmpl.get("env", 'export {k}="{v}";')
    path_tmpl = tmpl.get("path", 'export PATH="{p}:$PATH";')

    lines: list[str] = []
    for key, val in cfg["env"].items():
        lines.append(env_tmpl.format(k=key, v=val))

    for p in cfg["path"]["add"]:
        p_expanded = os.path.expanduser(p)
        lines.append(path_tmpl.format(p=p_expanded))

    return "\n".join(lines)


def cmd_sync(shell: str, last_mtime: str | None) -> None:
    gp = Path("~/.config/eap/config.toml").expanduser()
    pp = find_project_config()

    times: list[float] = []
    if gp.exists():
        times.append(gp.stat().st_mtime)
    if pp:
        times.append(pp.stat().st_mtime)

    current_mtime = str(max(times)) if times else "0"

    if current_mtime != (last_mtime or ""):
        if shell == "nu":
            cfg = get_config()
            record: dict[str, str | list[str]] = {**cfg["env"]}
            existing_path = os.environ.get("PATH", "")
            new_paths = ":".join(os.path.expanduser(p) for p in cfg["path"]["add"])
            if new_paths and existing_path:
                record["PATH"] = f"{new_paths}:{existing_path}"
            elif new_paths:
                record["PATH"] = new_paths
            else:
                record["PATH"] = existing_path
            print(__import__("json").dumps(record))
        else:
            exports = generate_exports(shell)
            if not exports:
                exports = ":"
            mtime_export = (
                f'export EAP_LAST_MTIME="{current_mtime}";'
                if shell != "fish"
                else f"set -gx EAP_LAST_MTIME {current_mtime};"
            )
            print(f"{exports}\n{mtime_export}")


def cmd_version() -> None:
    print(f"eap {VERSION}")


def cmd_activate(shell: str) -> None:
    import subprocess

    activate_sh = Path(__file__).parent / "activate.sh"
    result = subprocess.run(
        ["sh", str(activate_sh), shell],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    print(result.stdout, end="")


def cmd_help() -> None:
    print("""eap: Environment and Path manager.

Usage:
  eap help
  eap version
  eap activate <shell>
  eap sync <shell> [last_mtime]

Options:
  activate  Generate shell activation hooks
  sync      Output environment exports for shell
  help      Show this help message
  version   Show version

Config:
  - Global config: ~/.config/eap/config.toml
  - Project config: .eap.toml

Format:
  [env]
  KEY = "value"

  [path]
  add = ["/path/to/bin"]
""")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "help":
        cmd_help()
        return

    if cmd == "version":
        cmd_version()
        return

    if cmd == "activate":
        if len(sys.argv) < 3:
            sys.exit(1)
        cmd_activate(sys.argv[2])
        return

    if len(sys.argv) < 3:
        sys.exit(1)

    shell = sys.argv[2]
    last_mtime = sys.argv[3] if len(sys.argv) > 3 else None

    if cmd == "sync":
        cmd_sync(shell, last_mtime)


if __name__ == "__main__":
    main()

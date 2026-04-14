# eap Reference

Minimalist environment and path manager.

## Quick Install
```bash
curl -sSL https://cdn.jsdelivr.net/gh/dobbyncicode/eap@v0.1.1/install.sh | sh
```

If that doesn't work, try the commit SHA:
```bash
curl -sSL https://cdn.jsdelivr.net/gh/dobbyncicode/eap@e2b290f/install.sh | sh
```

Or install from GitHub directly:
```bash
curl -sSL https://raw.githubusercontent.com/dobbyncicode/eap/prod/install.sh | sh
```

## Requirements
- Python 3.11+ (uses built-in `tomllib`)
- For Python 3.10 and earlier: `pip install tomli`

> **Security Note**: Environment variables set via eap may be visible in process listings (`ps`, `top`). Avoid storing sensitive secrets (passwords, API keys, tokens) in `config.toml`. Use a secrets manager instead.

## Activation
Add the exact line corresponding to your shell to your configuration file.

### Zsh
Add to `~/.zshrc`:
```zsh
eval "$(~/.local/bin/eap activate zsh)"
```

### Bash
Add to `~/.bashrc`:
```bash
eval "$(~/.local/bin/eap activate bash)"
```

### Fish
Add to `~/.config/fish/config.fish`:
```fish
eval (~/.local/bin/eap activate fish | string collect)
```

### NuShell
Add to `env.nu` or `config.nu`:
```nushell
eval (eap activate nu)
```

---

## Configuration

### 1. User Config (`~/.config/eap/config.toml`)
Define your variables and paths here.

**Structure:**
- `[env]`: Key-value pairs for environment variables.
- `[path]`: A list of folders to add to your system PATH.

**Example:**
```toml
[env]
EDITOR = "nvim"

[path]
add = ["~/.local/bin", "~/scripts"]
```

### 2. Project Config (`.eap.toml`)
Place this file in any project directory to override global settings for that folder and its subfolders. Use the same structure as `config.toml`.

---

## Extending Shells (`~/.config/eap/shells.toml`)

If you use a shell not listed by default, add it to `shells.toml`. eap uses simple templates to generate the export commands.

**Available Variables:**
- `{k}`: The variable key (e.g., `EDITOR`)
- `{v}`: The variable value (e.g., `nvim`)
- `{p}`: The path string (e.g., `/home/user/.local/bin`)

**Example: Adding a custom shell**
```toml
[my-shell]
env = 'export {k}="{v}";'
path = 'export PATH="{p}:$PATH";'
```

## Internal Logic
- **Sync**: eap monitors the modification time (mtime) of your config files.
- **Trigger**: The environment is refreshed automatically when the shell prompt is displayed.
- **Precedence**: Project `.eap.toml` $\rightarrow$ Global `config.toml`.

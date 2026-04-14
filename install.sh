#!/bin/sh

set -e

REPO_URL="https://cdn.jsdelivr.net/gh/dobbyncicode/eap@prod"

mkdir -p "$HOME/.eap"
mkdir -p "$HOME/.config/eap"

echo "Downloading eap files..."
curl -sSL "$REPO_URL/core.py" -o "$HOME/.eap/core.py"
curl -sSL "$REPO_URL/activate.sh" -o "$HOME/.eap/activate.sh"
curl -sSL "$REPO_URL/uninstall.sh" -o "$HOME/.eap/uninstall.sh"

cp "$HOME/.eap/core.py" "$HOME/.local/bin/eap"

chmod +x "$HOME/.eap/core.py"
chmod +x "$HOME/.local/bin/eap"

if [ ! -f "$HOME/.config/eap/config.toml" ]; then
    cat << 'EOF' > "$HOME/.config/eap/config.toml"
[env]

[path]
add = [
    "~/.local/bin"
]
EOF
fi

if [ ! -f "$HOME/.config/eap/shells.toml" ]; then
    cat << 'EOF' > "$HOME/.config/eap/shells.toml"
[zsh]
env = 'export {k}="{v}";'
path = 'export PATH="{p}:$PATH";'

[bash]
env = 'export {k}="{v}";'
path = 'export PATH="{p}:$PATH";'

[fish]
env = 'set -gx {k} "{v}";'
path = 'fish_add_path {p};'

[nu]
env = '{k} = "{v}"'
path = 'PATH = ["{p}", ..PATH]'

[default]
env = 'export {k}="{v}";'
path = 'export PATH="{p}:$PATH";'
EOF
fi

echo "Done."
echo "Add to your shell config: eval \"\$($HOME/.local/bin/eap activate <shell>)\""

if [ ! -f "$HOME/.config/eap/config.toml" ]; then
    cat << 'EOF' > "$HOME/.config/eap/config.toml"
[env]

[path]
add = [
    "~/.local/bin"
]
EOF
fi

if [ ! -f "$HOME/.config/eap/shells.toml" ]; then
    cat << 'EOF' > "$HOME/.config/eap/shells.toml"
[zsh]
env = 'export {k}="{v}";'
path = 'export PATH="{p}:$PATH";'

[bash]
env = 'export {k}="{v}";'
path = 'export PATH="{p}:$PATH";'

[fish]
env = 'set -gx {k} "{v}";'
path = 'fish_add_path {p};'

[nu]
env = '{k} = "{v}"'
path = 'PATH = ["{p}", ..PATH]'

[default]
env = 'export {k}="{v}";'
path = 'export PATH="{p}:$PATH";'
EOF
fi

echo "Done."
echo "Add to your shell config: eval \"\$($HOME/.local/bin/eap activate <shell>)\""
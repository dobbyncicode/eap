#!/bin/sh
set -e

LATEST_SHA=$(curl -s "https://api.github.com/repos/dobbyncicode/eap/commits/prod" | grep '"sha"' | head -1 | cut -d'"' -f4)
BASE_URL="https://cdn.jsdelivr.net/gh/dobbyncicode/eap@$LATEST_SHA"

mkdir -p "$HOME/.local/bin"
mkdir -p "$HOME/.eap"
mkdir -p "$HOME/.config/eap"

echo "Downloading eap files..."
curl -sSL "$BASE_URL/core.py" -o "$HOME/.eap/core.py"
curl -sSL "$BASE_URL/activate.sh" -o "$HOME/.eap/activate.sh"
curl -sSL "$BASE_URL/uninstall.sh" -o "$HOME/.eap/uninstall.sh"

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
echo "Add to your shell config:"
echo "  Bash:   eval \"\$(~/.local/bin/eap activate bash)\""
echo "  Zsh:    eval \"\$(~/.local/bin/eap activate zsh)\""
echo "  Fish:   eval (\~/.local/bin/eap activate fish | string collect)"
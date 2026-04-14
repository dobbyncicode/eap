#!/bin/sh

set -e

case ":$PATH:" in
    *:"$HOME/.local/bin":*) ;;
    *) export PATH="$HOME/.local/bin:$PATH" ;;
esac

echo "Installing eap..."

mkdir -p "$HOME/.eap"
mkdir -p "$HOME/.config/eap"

cp core.py activate.sh uninstall.sh "$HOME/.eap/"
cp core.py "$HOME/.local/bin/eap"

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
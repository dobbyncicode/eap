#!/bin/sh

set -e

echo "Uninstalling eap..."

rm -f "$HOME/.local/bin/eap"
rm -rf "$HOME/.eap"
rm -rf "$HOME/.config/eap"

echo "Done."
echo "Remove the activation line from your shell config file."
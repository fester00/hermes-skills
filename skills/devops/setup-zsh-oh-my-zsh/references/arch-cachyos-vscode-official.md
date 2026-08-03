# Official Microsoft VS Code on Arch / CachyOS / Manjaro

The user explicitly prefers the **official Microsoft build** of VS Code over the AUR `visual-studio-code-bin` package and over the open-source `code` package in Arch repos, because the AUR build can fail to connect to the Extension Marketplace.

## When to use this recipe

- Target is Arch, CachyOS, Manjaro, or another pacman-based distro.
- User asked for VS Code and wants full Marketplace/extension support.
- User said "don't use AUR" or similar.

## Recipe

```bash
#!/bin/bash
set -e

VSCODE_URL="https://update.code.visualstudio.com/latest/linux-x64/stable"
VSCODE_TARBALL="/tmp/vscode-stable.tar.gz"
VSCODE_DIR="/opt/visual-studio-code"

# Download official Microsoft build
curl -L --max-time 300 "$VSCODE_URL" -o "$VSCODE_TARBALL"

# Install into /opt
sudo mkdir -p "$VSCODE_DIR"
sudo rm -rf "$VSCODE_DIR"/*
sudo tar -xzf "$VSCODE_TARBALL" -C "$VSCODE_DIR" --strip-components=1

# Symlink binary into PATH
sudo ln -sf "$VSCODE_DIR/bin/code" /usr/local/bin/code

# Optional: desktop entry for launchers
sudo cp "$VSCODE_DIR/resources/app/resources/linux/code.png" /usr/share/pixmaps/visual-studio-code.png || true
sudo tee /usr/share/applications/visual-studio-code.desktop > /dev/null <<'DESKTOP'
[Desktop Entry]
Name=Visual Studio Code
Comment=Code Editing. Redefined.
Exec=/opt/visual-studio-code/bin/code --unity-launch %F
Icon=visual-studio-code
Type=Application
StartupNotify=false
StartupWMClass=Code
Categories=TextEditor;Development;IDE;
MimeType=text/plain;inode/directory;
Actions=new-empty-window;
Keywords=vscode;

[Desktop Action new-empty-window]
Name=New Empty Window
Exec=/opt/visual-studio-code/bin/code --new-window %F
Icon=visual-studio-code
DESKTOP

rm -f "$VSCODE_TARBALL"
code --version
```

## Why not other options?

| Package | Why avoid / caveat |
|---------|------------------|
| `visual-studio-code-bin` (AUR) | User reported Marketplace connection issues. |
| `code` (Arch `extra`, CachyOS `cachyos-extra-v3`) | Open-source build; Marketplace access may be limited. |
| Microsoft `.deb` via debtap | Unnecessary complexity; the official tarball works natively. |

## After install

- `code` is available system-wide via `/usr/local/bin/code`.
- Desktop environments and Wayland compositors (including niri) can use the `.desktop` entry.

## Notes

- This recipe requires `curl`, `tar`, and root/sudo rights.
- The download URL is the Microsoft official update endpoint and always returns the latest stable build.

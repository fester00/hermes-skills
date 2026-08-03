# Remote automation on CachyOS / Arch over SSH

Session-specific recipes for driving installs and fixes on a CachyOS (Arch-based) machine from another host via SSH, especially when the user account has a password-protected sudo and the login shell is fish.

## SSH port closed but sshd is running

Symptom: `nc -vz HOST 22` times out, yet on the target `systemctl status sshd` shows it listening on 0.0.0.0:22.

Likely cause: **UFW / iptables default INPUT policy DROP** with no rule for port 22.

Fix on target:

```bash
sudo ufw allow ssh
sudo ufw status verbose
```

Verify from remote:

```bash
nc -vz HOST 22
ssh user@HOST
```

## Running sudo commands non-interactively over SSH

`sshpass ... ssh 'sudo ...'` fails with `a terminal is required to read the password` because sudo wants a TTY. Two options:

### Option A: Temporary SUDO_ASKPASS helper (used in this session)

On the target, create an askpass script containing the sudo password:

```bash
#!/bin/bash
echo "nat1789418"
```

Make it executable, then run commands with `SUDO_ASKPASS`:

```bash
chmod 700 /tmp/askpass.sh
export SUDO_ASKPASS=/tmp/askpass.sh
sudo -A pacman -S --needed --noconfirm zsh
sudo -A usermod --shell /bin/zsh "$USER"
rm -f /tmp/askpass.sh
```

**Security:** do this only over a trusted local network, and delete the helper immediately.

### Option B: Build packages as user, install via sudo -A

Example for `yay` on CachyOS when no AUR helper exists:

```bash
cd /tmp
git clone https://aur.archlinux.org/yay.git yay-build
cd yay-build
makepkg --noconfirm
export SUDO_ASKPASS=/tmp/askpass.sh
sudo -A pacman -U ./yay-*.pkg.tar.zst --noconfirm
```

## Passing scripts when the remote login shell is fish

Fish handles quoting and heredocs differently from bash. Instead of long inline `ssh ... 'bash -lc "..."'` commands with complex escaping, write a bash script locally and copy it with `scp`:

```bash
# local
scp /tmp/setup_cachyos.sh parazit@192.168.0.121:/tmp/setup_cachyos.sh
ssh parazit@192.168.0.121 'bash /tmp/setup_cachyos.sh'
```

This avoids fish parsing surprises entirely.

## Installing official Microsoft VS Code on CachyOS

The user prefers the official Microsoft build over the AUR `visual-studio-code-bin` and the open-source `code` package, because of Extension Marketplace issues.

See full recipe: `references/arch-cachyos-vscode-official.md`.

Quick summary:

```bash
VSCODE_URL="https://update.code.visualstudio.com/latest/linux-x64/stable"
curl -L "$VSCODE_URL" -o /tmp/vscode-stable.tar.gz
sudo mkdir -p /opt/visual-studio-code
sudo rm -rf /opt/visual-studio-code/*
sudo tar -xzf /tmp/vscode-stable.tar.gz -C /opt/visual-studio-code --strip-components=1
sudo ln -sf /opt/visual-studio-code/bin/code /usr/local/bin/code
```

## Useful verification commands

```bash
getent passwd "$USER" | cut -d: -f7       # default login shell
echo "$SHELL"                             # shell of current session
which code
code --version | head -3
grep ZSH_THEME ~/.zshrc
ls ~/.oh-my-zsh/custom/themes/fox.zsh-theme
```

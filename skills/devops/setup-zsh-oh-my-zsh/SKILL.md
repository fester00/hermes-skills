---
name: setup-zsh-oh-my-zsh
description: Install zsh and Oh My Zsh, set a theme, enable plugins, and switch the default shell on Ubuntu/Debian and Arch-based Linux.
title: Setup zsh + Oh My Zsh on Linux
category: devops
tags: [zsh, oh-my-zsh, shell, ubuntu, arch, cachyos, terminal]
author: hermes
version: 1.0
---

# Setup zsh + Oh My Zsh on Ubuntu/Linux

Installs `zsh`, `oh-my-zsh`, selects a theme, enables useful plugins, and explains how to set zsh as the default shell.

## When to use

- User asks to install zsh and/or oh-my-zsh.
- User wants a specific OMZ theme or plugin set.
- Target is Ubuntu/Debian, Arch, CachyOS, or another pacman-based distro.

## Procedure

### 1. Check current state

```bash
which zsh
 echo $SHELL
 grep '^ID=' /etc/os-release
```

If `zsh` is missing, install it with the distro's package manager:

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install -y zsh
```

**Arch / CachyOS / Manjaro:**
```bash
sudo pacman -S --needed --noconfirm zsh
```

### 2. Install Oh My Zsh unattended

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
```

This creates `~/.oh-my-zsh` and copies the template to `~/.zshrc`.

### 3. Set the theme

Find the line in `~/.zshrc`:

```bash
ZSH_THEME="robbyrussell"
```

Replace with the desired theme, e.g.:

```bash
ZSH_THEME="fox"
```

For users with a dark/minimal preference, `fox` is a compact single-line prompt. Available themes: https://github.com/ohmyzsh/ohmyzsh/wiki/Themes

### 4. Enable plugins

Recommended set for this user's stack (web dev, Node, Docker, Rust):

```bash
plugins=(git node npm docker docker-compose sudo command-not-found z rust)
```

Edit `~/.zshrc` and replace the `plugins=(git)` line.

### 5. Useful options

Uncomment or add these in `~/.zshrc`:

```bash
COMPLETION_WAITING_DOTS="true"
HIST_STAMPS="dd.mm.yyyy"
```

### 6. Verify config loads

```bash
zsh -c "echo 'zsh loaded OK'"
```

### 7. Make zsh the default shell

```bash
chsh -s $(which zsh)
```

This requires the user's password. If it fails non-interactively, use `sudo usermod --shell $(which zsh) "$USER"` (requires root/sudo rights) or ask the user to run `chsh` manually, then re-login or open a new terminal.

**Note:** `chsh` locks the password prompt and cannot be fed a password via stdin on some systems. When automating over SSH, prefer `sudo usermod --shell /bin/zsh "$USER"` if passwordless sudo or an `SUDO_ASKPASS` helper is available.

Verify after re-login:

```bash
echo $SHELL   # should print /usr/bin/zsh or similar
grep "^$(whoami):" /etc/passwd  # should end in /bin/zsh or /usr/bin/zsh
```

## Pitfalls

- `chsh` cannot be run without the user's password; do not guess. Prefer `sudo usermod --shell /bin/zsh "$USER"` for non-interactive remote installs when sudo is available.
- Hermes itself runs commands through bash regardless of user's default shell, so this install does not break terminal control.
- Environment variables and aliases defined only in `.zshrc` are not visible to non-interactive commands Hermes runs. Put system-wide env vars in `~/.profile` or `~/.zshenv`.
- **PATH for user-local tools (e.g. Hermes CLI in `~/.local/bin`)** must be added to `~/.zshrc` explicitly, not just `~/.profile`, because many terminals launch zsh as a non-login interactive shell and do not source `~/.profile`. Place the guard after `source $ZSH/oh-my-zsh.sh`:
  ```zsh
  if [[ -d "$HOME/.local/bin" ]] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
      export PATH="$HOME/.local/bin:$PATH"
  fi
  ```
- `~/.profile` is fine for login shells and bash, but zsh on Ubuntu typically reads it only in specific login/compat paths. Do not rely on `~/.profile` alone to make `hermes` or other `~/.local/bin` tools available in every terminal.
- Too many plugins slow down shell startup; keep the list focused.
- On Arch/CachyOS, the user prefers `pacman` packages over AUR helpers. Avoid AUR builds for tools that the user expects to be official (e.g. VS Code) — see `references/arch-cachyos-vscode-official.md`.

## Using Oh My Posh themes with Oh My Zsh

Oh My Posh can replace the OMZ prompt while keeping OMZ plugins, aliases, and completions. This is the fastest way to use an OMP theme (e.g. `1_shell.omp.json`) under zsh.

### Installation

```bash
curl -s https://ohmyposh.dev/install.sh | bash -s -- -d ~/.local/bin
mkdir -p ~/.config/oh-my-posh
curl -fsSL -o ~/.config/oh-my-posh/1_shell.omp.json \
  https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/1_shell.omp.json
```

### Wiring into `~/.zshrc`

1. Keep `ZSH_THEME` set to an existing OMZ theme (e.g. `robbyrussell`). Removing it or setting it to a non-existent value causes OMZ to print a warning on every shell start.
2. Ensure `~/.local/bin` is on `PATH` **before** OMZ loads, so the `oh-my-posh` binary is discoverable.
3. Initialize Oh My Posh **after** `source $ZSH/oh-my-zsh.sh`, or OMZ's theme setup will overwrite the OMP prompt.

```zsh
# Ensure user-local tools are discoverable before oh-my-zsh
export PATH="$HOME/.local/bin:$PATH"

export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"
plugins=(git)

source $ZSH/oh-my-zsh.sh

# Oh My Posh prompt (loaded after OMZ so it wins)
if (( $+commands[oh-my-posh] )); then
    eval "$(oh-my-posh init zsh --config $HOME/.config/oh-my-posh/1_shell.omp.json)"
fi
```

### Verification

```bash
zsh -il -c 'echo loaded'
```

For a visual check in a pseudo-terminal:

```bash
script -q -c 'zsh -i' /dev/null <<'EOF'
echo test
exit
EOF
```

### Pitfalls

- **Order matters:** `eval "$(oh-my-posh init zsh ...)"` must run **after** `source $ZSH/oh-my-zsh.sh`. If it runs before, OMZ's theme hooks will clobber the OMP prompt.
- **PATH timing:** `oh-my-posh` is often installed into `~/.local/bin`. If that directory is added to `PATH` only after `source $ZSH/oh-my-zsh.sh`, the `(( $+commands[oh-my-posh] ))` guard will fail on the first load and OMP will never initialize.
- **Nerd Font required:** Most OMP themes use icon glyphs. If the terminal font is not a Nerd Font, icons render as boxes or tofu. Install and select a Nerd Font in the terminal emulator (e.g. JetBrainsMono Nerd Font or MesloLGS Nerd Font).
- **No need to port the JSON:** You do not have to translate an OMP theme into an OMZ theme. The two systems are different; prompt rendering is handled by OMP, plugins/aliases by OMZ.

See also `references/oh-my-posh-with-oh-my-zsh.md` for a ready-to-use `.zshrc` snippet.

## Terminal emulator config (Alacritty / niri / Wayland)

Some Wayland compositors (e.g. **niri**) start the user session with a non-default shell (e.g. `/bin/fish`). The terminal emulator then inherits that `$SHELL`, so even after `chsh`, new terminal windows may still open in fish.

For **Alacritty 0.13+**, force zsh explicitly in `~/.config/alacritty/alacritty.toml`:

```toml
[terminal.shell]
program = "/bin/zsh"
args = ["-l"]
```

In older Alacritty (< 0.13) the deprecated key was:

```toml
[shell]
program = "/bin/zsh"
args = ["-l"]
```

If Alacritty logs a deprecation warning, migrate to `[terminal.shell]`.

Common niri keybinding for the terminal (check `~/.config/niri/cfg/keybinds.kdl`):

```kdl
Mod+Return hotkey-overlay-title="Open Terminal: Alacritty" { spawn "alacritty"; }
```

So **Super+Enter** opens Alacritty after the change.

## Remote install over SSH

When automating this install over SSH on a password-protected sudo account, `sudo` cannot read a password from stdin if it requires a TTY. Use a temporary `SUDO_ASKPASS` helper instead:

```bash
# On the remote machine, create a temporary askpass script
#!/bin/bash
echo "THE_PASSWORD"
```

Set it executable and point `SUDO_ASKPASS` at it:

```bash
export SUDO_ASKPASS=/tmp/askpass.sh
sudo -A pacman -S --needed --noconfirm zsh
sudo -A usermod --shell /bin/zsh "$USER"
```

**Clean up immediately after use:** `rm -f /tmp/askpass.sh`.

If the remote login shell is fish, complex inline quoting and heredocs often break. Prefer writing the install steps to a local bash script and copying it with `scp`, then running `bash /tmp/script.sh` on the remote host.

See also:

- `references/arch-cachyos-vscode-official.md` — official Microsoft VS Code install recipe.
- `references/arch-cachyos-remote-automation.md` — SSH + sudo + UFW troubleshooting recipes for CachyOS.

## References

- Oh My Zsh themes: https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
- Oh My Zsh plugins: https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins

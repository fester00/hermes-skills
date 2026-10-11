---
name: setup-zsh-oh-my-zsh
description: Use when setting up zsh on Linux. Install Oh My Zsh, pick a theme, enable plugins, and switch the default shell.
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
- **PATH line must be real, not commented:** A commented example like `# export PATH=$HOME/.local/bin:$PATH` does not make the binary discoverable. When automating edits, do not pattern-match `$HOME/.local/bin` naively; check for an actual, uncommented `export PATH=...` line.
- **OMZ theme conflict:** Some OMZ themes (e.g. `fox`) install aggressive prompt hooks that survive after `source $ZSH/oh-my-zsh.sh` and can overwrite the Oh My Posh prompt even if OMP is loaded later. Keep `ZSH_THEME="robbyrussell"` (or another lightweight built-in) when using Oh My Posh; OMP will replace the rendered prompt anyway.
- **Nerd Font required:** Most OMP themes use icon glyphs. If the terminal font is not a Nerd Font, icons render as boxes or tofu. Install and select a Nerd Font in the terminal emulator (e.g. JetBrainsMono Nerd Font or MesloLGS Nerd Font).
- **No need to port the JSON:** You do not have to translate an OMP theme into an OMZ theme. The two systems are different; prompt rendering is handled by OMP, plugins/aliases by OMZ.

See also `references/oh-my-posh-with-oh-my-zsh.md` for a ready-to-use `.zshrc` snippet and `references/remote-ssh-password-install.md` for installing Oh My Posh on a password-auth SSH host without interaction.

## eza: icon-rich `ls` replacement

`eza` is a modern `ls` replacement with Nerd Font icons, git highlighting, and tree output.

### Install

**Arch / CachyOS / Manjaro:**
```bash
sudo pacman -S --needed eza
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install -y eza
```

### Recommended zsh aliases

Place these **after** `source $ZSH/oh-my-zsh.sh` so they override any OMZ `ls` aliases:

```zsh
unalias ls la ll lt 2>/dev/null

alias ls='eza --icons=always --group-directories-first'
alias la='eza -a --icons=always --group-directories-first'
alias ll='eza -la --icons=always --group-directories-first'
alias lt='eza --tree --icons=always --level=2'
```

Use `--icons=always` (not bare `--icons`) so icons render even when the tool is uncertain about terminal capability.

### Pitfalls

- **No icons:** Terminal font is not a Nerd Font, or locale is `POSIX`/`C`. See the Nerd Fonts and locale sections below.
- **OMZ aliases win:** If `ls` still invokes the old command, Oh My Zsh's `lib/directories.zsh` may have loaded its own aliases. The `unalias` guard above fixes this.

## Nerd Fonts for icons

Oh My Posh and eza rely on Nerd Font glyphs. Without one, icons render as boxes or `?????`.

### Quick setup

Install a Nerd Font on the machine where the terminal emulator runs (not the SSH server, unless you use a local console there). Recommended fonts:

- **MesloLGS Nerd Font Mono** — default recommendation, wide glyphs, very compatible.
- **JetBrainsMono Nerd Font Mono** — coding-focused, clean.

### Meslo suffixes explained

| Suffix | Meaning |
|---|---|
| `LGS` | Largest, widest glyphs (best for big icons). |
| `LGM` | Medium size/width. |
| `LGL` | Taller line height, slightly more compact glyphs. |
| `SDZ` | Dotted zero (`0`). |
| `Mono` | Monospaced — required for terminal emulators. |
| `Propo` | Proportional — for documents, not terminals. |

If icons feel small, first increase the terminal font `size`; if still cramped, switch from `LGM` to `LGS`.

### Alacritty example

```toml
[font]
normal = { family = "MesloLGS Nerd Font Mono", style = "Regular" }
size = 11.0
```

Restart the terminal emulator after changing the font.

## Locale: icons require UTF-8

A `POSIX` or `C` locale will break icon rendering over SSH even if a Nerd Font is installed. Always set a UTF-8 locale in `~/.zshrc`:

```zsh
export LANG="en_US.UTF-8"
```

On Arch/CachyOS, make sure the locale is generated:

```bash
grep "^en_US.UTF-8" /etc/locale.gen
# If missing, add it and run:
sudo locale-gen
```

### Symptoms of wrong locale

- Oh My Posh icons show as `?????` or empty boxes.
- `eza --icons` does not render folder/file icons.
- `fastfetch` or `neofetch` shows `Locale: C` or `POSIX`.

The fix is the `export LANG=en_US.UTF-8` line in `~/.zshrc`, placed early enough that all icon-rendering tools inherit it.

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
- `references/oh-my-posh-with-oh-my-zsh.md` — ready-to-use `.zshrc` snippet for Oh My Posh under OMZ.
- `references/remote-ssh-password-install.md` — installing Oh My Posh on a password-auth SSH host without interaction.
- `references/nerd-fonts-for-terminal-icons.md` — choosing and configuring a Nerd Font for icon glyphs.
- `references/eza-ls-replacement.md` — replacing `ls` with `eza` for icons and color output.

## References

- Oh My Zsh themes: https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
- Oh My Zsh plugins: https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins

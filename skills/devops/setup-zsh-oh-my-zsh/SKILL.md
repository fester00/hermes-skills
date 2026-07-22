---
name: setup-zsh-oh-my-zsh
description: Install zsh and Oh My Zsh, set a theme, enable plugins, and switch the default shell on Ubuntu/Debian Linux.
title: Setup zsh + Oh My Zsh on Ubuntu/Linux
category: devops
tags: [zsh, oh-my-zsh, shell, ubuntu, terminal]
author: hermes
version: 1.0
---

# Setup zsh + Oh My Zsh on Ubuntu/Linux

Installs `zsh`, `oh-my-zsh`, selects a theme, enables useful plugins, and explains how to set zsh as the default shell.

## When to use

- User asks to install zsh and/or oh-my-zsh.
- User wants a specific OMZ theme or plugin set.
- Target is an Ubuntu/Debian-style Linux machine.

## Procedure

### 1. Check current state

```bash
which zsh
 echo $SHELL
 grep '^ID=' /etc/os-release
```

If `zsh` is missing, install it:

```bash
sudo apt update && sudo apt install -y zsh
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

Available themes: https://github.com/ohmyzsh/ohmyzsh/wiki/Themes

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

This requires the user's password. If it fails non-interactively, ask the user to run it manually, then re-login or open a new terminal.

Verify after re-login:

```bash
echo $SHELL   # should print /usr/bin/zsh or similar
echo $ZSH_THEME  # should print chosen theme, e.g. fox
```

## Pitfalls

- `chsh` cannot be run without the user's password; do not guess.
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

## References

- Oh My Zsh themes: https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
- Oh My Zsh plugins: https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins

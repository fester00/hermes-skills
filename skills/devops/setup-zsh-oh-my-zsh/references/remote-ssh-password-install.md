# Remote Oh My Posh install over password SSH

When the target host uses password authentication and Hermes’ `ssh` channel is
non-interactive, use `sshpass` to feed the password. This recipe is for
non-sudo steps (installing Oh My Posh into `~/.local/bin` and editing
`~/.zshrc`).

## Preconditions

- `sshpass` available on the local Hermes host:
  ```bash
  sudo apt-get install -y sshpass   # Debian/Ubuntu
  sudo pacman -S --needed sshpass    # Arch/CachyOS
  ```
- Target user can reach the internet from the remote host.
- Target already has zsh + Oh My Zsh installed (or install them first).

## One-shot install

```bash
USER=parazit
HOST=192.168.0.121
PASS='nat1789418'

sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" '
  set -e
  mkdir -p ~/.local/bin ~/.config/oh-my-posh
  if [[ ! -x ~/.local/bin/oh-my-posh ]]; then
    curl -s https://ohmyposh.dev/install.sh | bash -s -- -d ~/.local/bin
  fi
  curl -fsSL -o ~/.config/oh-my-posh/1_shell.omp.json \
    https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/1_shell.omp.json
'
```

## Wire into `~/.zshrc` remotely

Use a Python one-liner to avoid quoting hell across SSH:

```bash
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" 'python3 -' <<'PY'
from pathlib import Path
p = Path.home() / '.zshrc'
text = p.read_text()
backup = Path.home() / f'.zshrc.bak.{int(__import__("time").time())}'
backup.write_text(text)

# make .local/bin available
path_line = 'export PATH="$HOME/.local/bin:$PATH"\n'
if path_line.strip() not in text:
    text = text.replace('source $ZSH/oh-my-zsh.sh\n', path_line + '\nsource $ZSH/oh-my-zsh.sh\n')

# avoid OMZ theme clobbering Oh My Posh
text = text.replace('ZSH_THEME="fox"', 'ZSH_THEME="robbyrussell"')

# add oh-my-posh init if missing
if '1_shell.omp.json' not in text:
    marker = 'source $ZSH/oh-my-zsh.sh\n'
    insert = '''source $ZSH/oh-my-zsh.sh

# Oh My Posh prompt with 1_shell theme
if (( $+commands[oh-my-posh] )); then
    eval "$(oh-my-posh init zsh --config $HOME/.config/oh-my-posh/1_shell.omp.json)"
fi
'''
    text = text.replace(marker, insert)

p.write_text(text)
print('OK')
PY
```

## Verify

```bash
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" 'zsh -il -c "which oh-my-posh; echo loaded"'

# Visual prompt check in pseudo-terminal
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" 'script -q -c "zsh -i" /dev/null <<EOF
echo test
exit
EOF'
```

## Common issues

- `oh-my-posh not found` on load → `~/.local/bin` is not on PATH before the
  `(( $+commands[oh-my-posh] ))` guard. Make sure the `export PATH` line is
  uncommented and placed before `source $ZSH/oh-my-zsh.sh`.
- Old OMZ prompt still shows → `ZSH_THEME` is set to a theme (like `fox`) whose
  hooks survive after `source`. Switch to `robbyrussell`.
- Icons show as boxes/tofu → terminal font on the **client** is not a Nerd
  Font. Fix the client terminal font; the remote config is fine.

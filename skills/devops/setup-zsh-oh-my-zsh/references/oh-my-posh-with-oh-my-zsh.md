# Oh My Posh with Oh My Zsh

Ready-to-use wiring for running an Oh My Posh theme inside an Oh My Zsh environment.
Use this when the user wants a specific OMP visual theme but wants to keep OMZ plugins, completions, and aliases.

## Minimal `.zshrc` snippet

```zsh
# Path to Oh My Zsh
export ZSH="$HOME/.oh-my-zsh"

# Keep a real OMZ theme here. If you set a non-existent theme, OMZ prints a warning.
ZSH_THEME="robbyrussell"

plugins=(git)

# Make sure oh-my-posh (installed to ~/.local/bin by default) is on PATH
# before OMZ starts, so the guard below can find it.
export PATH="$HOME/.local/bin:$PATH"

source $ZSH/oh-my-zsh.sh

# Load Oh My Posh AFTER OMZ, or OMZ will overwrite the OMP prompt.
if (( $+commands[oh-my-posh] )); then
    eval "$(oh-my-posh init zsh --config $HOME/.config/oh-my-posh/1_shell.omp.json)"
fi
```

## One-line install

```bash
curl -s https://ohmyposh.dev/install.sh | bash -s -- -d ~/.local/bin
mkdir -p ~/.config/oh-my-posh
curl -fsSL -o ~/.config/oh-my-posh/1_shell.omp.json \
  https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/1_shell.omp.json
```

## Visual verification

Because Oh My Posh uses a `precmd` hook, `PROMPT` may look empty in non-interactive output. Use a pseudo-terminal to see the rendered prompt:

```bash
script -q -c 'zsh -i' /dev/null <<'EOF'
echo hello
exit
EOF
```

## Common issues

1. **Prompt still shows OMZ theme:** `oh-my-posh init zsh` is running before `source $ZSH/oh-my-zsh.sh`. Move it after.
2. **`[oh-my-zsh] theme 'X' not found`:** `ZSH_THEME` points to a missing theme. Keep a default like `robbyrussell`; OMP overrides the actual prompt anyway.
3. **`oh-my-posh: command not found` during init:** `~/.local/bin` is not in PATH when `.zshrc` reaches the guard. Export PATH early, before OMZ loads.
4. **Icons show as boxes:** Terminal font is not a Nerd Font. Install one (JetBrainsMono Nerd Font, MesloLGS Nerd Font, etc.) and set it in the terminal emulator.

## References

- Oh My Posh docs: https://ohmyposh.dev/docs/
- Oh My Posh themes: https://github.com/JanDeDobbeleer/oh-my-posh/tree/main/themes
- Oh My Zsh themes: https://github.com/ohmyzsh/ohmyzsh/wiki/Themes

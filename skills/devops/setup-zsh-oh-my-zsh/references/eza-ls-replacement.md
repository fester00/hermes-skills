# eza as a Colorful `ls` Replacement

`eza` is a modern `ls` replacement written in Rust. It supports icons, git integration, color-coded file types, and tree output.

## Install

**Arch / CachyOS / Manjaro:**
```bash
sudo pacman -S --needed eza
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install -y eza
```

If the package is unavailable, install the binary from GitHub releases.

## Recommended zsh aliases

Add to `~/.zshrc` **after** `source $ZISH/oh-my-zsh.sh` (so they override any OMZ `ls` aliases):

```zsh
unalias ls la ll lt 2>/dev/null

alias ls='eza --icons=always --group-directories-first'
alias la='eza -a --icons=always --group-directories-first'
alias ll='eza -al --icons=always --group-directories-first'
alias lt='eza --tree --icons=always --level=2'
```

Use `--icons=always` rather than `--icons` alone. The plain `--icons` flag may fall back to no icons depending on environment/terminal detection.

## Common flags

| Flag | Meaning |
|---|---|
| `--icons=always` | Always show icons |
| `--group-directories-first` | Directories before files |
| `-a` / `--all` | Show hidden files |
| `-l` | Long listing |
| `-la` | Long + hidden |
| `--tree --level=N` | Tree output limited to N levels |
| `--git-ignore` | Hide files ignored by git |

## Verification

```bash
ls -la
```

Expected: file and folder icons rendered next to names.

## Pitfalls

- **Icons missing:** Terminal font is not a Nerd Font, or locale is `POSIX`/`C`. Fix both: install a Nerd Font and set `export LANG=en_US.UTF-8`.
- **Aliases not applied:** Oh My Zsh `lib/directories.zsh` may define its own `ls` aliases. Add `unalias ls la ll lt 2>/dev/null` before defining eza aliases.
- **Wrong icons:** Some icon sets differ between Nerd Font versions. If a glyph is wrong, update the font to the latest Nerd Fonts release.

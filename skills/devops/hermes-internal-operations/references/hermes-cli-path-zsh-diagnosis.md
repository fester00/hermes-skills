---
date: 2026-07-07
context: Hermes CLI stopped resolving in new zsh terminals; manual `export PATH="$HOME/.local/bin:$PATH"; hash -r` was required.
---

# Hermes CLI PATH resolution diagnosis (zsh)

## Symptom

The user reported that `hermes` used to launch with a plain `hermes` command, but now a new terminal only finds it after running:

```zsh
export PATH="$HOME/.local/bin:$PATH"
hash -r
hermes
```

## Root cause

`~/.local/bin/hermes` (symlink to `~/.hermes/hermes-agent/venv/bin/hermes`) was intact, the Python interpreter chain was intact, and `hermes --version` worked when called by absolute path. The actual problem was that new zsh instances did not always source `~/.profile`, so `~/.local/bin` was not added to PATH automatically.

Common reasons zsh skips `~/.profile`:
- New terminals open as non-login interactive shells.
- Some terminal emulators / remote sessions source only `~/.zshrc`.
- `~/.zprofile` is missing.

## Diagnostic commands

```zsh
echo $SHELL              # should be /usr/bin/zsh
echo $PATH               # check for $HOME/.local/bin
which hermes || echo "not in PATH"
ls -la ~/.local/bin/hermes
ls -la ~/.hermes/hermes-agent/venv/bin/hermes
file ~/.hermes/hermes-agent/venv/bin/python

# Compare login vs non-login shell
zsh -lc 'which hermes; echo $PATH'
zsh -c 'which hermes; echo $PATH'
```

## Permanent fix

Add an explicit guard to `~/.zshrc` **after** `source $ZSH/oh-my-zsh.sh`:

```zsh
if [[ -d "$HOME/.local/bin" ]] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    export PATH="$HOME/.local/bin:$PATH"
fi
```

Why after `source $ZSH/oh-my-zsh.sh`? OMZ itself can prepend to PATH (e.g. for completions, plugin shims). Adding the guard after OMZ ensures the final PATH is correct and avoids race conditions with OMZ initialization.

## One-off fix for the current terminal

```zsh
export PATH="$HOME/.local/bin:$PATH"
rehash
hermes --version
```

## Also check `~/.profile`

Keep the `~/.profile` block for login shells and bash compatibility:

```bash
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi
hash -r 2>/dev/null || true
```

But do **not** rely on `~/.profile` alone for zsh.

## Cleanup duplicate PATH entries

If the startup files all prepend the same directory, PATH can end up with duplicates such as:

```
/home/natan/.local/bin:/home/natan/bin:/home/natan/.cargo/bin:/home/natan/.local/bin:/home/natan/bin:/home/natan/.local/bin:...
```

Use the idempotent guard above to prevent new duplicates. To deduplicate the current session:

```zsh
export PATH=$(echo "$PATH" | tr ':' '\n' | awk '!seen[$0]++' | paste -sd: -)
```

## Verification after applying the fix

1. Save `~/.zshrc`.
2. Open a brand new terminal (or run `exec zsh -l`).
3. Run:
   ```zsh
   which hermes
   hermes --version
   echo $PATH | tr ':' '\n'
   ```
4. Confirm `hermes` resolves without any manual `export PATH`.

# Nerd Fonts for Terminal Icons

Reference for choosing and configuring a Nerd Font so that Oh My Posh, eza, and other icon-rendering tools display glyphs correctly.

## Why a Nerd Font is required

Tools like Oh My Posh and `eza --icons` use icon glyphs from the Nerd Fonts patch set. A standard programming font does not contain these glyphs, so icons render as empty boxes, question marks, or tofu (`?????`).

## Meslo Nerd Font variants

The Meslo family is the most common starting point. The suffix letters describe size/width; **Mono** means monospaced (required for terminal emulators).

| Variant | Meaning | Use when |
|---|---|---|
| **MesloLGS** | **L**arger glyph size, **G**reater width, **S**hort line height | You want the biggest, widest glyphs. Best for readability and large icons. |
| **MesloLGM** | Medium size/width | Balanced compromise between glyph size and terminal density. |
| **MesloLGL** | Larger line height, slightly more compact glyphs | You want more lines on screen and taller line spacing. |
| **MesloLGSDZ** | Same as LGS but with **D**otted **Z**ero (`0` has a dot inside) | You prefer dotted zero to distinguish it from `O`. |
| **MesloLGS Nerd Font Mono** | Monospaced version of LGS | Use in terminal emulators. |
| **MesloLGS Nerd Font Propo** | Proportional version | For documents/UI text, **not** for terminals. |

If icons feel too small, first increase the terminal font `size`; if they still feel cramped, switch from `LGM` to `LGS`.

## Alacritty font configuration

```toml
[font]
normal = { family = "MesloLGS Nerd Font Mono", style = "Regular" }
bold = { family = "MesloLGS Nerd Font Mono", style = "Bold" }
italic = { family = "MesloLGS Nerd Font Mono", style = "Italic" }
bold_italic = { family = "MesloLGS Nerd Font Mono", style = "Bold Italic" }
size = 11.0
```

Restart Alacritty after changing the font.

## Other good Nerd Fonts

- **JetBrainsMono Nerd Font** — very readable, coding-focused.
- **MesloLGS Nerd Font Mono** — default recommendation for compatibility.
- **CaskaydiaCove Nerd Font** — Cascadia Code base, good for Windows/Linux.

## Verification

After setting the font and locale:

```bash
eza --icons=always --group-directories-first
```

You should see folder icons (``) and file-type icons next to names, not boxes or question marks.

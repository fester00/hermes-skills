---
name: ascii-creative
description: |
  ASCII art generation: pyfiglet text banners, cowsay, boxes, image-to-ASCII,
  colored ASCII video conversion (MP4/GIF), and terminal-based visual creative tools.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ascii, art, text, video, creative, terminal]
    related_skills: [baoyu-content, creative-ideation]
---

# ASCII Creative

Generate text-based art and video from the terminal.

---

## 1. Static ASCII Art

### pyfiglet — Text Banners
```bash
pyfiglet "Hello World"         # Default font
pyfiglet -f slant "Hello"     # Specific font
pyfiglet -l                    # List fonts
```

### cowsay / cowthink
```bash
cowsay "Hello"
cowthink "Hmm..."
cowsay -f tux "Linux rules"
```

### boxes — Decorative borders
```bash
echo "Hello" | boxes -d diamond
```

### image-to-ASCII
```bash
# Using img2txt or ascii-image-converter
ascii-image-converter image.png --color
```

**See `references/ascii-art.md` for full font lists, color options, and programmatic generation.**

---

## 2. ASCII Video

Convert video or audio to colored ASCII art MP4/GIF.

### Requirements
```bash
pip install ascii-movie
# or use ffmpeg + image-to-ascii pipeline
```

### Usage
```bash
# Video to ASCII MP4
ascii-movie input.mp4 --output output.mp4 --cols 120

# GIF to ASCII GIF
ascii-movie input.gif --output output.gif --fps 10 --color
```

**See `references/ascii-video.md` for full parameter reference, custom character sets, and batch processing.**

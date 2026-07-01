# Wallpaper/Image Sources for Luxury Sites

## Russian Sites (Cyrillic / Local Content)

### wallpaperscraft.ru
- URL pattern: `https://wallpaperscraft.ru/catalog/nature`
- Image URLs: thumbnails `300x168` → original `1920x1080` by replacing in `src`
- Search: hover over image, right-click → copy image link, replace `300x168` with original resolution
- Download: `curl -O` or `wget` direct URLs
- Categories: nature, abstract, architecture, minimal, art

### Other sources
- `unsplash.com` — global, hotlink-friendly, `?w=1920&q=80` params
- `pexels.com` — similar, no hotlink restrictions
- `wallhaven.cc` — community curated, requires download

## Batch Download Script
```bash
#!/bin/bash
# Download wallpapers from a list of URLs
mkdir -p public/images
cd public/images
while read url; do
  curl -sL -O "$url"
done < urls.txt
```

## Image Processing
- Resize to consistent aspect ratio: `mogrify -resize 1920x1080^ -gravity center -extent 1920x1080 *.jpg`
- Compress for web: `jpegoptim --size=500k *.jpg`

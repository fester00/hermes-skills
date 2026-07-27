from PIL import Image, ImageDraw, ImageFont
import os


def create_product_placeholder(output_path: str, title: str, subtitle: str, size=(800, 600)):
    """Generate a dark, consistent product placeholder image."""
    img = Image.new("RGB", size, color="#141414")
    draw = ImageDraw.Draw(img)

    # Subtle radial glow
    for r in range(size[1] // 2, 0, -10):
        alpha = int(8 * (1 - r / (size[1] // 2)))
        color = (20 + alpha, 24 + alpha, 30 + alpha)
        draw.ellipse(
            [size[0] // 2 - r, size[1] // 2 - r, size[0] // 2 + r, size[1] // 2 + r],
            fill=color,
        )

    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except Exception:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Accent line
    line_width = 120
    draw.rectangle(
        [size[0] // 2 - line_width // 2, size[1] // 2 - 80, size[0] // 2 + line_width // 2, size[1] // 2 - 76],
        fill="#89AACC",
    )

    # Title
    bbox = draw.textbbox((0, 0), title, font=title_font)
    text_w = bbox[2] - bbox[0]
    x = (size[0] - text_w) // 2
    y = size[1] // 2 - 40
    draw.text((x, y), title, fill="#f0f0f0", font=title_font)

    # Subtitle
    bbox2 = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    text_w2 = bbox2[2] - bbox2[0]
    x2 = (size[0] - text_w2) // 2
    y2 = y + 70
    draw.text((x2, y2), subtitle, fill="#89AACC", font=subtitle_font)

    # Decorative border
    margin = 30
    draw.rectangle(
        [margin, margin, size[0] - margin, size[1] - margin],
        outline="#2a2a2a",
        width=3,
    )

    img.save(output_path, "WEBP", quality=90)


if __name__ == "__main__":
    out_dir = "public/images"
    os.makedirs(out_dir, exist_ok=True)
    create_product_placeholder(
        os.path.join(out_dir, "unicast-6v.webp"),
        "ЮниКаст 6В",
        "Жидкий полиуретан 70 Шор D",
    )
    create_product_placeholder(
        os.path.join(out_dir, "unisil-9500.webp"),
        "Юнисил 9500",
        "Платиновый силикон 2 Шор А",
    )
    print("Placeholders generated")

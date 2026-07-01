# PDF Design Mockup → React Native Implementation Workflow

Used when the user provides PDF mockups for mobile app screens and wants pixel-perfect implementation.

## Workflow

### 1. Locate PDF files
Search the project directory or nearby paths for `.pdf` files:
```bash
find /path/to/project -maxdepth 3 -type f \( -iname "*.pdf" -o -iname "*.png" \)
```

PDFs may be in:
- Project root (`/home/user/workspace/*.pdf`)
- A `design/` or `docs/` subdirectory
- Already converted to PNG thumbnails in a `pdf_thumbs/` folder

### 2. Convert PDF to PNG (if needed)
If only PDFs exist, convert pages to PNG using ImageMagick or Python:
```bash
# ImageMagick (requires poppler/ghostscript)
pdftoppm -png input.pdf output_prefix

# Or with Python
python3 -m pip install pdf2image
python3 -c "from pdf2image import convert_from_path; imgs = convert_from_path('design.pdf', dpi=200); [img.save(f'page_{i}.png') for i, img in enumerate(imgs)]"
```

### 3. Analyze with vision
Use `vision_analyze` on the resulting PNG files to extract design details:

```
vision_analyze(image_url="/path/to/page_1.png", question="""
Describe the screen structure in detail:
- Blocks from top to bottom
- Font sizes and weights
- Colors (hex approximations)
- Layout (flex direction, spacing, borders)
- Interactive elements (buttons, inputs, toggles)
- Icons and their approximate sizes
""")
```

Run this for **every screen** PDF page. Each page = one screen in the app.

### 4. Extract color palette
The user's PDF may contain a dedicated color palette page (e.g., "цвета"). If so, analyze it separately for exact hex values:

```
vision_analyze(image_url="/path/to/colors.png", question="
List every color swatch shown with its hex approximation and label/name.
")
```

### 5. Map to theme constants
Create or update `constants/theme.ts` with the extracted palette:

```ts
export const Colors = {
  light: {
    background: '#ffffff',
    text: '#221f21',
    subtext: '#706f6f',
    subBackground: '#ededed',
    boxOne: ['#9a191f', '#e30613'] as const,      // red gradient
    boxTwo: ['#95c11f', '#dedc00'] as const,      // orange-green gradient
    boxVallet: ['#dedc00', '#95c11f'] as const,   // green gradient (wallet)
    accentGreen: '#95c11f',
    tintBackground: '#9a191f',
  },
  dark: {
    // ... inverted or adapted
  },
} as const;
```

### 6. Implement screen by screen
For each screen, create the component structure matching the PDF:

- **Header**: Logo + greeting text (from vision description)
- **Cards**: Rounded corners (borderRadius: 20), gradient headers
- **Lists**: FlatList or View + .map() depending on nesting rules
- **Forms**: Controlled inputs with `BInput` pattern (see SKILL.md section 13)
- **Bottom nav**: Tab bar matching colors and icons from mockup

### 7. Pitfalls

**Nested ScrollView warning**: Never put `FlatList` inside `ScrollView`. Use `View` + `.map()` for short lists (under ~30 items). For long lists, make `FlatList` the root scroll container with `ListHeaderComponent` for static content above.

**Font sizes from vision are estimates**: The LLM vision gives approximate point sizes. Use them as starting values and adjust by ±2px during testing. Prioritize relative sizing (`flex`, `flexGrow`) over absolute pixel values.

**Icon names**: Vision may describe icons generically ("bell", "person", "list"). Map to actual icon library names (MaterialIcons, FontAwesome, SimpleLineIcons). When uncertain, use `@expo/vector-icons` searchable names.

**Text overflow**: PDF mockups show ideal content lengths. Real data may be longer. Always add `numberOfLines={2}` or `ellipsizeMode="tail"` to text elements, and test with long names/addresses.

**Platform differences**: iOS and Android render borderRadius, shadows, and fonts slightly differently. Test on both. Use `Platform.select()` for platform-specific adjustments only when necessary.

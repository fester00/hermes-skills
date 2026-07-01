# Извлечение цветов из PDF макетов дизайна

Техника преобразования PDF-макетов мобильных приложений в PNG + анализ палитры vision моделью.

## Когда использовать

- У пользователя есть PDF-макеты от дизайнера (Figma export, Adobe PDF)
- Нужно извлечь точные hex-коды, градиенты, цвета для темы приложения
- Нет доступа к исходникам Figma/Sketch

## Шаги

### 1. PDF → PNG (pymupdf / fitz)

```bash
pip3 install pymupdf
python3 -c "
import fitz, os, sys
os.makedirs('pdf_thumbs', exist_ok=True)
for f in sys.argv[1:]:
    doc = fitz.open(f)
    pix = doc[0].get_pixmap(dpi=200)
    out = f'pdf_thumbs/{os.path.basename(f).replace(\".pdf\", \".png\")}'
    pix.save(out)
    print(f'Saved {out}')
    doc.close()
" color_palette.pdf main_screen.pdf profile_screen.pdf
```

### 2. PNG → Color extraction (vision_analyze)

```python
# Анализ палитры
vision_analyze('/path/to/pdf_thumbs/color_palette.png',
    question='Извлеки ВСЕ цвета. hex коды, RGB, названия.')

# Анализ отдельных экранов
for screen in ['main_screen', 'profile', 'services', 'finances']:
    vision_analyze(f'pdf_thumbs/{screen}.png',
        question='Опиши дизайн экрана: элементы UI, цвета, расположение блоков.')
```

### 3. Маппинг в theme.ts

```ts
// Извлечённые из PDF:
const brandRed      = '#e30613';   // градиент начало
const brandRedDark  = '#9a191f';   // градиент конец
const accentOrange  = '#f39200';   // тарифы
const accentOrangeLight = '#f9b233';
const walletYellow  = '#dedc00';   // кошелёк начало
const accentGreen   = '#95c11f';   // кошелёк конец, акцент
const cardBgLight   = '#ededed';   // фон карточек
const textSecondary = '#706f6f';   // вторичный текст
const activeTabBg   = '#a3191c';   // активный таб навбара
```

### Практические значения из реальных проектов

| Типовой компонент | Пример hex | Источник |
|---|---|---|
| Брендовый красный градиент | `#e30613` → `#9a191f` | ЛигаЛинк, PDF палитра |
| Оранжевый тариф | `#f39200` → `#f9b233` | ЛигаЛинк |
| Зелёный кошелёк | `#dedc00` → `#95c11f` | ЛигаЛинк |
| Фон карточек | `#ededed` | ЛигаЛинк |
| Вторичный текст | `#706f6f` | ЛигаЛинк |
| Активный таб | `#a3191c` | ЛигаЛинк |

## Подводные камни

- **vision_analyze не принимает PDF напрямую**. Нужна PNG конвертация.
- **pdftoppm может отсутствовать**. Лучше использовать pymupdf (cross-platform).
- **DPI**: 150-200 достаточно для цветов, 300 если нужны мелкие детали.
- **Цвета в тёмной теме**: PDF может содержать отдельный макет тёмной темы — анализировать оба.
- **Градиенты**: vision модель может писать «red gradient» — просить явно hex для начала и конца.

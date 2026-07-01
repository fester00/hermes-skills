# Конвертация изображений pentajunior-v2 в WebP

Контекст: проект pentajunior-v2 на Next.js 16 использует `next/image` с `formats: ['image/avif', 'image/webp']`. Исходные PNG/JPG в `public/images/` часто весят по 1–2 МБ каждый, что замедляет первую загрузку даже при серверной оптимизации Next.js.

## Цель

- Уменьшить общий вес изображений в ~10 раз.
- Сохранить качество (WebP q=85, размер ≤1600 px по большей стороне).
- Обновить пути в БД (`products.image`, категории/подкатегории), чтобы новые файлы использовались.

## Пошаговый рецепт

1. **Бэкап**:
   ```bash
   cp -r /home/natan/pentajunior-v2/public/images /home/natan/pentajunior-v2/public/images_backup_$(date +%Y%m%d_%H%M%S)
   cp /home/natan/pentajunior-v2/pentajunior.db /home/natan/pentajunior-v2/pentajunior.db.images-backup-$(date +%Y%m%d-%H%M%S)
   ```

2. **Конвертация** (Python + Pillow):
   ```python
   import os, glob
   from PIL import Image

   base = "/home/natan/pentajunior-v2/public"
   for path in glob.glob(base + "/images/**/*", recursive=True):
       if not os.path.isfile(path): continue
       ext = os.path.splitext(path)[1].lower()
       if ext not in ['.png', '.jpg', '.jpeg']: continue
       img = Image.open(path)
       if img.mode in ('RGBA', 'P'):
           img = img.convert('RGB')
       w, h = img.size
       if w > 1600 or h > 1600:
           ratio = min(1600 / w, 1600 / h)
           img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
       new_path = os.path.splitext(path)[0] + '.webp'
       img.save(new_path, 'WEBP', quality=85, method=6)
       os.remove(path)
   ```

3. **Обновление путей в БД**:
   ```python
   import sqlite3, re, shutil
   DB = "/home/natan/pentajunior-v2/pentajunior.db"
   conn = sqlite3.connect(DB)
   conn.row_factory = sqlite3.Row
   cur = conn.cursor()
   for row in cur.execute("SELECT id, image FROM products WHERE image IS NOT NULL").fetchall():
       new = re.sub(r'\.(png|jpg|jpeg)$', '.webp', row['image'], flags=re.IGNORECASE)
       if new != row['image']:
           cur.execute("UPDATE products SET image = ? WHERE id = ?", (new, row['id']))
   conn.commit()
   ```

4. **Проверка**:
   - Убедиться, что все пути из БД существуют на диске.
   - Собрать проект: `tsc --noEmit && rm -rf .next && npm run build`.
   - Проверить отображение изображений на карточках товаров и категорий.

5. **Коммит**:
   ```bash
   cd /home/natan/pentajunior-v2
   git add pentajunior.db public/images/
   git commit -m "Convert product/category images to WebP, update DB image paths"
   git push
   ```

## Подводные камни

- `next/image` в dev-режиме не кеширует оптимизацию так же агрессивно, как production. Для реальной проверки скорости запускать `npm run build && npx next start -p 3001`.
- SVG-файлы (например, `/images/fav.svg`) не нужно конвертировать.
- После замены расширений старые ссылки из `pentajunior.db` на `.png`/`.jpg` станут битыми; обновление БД обязательно.
- Если в проекте есть жёстко заданные пути к изображениям в коде (не из БД), их тоже нужно поправить вручную.

## Результат типичного прогона

- До: ~41 MB PNG/JPG.
- После: ~3 MB WebP.
- Экономия: ~93%.

## Adding category images to `/production`

When the `/production` catalog page shows categories as cards (`ProductsCard`), each card reads `category.image`. If a category has no image, the card renders a placeholder. To fill missing category images:

1. Check existing category images and confirm the file exists on disk (old `.png` references may point to converted `.webp` files).
2. For categories without `image`, pick the first product image in that category that exists on disk.
3. For categories where no product image is available, reuse a visually related existing image (e.g. a generic aerosol can for shoe-care products).
4. Update `categories.image` in `pentajunior.db` for all affected rows.
5. Run the build gate and commit only `pentajunior.db`.

Example mapping from 2026-06-23:
- `silikon-dlya-zalivki-form` → `/images/RTV/9110.webp`
- `production-release` → `/images/categorys/Smazki_Group.webp`
- `silicon-oils` → `/images/pms/PMS.webp`
- `visokotemperaturnie-smazki` → `/images/высокотемпературные смазки/Пента-200.webp`
- `germetics` → `/images/sealants/1100.webp`
- `antiprigarnii-material-tsm1` → `/images/TSM/тсм-1.webp`
- `izdelija-iz-silikonovyh-rezin` → `/images/krems/krem_slilicon.webp`
- `obrabotka-poverhnosti-propitki` → `/images/гидрофобизаторы/Пента-811.webp`
- `production-hand-care` → `/images/krems/krem_slilicon.webp`
- `electrosealant` → `/images/cremnii-germetics/Пентэласт-711.webp`
- `shoes-protection` → `/images/smazki/si_m_smazka.webp`
- `smazochno-ohlazhdayushhie-zhidkosti` → `/images/сож/сож.webp`
- `ochistitel-press-form` → `/images/smazki/Пента-150.webp`

Always verify each new path exists in `public/images/` before updating the database.

# Ozon Product Extraction Patterns

## Рабочие селекторы (проверено 2026-05-09)

### Получение списка товаров

```javascript
// Способ 1: Через карточки товаров
const cards = document.querySelectorAll(
  '[data-widget="searchResultsV2"] .ts, ' +
  '[data-widget="catalogResults"] .ts, ' +
  '.tile-root'
);

// Способ 2: Через ссылки (надёжнее когда селекторы карточек меняются)
const links = document.querySelectorAll('a[href*="/product/"]');
const seen = new Set();
links.forEach(link => {
  const href = link.href;
  if (seen.has(href)) return;
  seen.add(href);
  
  // Найти имя в родительской карточке (вверх по DOM)
  let nameEl = null;
  let current = link;
  for (let i = 0; i < 5; i++) {
    current = current.parentElement;
    if (!current) break;
    const spans = current.querySelectorAll('span');
    for (const s of spans) {
      const text = s.textContent.trim();
      if (text.length > 20 && (text.includes('TB') || text.includes('ТБ'))) {
        nameEl = s;
        break;
      }
    }
    if (nameEl) break;
  }
  
  if (nameEl) {
    results.push({
      name: nameEl.textContent.trim().substring(0, 100),
      href: href
    });
  }
});
```

### Извлечение цен

```javascript
// Цена (текущая)
const priceEl = card.querySelector('[class*="Price"], [class*="price"]');

// Старая цена (зачёркнутая)
const oldPriceEl = card.querySelector('[class*="oldPrice"], s, [class*="del"]');

// Скидка (бейдж)
const discountEl = card.querySelector('[class*="discount"], [class*="Discount"]');

// Рейтинг
const ratingEl = card.querySelector('[class*="rating"], [class*="Rating"]');

// Количество отзывов
const reviewsEl = card.querySelector('[class*="reviews"], [class*="Review"]');

// Наличие
const stockEl = card.querySelector('[class*="stock"], [class*="available"]');
```

### Извлечение с именем продавца

```javascript
const sellerEl = card.querySelector('[class*="seller"], [class*="brand"]');
const seller = sellerEl ? sellerEl.textContent.trim() : '';
```

## Пример полного извлечения

```javascript
(function() {
  const results = [];
  const cards = document.querySelectorAll(
    '[data-widget="searchResultsV2"] .ts, .tile-root'
  );
  
  cards.forEach((card, i) => {
    if (i > 15) return;
    
    const nameEl = card.querySelector('[class*="tsBody"], span');
    const priceEl = card.querySelector('[class*="Price"]');
    const oldPriceEl = card.querySelector('s, [class*="oldPrice"]');
    const linkEl = card.querySelector('a[href*="/product/"]');
    
    if (nameEl && linkEl) {
      results.push({
        name: nameEl.textContent.trim().substring(0, 120),
        price: priceEl ? priceEl.textContent.trim() : 'N/A',
        oldPrice: oldPriceEl ? oldPriceEl.textContent.trim() : '',
        href: linkEl.href
      });
    }
  });
  
  return JSON.stringify(results.slice(0, 10));
})()
```

## Питфолы

1. **Селекторы Ozon меняются часто** — всегда иметь fallback через `a[href*="/product/"]`
2. **Имена продуктов могут быть пустыми** — проверять `textContent.trim().length > 10`
3. **Дублирующиеся ссылки** — использовать `Set` для фильтрации
4. **Мобильная версия** — без `Emulation.setDeviceMetricsOverride` Ozon покажет мобильный layout

## Рабочие ссылки (шаблоны)

```
Ozon: https://www.ozon.ru/search/?text=QUERY&from_global=true
Yandex Market: https://market.yandex.ru/search?text=QUERY
Citilink: https://www.citilink.ru/search/?text=QUERY&available=1&order=price:asc
DNS: https://www.dns-shop.ru/search/?q=QUERY  (только прямые ссылки, 403 в браузере)
```

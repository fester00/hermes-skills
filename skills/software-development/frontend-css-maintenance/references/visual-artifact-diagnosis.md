# Диагностика визуальных артефактов, похожих на битый CSS

Сессионный рецепт из silicone-landing (июль 2026). Пользователь прислал скриншот, на котором подложки под иконками контактов выглядели «битыми» — вокруг иконок были странные вертикальные полосы и искажённые фигуры.

## Что проверять в первую очередь

1. **Computed styles обёртки иконки**
   - `width`, `height`, `border-radius`, `background`, `border`, `box-shadow`, `filter`, `transform`
   - псевдоэлементы `::before` / `::after`
   - Цель: убедиться, что обёртка действительно круглая/квадратная и фон однородный.

2. **Computed styles самой иконки (SVG)**
   - `width`, `height`, `transform`, `overflow` родителя
   - Цель: понять, не выходит ли форма SVG за границы обёртки. Иконки Lucide (`MapPin`, `Phone`) имеют выступы, которые обрезаются в маленьком круглом контейнере 44×44 px и создают визуальный шум.

3. **Фон секции**
   - Если позади иконок видео-фон или сложный градиент, артефакты могут быть не в иконках, а в фоне.
   - Временно скрыть видео/фон и переснять скриншот — быстрый способ отделить фон от иконки.

## Типичные причины

| Симптом | Причина | Решение |
|---|---|---|
| Вертикальные полосы вокруг круглой иконки | Иконка SVG выходит за края `border-radius: 50%` | Увеличить обёртку или заменить круг на squircle (`rounded-2xl`) |
| Фон подложки неоднородный / «цветной» | Конфликт классов или фоновый видео/градиент | Проверить computed `background`; изолировать секцию |
| Псевдоэлементы торчат из-под иконки | `::before`/`::after` у `.group` или обёртки | Проверить `content` псевдоэлементов |
| После hover появляются артефакты | Transition/scale иконки без `overflow-hidden` | Добавить `overflow-hidden` на обёртку |

## Быстрый сценарий Playwright

```ts
const data = await page.evaluate(() => {
  const wrap = document.querySelector('#contact a.contact-card svg').parentElement;
  const s = window.getComputedStyle(wrap);
  return {
    width: s.width, height: s.height,
    borderRadius: s.borderRadius,
    background: s.background,
    border: s.border,
    before: window.getComputedStyle(wrap, '::before').content,
    after: window.getComputedStyle(wrap, '::after').content,
  };
});
```

## Решение для иконок Lucide в контактах

- Обёртка: `52×52 px`, `border-radius: 1rem` (squircle), `overflow: hidden`
- Иконка: `20 px` вместо `22 px`
- Hover: лёгкий подъём обёртки и подсветка бордера

Это даёт визуальный воздух и убирает обрезку выступающих частей SVG.

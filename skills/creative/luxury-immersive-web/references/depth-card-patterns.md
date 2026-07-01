# Depth Card Patterns — Luxury Immersive Web

## Bottom Overlay Reveal (Products / Showcase)

Info (title, price, description) скрыта в нижней части карточки и выезжает при hover.

```tsx
<div className="absolute bottom-0 left-0 right-0 p-6 translate-y-4 group-hover:translate-y-0 transition-transform duration-500">
  <div className="h-[1px] w-12 bg-vidvis-gold mb-4 group-hover:w-full transition-all duration-700" />
  {/* opacity-0 → group-hover:opacity-100 с delay для stagger-акцента */}
  <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-500 delay-100">{price}</div>
  <h3 className="text-white">{title}</h3>
  <p className="opacity-0 group-hover:opacity-100 transition-opacity duration-500 delay-200">{desc}</p>
</div>
```

Поверх изображения всегда держать затемнение `bg-black/40`, которое осветляется до `bg-black/10` на hover.

## Vignette Overlay

Кинематографичный vignette на карточках и фонах:

```css
bg-[radial-gradient(ellipse_at_center,transparent_0%,rgba(0,0,0,0.4)_100%)]
```

pointer-events-none. Работает совместно с любым `<Image fill />`.

## Index Numbers for Depth

Большие затухшие числа в углу элемента создают визуальную глубину:

```tsx
<div className="absolute top-4 right-4 font-playfair text-6xl text-white/5 group-hover:text-white/10 select-none">
  {String(i + 1).padStart(2, "0")}
</div>
```

Используется в Products, Technologies, ArtGallery.

## Radial Gradient Section Background

Лёгкий depth-фон между секциями, не требует изображений:

```tsx
<div className="absolute inset-0 opacity-10 pointer-events-none">
  <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-vidvis-gold via-transparent to-transparent" />
</div>
```

## Technologies Showcase Grid

Grid карточек с tech stack. Каждая карточка:
- `preserve-3d` + `perspective: 1200px` на контейнере
- GSAP 3D tilt hover (`rotateY: x*14`, `rotateX: -y*14`)
- Elastic return на `mouseleave`
- Subtle parallax float через `scrub: 1.5` (чётные вверх, нечётные вниз)
- Gold accent line раскрывается по ширине на hover

## CSS Preset

```css
.perspective-1200 { perspective: 1200px; }
.preserve-3d { transform-style: preserve-3d; }
```

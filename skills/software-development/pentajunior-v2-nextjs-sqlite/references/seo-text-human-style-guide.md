# Стиль SEO-текстов для pentajunior-v2

Контекст: пользователь ценит естественный, полезный, «человеческий» стиль SEO-текстов. Избегать AI-слоупа и пустых маркетинговых штампов.

## Чего избегать

- **Undue significance:** "stands as", "serves as", "a testament to", "pivotal moment", "vital role", "enduring legacy".
- **Promotional adjectives:** "vibrant", "rich", "stunning", "breathtaking", "groundbreaking", "seamless".
- **AI filler words:** "additionally", "delve", "foster", "garner", "highlight", "intricate", "pivotal", "showcase", "tapestry", "underscore", "valuable".
- **Vague attributions:** "Industry observers", "Experts argue", "Some sources say".
- **Filler phrases:** "In order to", "Due to the fact that", "At this point in time", "It is important to note that".
- **Signposting:** "Let's dive in", "Here's what you need to know", "Let's explore".
- **Rule of three:** "innovation, inspiration, and insights".
- **Generic conclusions:** "The future looks bright", "Exciting times lie ahead".
- **Title case in headings:** писать "Как выбрать силикон" вместо "Как Выбрать Силикон".

## Что использовать

- **Конкретные факты:** вязкость, температура, пропорции смешивания, срок службы.
- **Практические применения:** для чего используется, на каких материалах, в каких условиях.
- **Прямые сравнения:** "платиновый vs оловянный", "для мягких vs твёрдых форм".
- **Предупреждения:** чувствителен к ингибиторам, не подходит для металлов, требует температуры выше +16 °C.
- **Призывы к действию:** "Смотрите ...", "Напишите менеджеру", "Оставьте заявку".

## Пример: до и после

**Before (AI-sounding):**
> Двухкомпонентный жидкий силикон для отливки форм — это эластичный материал, который играет ключевую роль в современном производстве, обеспечивая бесшовное создание форм и подчёркивая важность качественных материалов.

**After (human):**
> Двухкомпонентный жидкий силикон для отливки форм отверждается при комнатной температуре. При смешивании базы и катализатора запускается реакция полимеризации, и за 4–24 часа жидкая масса превращается в прочную, гибкую резину. Готовая форма точно копирует рельеф мастер-модели и выдерживает сотни циклов заливки.

## Структура SEO-текста

1. Вводный абзац — что это, как работает, зачем нужно.
2. 2–4 карточки с иконками Bootstrap:
   - каждая карточка — подкатегория или аспект применения;
   - заголовок карточки — ссылка на подкатегорию;
   - внутри — 1–2 ссылки на ключевые товары.
3. Завершающий абзац — практический призыв или перекрёстная ссылка.

## Шаблон карточки

```html
<div class="row g-4 my-1">
  <div class="col-md-6">
    <div class="h-100 p-4 rounded-3 bg-body-tertiary">
      <h2 class="h6 fw-semibold mb-2">
        <i class="bi bi-droplet-half me-2 text-primary"></i>
        <a href="/production/<cat>/<sub>" class="text-decoration-none">Название подкатегории</a>
      </h2>
      <p class="mb-0 small text-body-secondary">
        Конкретное описание. Популярные позиции: 
        <a href="/production/<cat>/<sub>/<product1>">Товар 1</a>, 
        <a href="/production/<cat>/<sub>/<product2>">Товар 2</a>.
      </p>
    </div>
  </div>
</div>
```

## Проверка перед сохранением

- Прочитать вслух — звучит естественно?
- Нет ли AI-штампов из списка выше?
- Все ли ссылки ведут на реальные страницы?
- Заголовки идут H1 → H2 → H2, без пропусков?

## Примеры хороших SEO-текстов из практики

См. `references/seo-silikon-dlya-zalivki-form-2026-06-22.md` и соседние `seo-*-2026-06-22.md` — там записаны одобренные пользователем черновики для каждой категории. Использовать как образец тона, структуры и плотности внутренних ссылок.

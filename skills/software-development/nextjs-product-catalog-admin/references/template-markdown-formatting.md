# Markdown-разметка в шаблонных текстах продукта

## Когда использовать

Нужно дать контент-менеджеру возможность выделять слова или фразы жирным в шаблонных текстовых полях (`intro`, `body`, `composition`, `application`, `usage` и т.д.) без WYSIWYG-редактора, без хранения HTML в базе и без `dangerouslySetInnerHTML`.

## Подход

- В админке текст оборачивается в `**жирный текст**`.
- В шаблоне продукте функция `renderMarkdownText()` превращает `**...**` в React-элемент `<strong>`.
- Переводы строк превращаются в `<br />`.
- Никакого парсинга произвольного HTML.

## Файл-утилита `src/lib/markdown.tsx`

```tsx
import { Fragment, ReactNode } from 'react';

export function renderMarkdownText(text: string | undefined | null): ReactNode {
  if (text === undefined || text === null) return null;
  const str = String(text);
  if (str === '') return null;

  const lines = str.split('\n');
  const nodes: ReactNode[] = [];

  lines.forEach((line, lineIndex) => {
    if (lineIndex > 0) {
      nodes.push(<br key={`br-${lineIndex}`} />);
    }

    const parts: ReactNode[] = [];
    let remaining = line;
    let partIndex = 0;

    while (remaining.length > 0) {
      const open = remaining.indexOf('**');
      if (open === -1) {
        parts.push(<span key={`plain-${lineIndex}-${partIndex++}`}>{remaining}</span>);
        break;
      }

      const afterOpen = remaining.slice(open + 2);
      const close = afterOpen.indexOf('**');

      if (close === -1) {
        parts.push(<span key={`plain-${lineIndex}-${partIndex++}`}>{remaining}</span>);
        break;
      }

      if (open > 0) {
        parts.push(
          <span key={`plain-${lineIndex}-${partIndex++}`}>{remaining.slice(0, open)}</span>
        );
      }

      const boldContent = remaining.slice(open + 2, open + 2 + close);
      parts.push(
        <strong key={`bold-${lineIndex}-${partIndex++}`}>
          {boldContent === '' ? '\u00A0' : boldContent}
        </strong>
      );

      remaining = remaining.slice(open + 2 + close + 2);
    }

    nodes.push(<Fragment key={`line-${lineIndex}`}>{parts}</Fragment>);
  });

  return <>{nodes}</>;
}
```

## Использование в шаблоне

```tsx
import { renderMarkdownText } from '@/lib/markdown';

<p className="news-card-desc mb-3">
  {renderMarkdownText(templateData.intro)}
</p>
```

## Кнопка "B" в админке

В `TemplateDataEditor.tsx` добавляется тулбар над каждым `textarea`:

```tsx
const textareaRefs = useRef<Record<string, HTMLTextAreaElement | null>>({});

const supportsFormatting = (field: TemplateField): boolean =>
  field.type === 'textarea' || field.type === 'lines';

const toggleBold = useCallback((key: string) => {
  const textarea = textareaRefs.current[key];
  if (!textarea) return;

  const start = textarea.selectionStart ?? 0;
  const end = textarea.selectionEnd ?? 0;
  if (start === end) return;

  const raw = getValue(key);
  const before = raw.slice(0, start);
  const selected = raw.slice(start, end);
  const after = raw.slice(end);
  const BOLD_MARKER = '**';

  const isWrapped =
    raw.slice(start - BOLD_MARKER.length, start) === BOLD_MARKER &&
    raw.slice(end, end + BOLD_MARKER.length) === BOLD_MARKER;

  let nextValue: string;
  let nextStart: number;
  let nextEnd: number;

  if (isWrapped) {
    nextValue = before.slice(0, start - BOLD_MARKER.length) + selected + after.slice(BOLD_MARKER.length);
    nextStart = start - BOLD_MARKER.length;
    nextEnd = nextStart + selected.length;
  } else {
    nextValue = before + BOLD_MARKER + selected + BOLD_MARKER + after;
    nextStart = start + BOLD_MARKER.length;
    nextEnd = nextStart + selected.length;
  }

  const field = fields.find((f) => f.key === key);
  setValue(key, nextValue, field?.type || 'textarea');

  requestAnimationFrame(() => {
    textarea.focus();
    textarea.setSelectionRange(nextStart, nextEnd);
  });
}, [fields, getValue, setValue]);
```

## Почему не WYSIWYG

- Не тянет тяжёлые зависимости.
- Не даёт админу сломать вёрстку произвольным HTML.
- SEO получает тот же результат — `<strong>` в финальном HTML.
- Контент-менеджеру достаточно кнопки **B**; продвинутые пользователи могут писать `**...**` вручную.

## Проверка

- `tsc --noEmit` без ошибок.
- `next build` успешен.
- В админке выделить текст → нажать **B** → сохранить → на сайте фраза отображается жирным.

import { useEffect, useRef, useCallback, memo } from 'react';

interface FieldDef {
  key: string;
  label: string;
  type: 'text' | 'textarea' | 'lines' | 'select';
  rows?: number;
  placeholder?: string;
  options?: { value: string; label: string }[];
}

interface FieldRowProps {
  field: FieldDef;
  initialValue: string;
  onCommit: (raw: string) => void;
}

/**
 * Uncontrolled field row used in long admin modal forms.
 *
 * Why uncontrolled:
 * - Every keystroke does NOT flow through parent React state.
 * - Parent re-renders (e.g. updating other fields) do not touch this DOM node.
 * - Scroll position and focus stay where the user expects.
 *
 * Commits:
 * - debounced 300 ms while typing (onInput)
 * - immediately on blur (onBlur)
 */
export const FieldRow = memo(function FieldRow({ field, initialValue, onCommit }: FieldRowProps) {
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sync DOM when the surrounding product changes, but never while the user is typing.
  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    if (el.value !== initialValue) {
      el.value = initialValue;
    }
  }, [initialValue]);

  const readValue = useCallback(() => inputRef.current?.value ?? '', []);

  const commitNow = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    onCommit(readValue());
  }, [onCommit, readValue]);

  const scheduleCommit = useCallback(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      onCommit(readValue());
    }, 300);
  }, [onCommit, readValue]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const supportsFormatting = field.type === 'textarea' || field.type === 'lines';

  return (
    <div className="mb-3 template-data-field" key={field.key}>
      <label className="form-label small fw-semibold">{field.label}</label>
      {field.type === 'text' ? (
        <input
          ref={inputRef as React.Ref<HTMLInputElement>}
          className="form-control form-control-sm"
          defaultValue={initialValue}
          onInput={scheduleCommit}
          onBlur={commitNow}
          placeholder={field.placeholder || ''}
        />
      ) : field.type === 'select' ? (
        <select
          ref={inputRef as React.Ref<HTMLSelectElement>}
          className="form-select form-select-sm"
          defaultValue={initialValue}
          onChange={scheduleCommit}
          onBlur={commitNow}
        >
          <option value="">— выберите —</option>
          {field.options?.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      ) : (
        <>
          {supportsFormatting && (
            <div className="d-flex align-items-center gap-2 mb-1">
              <button type="button" className="btn btn-outline-secondary btn-sm py-0 px-2">
                <strong>B</strong>
              </button>
              <small className="text-muted">Поддерживается <code>**жирный текст**</code></small>
            </div>
          )}
          <textarea
            ref={inputRef as React.Ref<HTMLTextAreaElement>}
            className={`form-control form-control-sm ${field.type === 'lines' ? 'font-monospace' : ''}`}
            rows={field.rows || 2}
            defaultValue={initialValue}
            onInput={scheduleCommit}
            onBlur={commitNow}
            placeholder={field.placeholder || ''}
          />
        </>
      )}
      {field.type === 'lines' && (
        <small className="form-text text-muted">Каждая строка — отдельный пункт</small>
      )}
    </div>
  );
});

# Установка Яндекс.Метрики в pentajunior-v2 (Next.js 16)

> Проверено на pentajunior-v2, Next.js 16.2.6, Node.js 24.13.1.

## Когда использовать

- Пользователь предоставил код счётчика Яндекс.Метрики.
- Нужно добавить счётчик на все страницы сайта.
- Включены расширенные опции: webvisor, clickmap, trackLinks, accurateTrackBounce.
- Подготовлен `ecommerce: "dataLayer"` для будущей передачи e-commerce событий.

## Шаги

### 1. Открыть `src/app/layout.tsx`

```tsx
import Script from "next/script";
```

### 2. Добавить `<Script>` и `<noscript>` внутрь `<body>` после `{children}`

```tsx
      <body className={inter.variable}>
        <BootstrapClient />
        <JsonData data={globalJsonLd} />
        <ClientLayout>
          {children}
        </ClientLayout>
        <Script id="yandex-metrika" strategy="afterInteractive">
          {`
            (function(m,e,t,r,i,k,a){
              m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
              m[i].l=1*new Date();
              for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
              k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
            })(window, document, 'script', 'https://mc.yandex.ru/metrika/tag.js?id=REPLACE_WITH_COUNTER_ID', 'ym');

            ym(REPLACE_WITH_COUNTER_ID, 'init', {
              ssr:true,
              webvisor:true,
              clickmap:true,
              ecommerce:"dataLayer",
              referrer: document.referrer,
              url: location.href,
              accurateTrackBounce:true,
              trackLinks:true
            });
          `}
        </Script>
        <noscript>
          <div>
            <img src="https://mc.yandex.ru/watch/REPLACE_WITH_COUNTER_ID" style={{ position: 'absolute', left: '-9999px' }} alt="" />
          </div>
        </noscript>
      </body>
```

### 3. Build gate

```bash
cd /home/natan/pentajunior-v2
npx tsc --noEmit
rm -rf .next tsconfig.tsbuildinfo
npm run build
```

### 4. Проверка на проде

```bash
curl -s https://pentajunior.ru/ | grep -oE 'mc\.yandex\.ru|ym\(COUNTER_ID|dataLayer'
```

Должны присутствовать: `mc.yandex.ru`, `ym(COUNTER_ID`, `dataLayer`.

## Подводные камни

- **Не использовать `'use client'` в `layout.tsx`** — `next/script` с `strategy="afterInteractive"` работает в server-компоненте.
- **Строковый интерполяция внутри `{`\`...\``}`** — экранировать обратные кавычки и `${}` не нужно, если оборачивать в шаблонные строки Next.js Script.
- **noscript `<img>`** — в Next.js можно использовать inline `style={{ position: 'absolute', left: '-9999px' }}`.
- **ecommerce** — без передачи событий в `dataLayer` не даст отчётов по электронной коммерции. Включать после настройки Yandex Commerce Protocol / событий «добавить в корзину».
- **ID счётчика** — заменить `REPLACE_WITH_COUNTER_ID` на реальный ID, например `106965328`.

## Deploy

После push сайта счётчик активируется при reload. PM2 reload:

```bash
pm2 reload pentajunior-v2 --update-env
```

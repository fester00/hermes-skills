# Site constants centralization pattern — pentajunior-v2

Session context: July 2026 refactor replacing hardcoded domain names, emails, phone numbers, and the company address across public pages.

## Problem

Contact and legal pages contained repeated literals:
- `penta-junior.ru`, `pentajunior.ru`
- `penta@penta-junior.ru`
- `+7 (495) 644-46-16`, `+7 (495) 730-58-51`
- `ООО «Пента Юниор»`
- office address in `policy/page.tsx`, `Footer.tsx`, etc.

This makes updates error-prone and produces inconsistent mailto/tel links.

## Solution

Extend the existing `src/app/syte-config.ts` with site-wide constants:

```ts
const CONFIG = {
  baseUrl: 'https://pentajunior.ru',
  domain: 'pentajunior.ru',
  legacyDomain: 'penta-junior.ru',
  description: "...",
  syteName: "Пента Юниор",
  companyName: "ООО «Пента Юниор»",
  email: "penta@penta-junior.ru",
  phones: ["+7 (495) 644-46-16", "+7 (495) 730-58-51"],
  address: "111123, г. Москва, Электродный проезд, д. 14, стр. 1",
  // ...existing fields
} as const;
```

## Pages/components updated

- `src/app/layout.tsx` — JSON-LD `telephone`, `email`.
- `src/components/Layout/Footer.tsx` — phone/email links.
- `src/app/info/page.tsx` — phone/email in "Как сделать закать" section.
- `src/app/contacts/page.tsx` — phone/email in contacts info.
- `src/app/policy/page.tsx` — company name, site names, email, address in legal text.

## Patterns applied

1. **Phone links:** derive `tel:` from digits only:
   ```tsx
   <a href={`tel:${CONFIG.phones[0].replace(/\D/g, '')}`}>{CONFIG.phones[0]}</a>
   ```
2. **Email links:** single source:
   ```tsx
   <a href={`mailto:${CONFIG.email}`}>{CONFIG.email}</a>
   ```
3. **Policy text helpers:** pre-compose repeated phrases to keep JSX readable:
   ```ts
   const siteNames = `${CONFIG.legacyDomain}, ${CONFIG.domain}`;
   const siteNamesWww = `www.${CONFIG.legacyDomain}, ${CONFIG.domain}`;
   ```

## What to leave alone

- `src/app/globals.css` may contain historical comments referencing the domain — these are harmless documentation and do not affect rendering or SEO.
- The `baseUrl` constant in `syte-config.ts` is the canonical URL; `domain` and `legacyDomain` are only for human-readable text and mailto links.

## Build gate

After touching site constants and public pages:
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use v24.13.1
cd /home/natan/pentajunior-v2
./node_modules/.bin/tsc --noEmit
rm -rf .next tsconfig.tsbuildinfo
npm run build
```

Static page count stayed at 156/156; no route behavior changed.

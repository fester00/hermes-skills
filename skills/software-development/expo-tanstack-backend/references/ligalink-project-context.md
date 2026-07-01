---
name: ligalink-project
title: LigaLink — React Native Expo ISP Customer Portal
description: |
  Полная архитектура, дизайн-система и конвенции проекта LigaLink —
  кроссплатформенное мобильное приложение (React Native Expo) для личного
  кабинета абонента ISP, интегрированное с UTM5 REST API.
triggers:
  - ligalink
  - liga link
  - проект ligalink
  - ligalink app
  - работа с ligalink
  - liga-link
  - ligalink описание
---

# LigaLink — Project Context

## 1. Общая архитектура

| Слой | Технология | Назначение |
|------|-----------|------------|
| Framework | React Native + Expo SDK 52 | Кроссплатформенная разработка |
| Router | Expo Router (file-based) | Навигация, `/app` структура |
| State Server | TanStack Query (React Query) | Кэширование API-данных |
| State Client | Zustand | Auth-состояние (isAuthenticated, token) |
| HTTP Client | Кастомный `fetch`-wrapper | Cookie-based auth (sid_customer) |
| UI | React Native + LinearGradient | Нативные компоненты |
| Icons | @expo/vector-icons | FontAwesome, MaterialIcons, Ionicons, SimpleLineIcons |
| Calendar | react-native-calendars | Календарь выбора периода |

## 2. API-интеграция (UTM5 REST)

- **Базовый URL:** `https://lk.liga-link.net/customer_api`
- **Авторизация:** Cookie-based (`sid_customer`), не JWT
- **RN-особенность:** `fetch` в React Native не хранит cookie между запросами → `sid_customer` передаётся через заголовок `Cookie: sid_customer=...`
- **Сохранение сессии:** **In-memory only** (`inMemorySid`). Закрытие приложения = сброс сессии, пользователь должен войти заново.
- **Logout:** `POST /auth/logout` + `removeSessionId()` + `removeToken()` + `zustand.logout()`

### AccountService (api/types.ts)
Ключевые поля для UI:
- `cost`, `cost_coef` — стоимость услуги.
- `discount_period_start: number` — Unix timestamp начала расчётного периода.
- `discount_period_end: number` — Unix timestamp конца расчётного периода.
- Форматирование: `new Date(ts * 1000).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })` → `"01/08"`.

**Паттерн использования на главном экране (расчётный период):**
```tsx
const firstService = mainAccount?.services?.[0];
const periodStart = firstService?.discount_period_start
  ? new Date(firstService.discount_period_start * 1000).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
  : '--/--';
const periodEnd = firstService?.discount_period_end
  ? new Date(firstService.discount_period_end * 1000).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
  : '--/--';
const billingPeriod = firstService ? `${periodStart} — ${periodEnd}` : '01/08 — 01/09';
```
Затем передать `period={billingPeriod}` в `DetailUser`.

### Endpoints (api/endpoints.ts)
```
/auth/login       POST  → { sid_customer }
/auth/logout      POST  → { result: 'OK' }
/account          GET   → профиль абонента
/account/links    GET   → привязанные услуги
/services/list    GET   → список услуг
/services/tariffs GET   → тарифы
/notifications    GET   → уведомления
/stats/statistics GET   → статистика (пополнения)
/stats/full       GET   → полная статистика (блокировки)
/payment/methods  GET   → способы оплаты
```

## 3. Структура проекта

```
ligalink/
├── app/
│   ├── (tabs)/
│   │   ├── _layout.tsx      ← TabLayout (5 табов)
│   │   ├── index.tsx        ← Главный экран
│   │   ├── phinance.tsx     ← Финансы + выход
│   │   ├── service.tsx      ← Услуги (тарифы, подключение)
│   │   ├── notice.tsx       ← Уведомления + календарь
│   │   └── profile.tsx      ← Профиль (3 блока, редактирование)
│   ├── _layout.tsx          ← RootLayout + AuthGuard
│   └── login.tsx            ← Экран авторизации
├── api/
│   ├── client.ts            ← HTTP-клиент (fetch + cookie)
│   ├── endpoints.ts         ← URL всех эндпоинтов
│   ├── query-keys.ts        ← TanStack Query keys
│   ├── types.ts             ← TypeScript интерфейсы
│   └── services/            ← HTTP-методы по доменам
│       ├── auth.ts          ← login, logout
│       ├── profile.ts       ← getProfile, updateProfile
│       ├── services.ts      ← getServices, getTariffs
│       ├── notification.ts  ← getNotifications
│       ├── statistics.ts    ← getStatistics, getFullStatistics
│       └── payment.ts       ← getPaymentMethods
├── hooks/api/               ← TanStack Query hooks
│   ├── auth.ts              ← useLogin, useLogout
│   ├── profile.ts           ← useProfile, useUpdateProfile
│   ├── catalog.ts           ← useServices, useTariffs, useServiceLinks
│   ├── billing.ts           ← useStatistics, useFullStatistics
│   ├── payments.ts          ← usePaymentMethods
│   └── notifications.ts     ← useNotifications
├── lib/
│   ├── auth-store.ts        ← Zustand (isAuthenticated, token, logout)
│   └── storage.ts           ← AsyncStorage (sid_customer, token)
├── components/
│   ├── BlockHeader.tsx      ← Красный заголовок блока + BInput
│   ├── WelcomeHeader.tsx    ← Шапка с именем и логотипом
│   ├── Detail.tsx           ← DetailUser (баланс, период)
│   ├── Vallet.tsx           ← Кошелёк с кнопкой пополнения
│   ├── NoticeList.tsx       ← Список уведомлений (View + .map())
│   ├── Checkbox.tsx         ← Чекбокс с label
│   └── ui/                  ← Expo-шаблонные компоненты
├── constants/theme.ts       ← Цветовая палитра (light/dark)
├── providers/QueryProvider.tsx ← TanStack QueryClientProvider
└── assets/images/           ← Android adaptive icons, splash, favicon
```

## 4. Дизайн-система (PDF-макеты)

### Палитра (constants/theme.ts)
```ts
boxOne:   ['#9a191f', '#e30613']   // красный градиент (шапки, кнопки)
boxTwo:   ['#95c11f', '#dedc00']   // оранжевый градиент (карточки услуг)
tabsBGgradient: ['#e30613', '#f5a623'] // градиент таб-бара
accentGreen: '#95c11f'              // зелёный (положительные суммы)
background: '#ffffff' / '#000000'
subBackground: '#ededed' / '#1c1c1e'
text: '#000000' / '#ffffff'
subtext: '#9a191f' / '#e30613'
activeTab: '#a3191c'
tintBackground: '#9a191f'
```

### Экраны (соответствие PDF)
| Экран | Файл PDF | Ключевые элементы |
|-------|----------|-------------------|
| Главный | `ЛигаЛинк_приложение_Главный_с.pdf` | 2 карточки (Адрес красный + Услуги оранжевый), баланс, кошелёк, уведомления |
| Финансы | `ЛигаЛинк_приложение_Финансы_с.pdf` | Баланс, чекбоксы Автоплатёж/Уведомления, история пополнений, блокировки, выход |
| Услуги | `ЛигаЛинк_приложение_Услуги_с.pdf` | Тариф (Интернет/ТВ), кнопка смены ↻, подключённые услуги, дополнительные |
| Уведомления | `ЛигаЛинк_приложение_Уведомления_с.pdf` | Баланс, период, календарь, фильтрация, долгое нажатие → модалка |
| Профиль | `ЛигаЛинк_приложение_Профиль_с.pdf` | 3 блока (Адрес, Персональные, Контактные), редактирование по блокам |

### BlockHeader + BInput
- **Заголовок блока:** `LinearGradient` красный, border-radius справа
- **Иконка Saved:** `SimpleLineIcons name="note"`
- **Иконка onEdit:** `MaterialIcons name="edit-note"`
- **BInput editMode=false:** `backgroundColor: colors.subBackground`, `editable: false`
- **BInput editMode=true:** `borderColor: colors.boxTwo[0]` (оранжевый), `borderWidth: 2`, `editable: true`

## 5. Auth Flow

### Вход
1. Пользователь вводит логин/пароль на `/login`
2. `useLogin.mutate()` → `POST /auth/login`
3. API возвращает `{ sid_customer }` в body
4. `client.ts` сохраняет `sid_customer` в `AsyncStorage`
5. `useLogin.onSuccess` → `authStore.setToken(sid)` → `isAuthenticated = true`
6. `AuthGuard` ловит `isAuthenticated = true` → редирект на `/(tabs)`

### Выход
1. Нажатие «Выйти» на экране Финансы
2. `logoutMutation.mutate()` → `POST /auth/logout`
3. `api/services/auth.ts` → `removeSessionId()` (чистит cookie)
4. `hooks/api/auth.ts` `onSuccess`/`onError` → `logoutStore()`
5. `auth-store.ts` → `removeToken()` + `set({ isAuthenticated: false })`
6. `AuthGuard` ловит `isAuthenticated = false` → редирект на `/login`

### AuthGuard (app/_layout.tsx)
```tsx
useEffect(() => {
  if (isLoading) return;
  if (!isAuthenticated && !atLogin) router.replace('/login');
  if (isAuthenticated && atLogin) router.replace('/(tabs)');
}, [isAuthenticated, isLoading, segments]);
```

## 6. Таб-бар (5 табов)

```
┌─────────┬─────────┬─────────┬─────────┬─────────┐
│ Главная │ Финансы │ Услуги  │Уведомл. │ Профиль │
│ house   │ ruble   │ list-ul │notif.   │ person  │
└─────────┴─────────┴─────────┴─────────┴─────────┘
```
- Фон: градиент `tabsBGgradient` (красный→оранжевый)
- Активный: белый текст на `#a3191c`
- Неактивный: `rgba(255,255,255,0.7)`
- `tabBarHideOnKeyboard: true` (скрывается при клавиатуре)

## 7. Известные ограничения и решения

| Проблема | Решение |
|----------|---------|
| RN fetch не хранит cookie | Ручная передача `Cookie: sid_customer=...` заголовком |
| VirtualizedList warning | НЕ использовать FlatList внутри ScrollView → только `View` + `.map()` |
| Query data cannot be undefined | `await client.get() ?? []` + `initialData: []` в хуках |
| Logout без редиректа | `useLogout` должен вызывать `logoutStore()` в `onSuccess`/`onError` |
| SetState во время рендера | `router.replace()` только внутри callback (onPress, onSuccess), НЕ в теле компонента |
| CORS в Expo Web | Тестировать только на реальном устройстве/эмуляторе |

### UI-паттерн: глазик в парольном поле (show/hide password)

**⚠️ Важно:** `position: 'absolute'` (классический подход с web) внутри `ScrollView` или `KeyboardAvoidingView` в React Native ломает нажатия — глазик становится невидим для touch-событий. Используй `flexDirection: 'row'` обёртку.

```tsx
import { useState } from 'react';
import { View, TextInput, TouchableOpacity, StyleSheet } from 'react-native';
import Ionicons from '@expo/vector-icons/Ionicons';

function PasswordInput() {
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  return (
    <View style={styles.passwordWrapper}>
      <TextInput
        style={[styles.input, styles.passwordInput]}
        value={password}
        onChangeText={setPassword}
        secureTextEntry={!showPassword}
        placeholder="Введите пароль"
      />
      <TouchableOpacity
        style={styles.eyeButton}
        onPress={() => setShowPassword(v => !v)}
        activeOpacity={0.6}
        hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
      >
        <Ionicons
          name={showPassword ? 'eye-off' : 'eye'}
          size={22}
          color={colors.subtext}
        />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  input: {
    height: 48,
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 16,
    borderWidth: 1,
  },
  passwordWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    borderWidth: 1,
    paddingRight: 4,
  },
  passwordInput: {
    flex: 1,
    height: 48,
    paddingHorizontal: 16,
    fontSize: 16,
    backgroundColor: 'transparent',
  },
  eyeButton: {
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
```

Ключевые моменты:
- Используем `Ionicons` (`eye` / `eye-off`) — уже в проекте.
- `secureTextEntry={!showPassword}` переключает маскировку. По умолчанию пароль СКРЫТ (`showPassword = false`).
- **НЕ используем** `position: 'absolute'` внутри `ScrollView` — нажатия не проходят.
- **Цвет иконки:** используй `colors.text` (чёрный/белый), а НЕ `colors.subtext` (красный `#9a191f`) — на сером `subBackground` красный глазик почти невидим. Это была реальная причина "глазик не работает" в сессии от 2026-05-06.
- Обёртка `passwordWrapper` — `flexDirection: 'row'`, фон и бордер вынесены сюда.
- `hitSlop` на `TouchableOpacity` — увеличивает зону нажатия на глазик.
- `flex: 1` на `TextInput` — занимает всё доступное пространство.
- `backgroundColor: 'transparent'` на инпуте, чтобы не конфликтовал с фоном обёртки.

## 8. Конвенции кода

- **Стили:** Inline-стили с `colors.` из темы, хардкод `#fff` только для белого текста на цветном фоне
- **Списки:** Никогда `FlatList` внутри `ScrollView` → `View` + `.map()`
- **Навигация:** `router.push('/(tabs)/xxx')` для переходов, `router.replace('/login')` для auth-редиректов
- **API:** Все массивные query-функции возвращают `|| []` (fallback)
- **Типы:** `api/types.ts` — единый источник интерфейсов

## 9. Команды

```bash
# Dev-сервер (очистка кэша Metro)
cd ligalink && npx expo start --clear

# Android
npx expo start --android --clear

# TypeScript check
npx tsc --noEmit
```

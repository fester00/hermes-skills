# LigaLink Profile Screen Rewrite — Session Notes

Date: 2025-01-06
Project: fester00/ligalink (React Native Expo + TanStack Query)

## What was built

Full profile editing screen with 3 editable blocks, each toggled independently.

### Architecture decisions

1. **Per-block edit mode**, not global. Each of the 3 blocks (Address, Personal, Contact) has its own `useState(false)` edit flag. This lets the user edit one section without unlocking all fields.

2. **BlockHeader component** acts as both title and toggle button. It accepts:
   - `title: string` — no `\n` (causes line-break artifacts in RN)
   - `status: 'Saved' | 'onEdit'` — switches icon (`note` → `edit-note`)
   - `onPress: () => void` — toggles the parent block's edit state

3. **BInput** — thin wrapper around `TextInput` that applies theme colors and edit-mode border highlight:
   - `backgroundColor` from `colors.subBackground` (dynamic, not hardcoded)
   - `borderColor: colors.boxTwo[0]` when `editMode=true` (orange outline)
   - `editable={editMode}` — prevents input when locked

### Critical bug: hardcoded `#ededed` background

The first version of `BlockHeader.tsx` had `backgroundColor: '#ededed'` inside `StyleSheet.create()`. This color never changed for dark mode. Fix: remove `backgroundColor` from StyleSheet and apply it inline via `colors.subBackground` at render time.

### Critical bug: inline color props on BInput

In `profile.tsx`, some `<BInput>` calls had inline style props:
```tsx
<BInput ... style={{ flex: 1, color: colors.text, backgroundColor: colors.subtext }} />
```
This overrode the component's internal theme logic and caused wrong colors. Fix: remove `color` and `backgroundColor` from inline style — BInput handles them internally.

### Keyboard handling

- `tabBarHideOnKeyboard: true` in `_layout.tsx` — hides bottom nav
- `KeyboardAvoidingView` wrapping `ScrollView` in `profile.tsx` — pushes content above keyboard
- `keyboardShouldPersistTaps="handled"` — buttons work without dismissing keyboard

### Logout flow

`useLogout` mutation must call `logoutStore()` (zustand) in **both** `onSuccess` and `onError`. Otherwise `AuthGuard` won't see `isAuthenticated=false` and won't redirect. The `phinance.tsx` logout handler uses callback pattern:
```ts
logoutMutation.mutate(undefined, {
  onSuccess: () => router.replace('/login'),
  onError: () => router.replace('/login'),
})
```

Never call `router.replace()` conditionally inside render (e.g. `if (logoutMutation.isSuccess) router.replace(...)`). This throws a React Navigation error because it triggers navigation during render phase.

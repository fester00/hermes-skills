# React Native — VirtualizedList inside ScrollView warning

## Symptom

Metro logs:
```
VirtualizedLists should never be nested inside plain ScrollViews with the same
orientation because it can break windowing and other functionality
```

## Root cause

`FlatList` (and `SectionList`, any `VirtualizedList`) inside a parent `ScrollView`
competes for scroll velocity, layout calculations, and `onScroll` events.

## Solutions

### 1. Replace FlatList with View + .map() (best for short lists)

Use when the list is < 30 items and shares the screen with static content.

```tsx
// components/NoticeList.tsx
import { View, Text } from 'react-native';

export function NoticeList({ notices }) {
  return (
    <View style={{ paddingHorizontal: 4 }}>
      {notices.map((item, i) => (
        <View key={i} style={{ marginBottom: 10 }}>
          <Text>{item.date}</Text>
          <Text>{item.text}</Text>
        </View>
      ))}
    </View>
  );
}
```

Then the parent screen uses a single top-level `ScrollView`:

```tsx
<ScrollView>
  <WelcomeHeader />
  <NoticeList notices={data} />
  <Footer />
</ScrollView>
```

**Important:** Even `scrollEnabled={false}` on a nested `ScrollView` can still
trigger the warning on some RN versions. The safest approach is to remove
`ScrollView` entirely and use a plain `View` wrapper.

### 2. Make FlatList the root scroll container (best for long lists)

Use when the list is the primary content of the screen and may contain 50+ items.

```tsx
<FlatList
  data={items}
  ListHeaderComponent={<WelcomeHeader />}
  ListFooterComponent={<Footer />}
  renderItem={({ item }) => <ItemCard item={item} />}
  keyExtractor={(item, i) => String(i)}
/>
```

## Decision table

| Situation | Preferred approach |
|-----------|-------------------|
| List < 30 items, mixed with static content | `View` + `.map()` inside parent `ScrollView` |
| List 50+ items, primary content | `FlatList` as root, `ListHeaderComponent` for static parts |
| Need pull-to-refresh on the whole screen | Parent `ScrollView` with `RefreshControl` + `View` + `.map()` |
| Inside a modal / bottom sheet | `FlatList` or `FlashList` as root of the modal content |

## Why metro cache hides the fix

After replacing `FlatList` with `View`, the warning may still appear because
Metro bundler caches the compiled bundle. Always run:

```bash
npx expo start --clear
```

or shake the device → "Reload" in Expo Go to force a full re-bundle.

# Product Template Mapping: Category → Template Type → Component → Fields

## Mapping Table

| Category ID | Category Slug | template_type | Template Component |
|---|---|---|---|
| 1 | `silikonovye-i-poliuretanovye-kompaundy` | `silikon` | `SilikonTemplate.tsx` |
| 2 | `razdelitelnye-smazki` | `smazka` | `ReleaseTemplate.tsx` |
| 3 | `silikonovye-germetiki` | `sealant` | `SealantTemplate.tsx` |
| 4 | `masla-pms` | `oil` | `OilTemplate.tsx` |
| 5 | `antiprigarnye-kovriki` | `kovrik` | `DefaultTemplate.tsx` |
| 6 | `penogasiteli` | `penogasitel` | `DefaultTemplate.tsx` |
| 7 | `gidrofobizatory` | `gidrofob` | `DefaultTemplate.tsx` |
| 8 | `smazki` | `grease` | `GreaseTemplate.tsx` |
| 9 | `kosmeticheskie-krema` | `krem` | `DefaultTemplate.tsx` |
| 10 | `tekhnologicheskie-zhidkosti` | `techmol` | `DefaultTemplate.tsx` |
| 11 | `silicon-products` | `silicon` | `DefaultTemplate.tsx` |
| 12 | `silikonovye-elastomery` | `elastomer` | `DefaultTemplate.tsx` |

## Template Component Directory

```
src/components/ProductTemplates/
├── index.tsx                  # TemplateProps + shared types
├── TemplateSelector.tsx       # Maps template_type → component
├── SilikonTemplate.tsx        # silikon: intro + body + bullets + application
├── OilTemplate.tsx            # oil: intro + body + bullets + viscosity + applications
├── SealantTemplate.tsx        # sealant: intro + body + bullets + usage + temp_range
├── ReleaseTemplate.tsx        # smazka (release agents): full multi-section
├── GreaseTemplate.tsx         # grease (lubricants): intro + body + bullets + temp_range + method
└── DefaultTemplate.tsx        # fallback: intro + body + bullets + composition + method + temp_range + application
```

## Template Selector Component

```tsx
// src/components/ProductTemplates/TemplateSelector.tsx
import SilikonTemplate from "./SilikonTemplate";
import OilTemplate from "./OilTemplate";
import SealantTemplate from "./SealantTemplate";
import ReleaseTemplate from "./ReleaseTemplate";
import GreaseTemplate from "./GreaseTemplate";
import DefaultTemplate from "./DefaultTemplate";

const templateMap: Record<string, React.ComponentType<any>> = {
  silikon: SilikonTemplate,
  oil: OilTemplate,
  sealant: SealantTemplate,
  smazka: ReleaseTemplate,   // release / разделительные смазки
  grease: GreaseTemplate,    // lubricants / высокотемпературные смазки
};

export default function TemplateSelector({
  product,
}: {
  product: ProductForDetailPage;
}) {
  const Template = templateMap[product.templateType] || DefaultTemplate;
  return <Template product={product} templateData={product.templateData} />;
}
```

## Template Data JSON Structure (Full)

### ReleaseTemplateData — `smazka` (release agents)
```json
{
  "intro": "силиконовая смазка для разделения форм...",
  "composition": "силоксановые жидкости с добавлением функциональных наполнителей",
  "body": "Применяется в производстве РТИ, пластмасс и композитов...",
  "bullets": ["Высокая термостойкость", "Экономичный расход"],
  "properties": ["образует тонкую плёнку", "не влияет на окраску изделий"],
  "temp_range": "от -40 до +200 °C",
  "method": "наносится кистью, валиком или методом пневмораспыления",
  "surfaces": "металл, пластмасса, стеклопластик, резина",
  "usage": "при изготовлении деталей методом литья под давлением, вакуумформования и ручного формования",
  "shelf_life": "36 месяцев",
  "tu": "ТУ 20.30.12-001-79343382-2017",
  "application_industrial": [
    "При изготовлении пневматических камер",
    "При производстве РТИ на основе каучуков общего назначения"
  ],
  "application_domestic": "для разделения липких и вязких поверхностей: микроволновки, варочных панелей, духовых шкафов"
}
```

Rendered structure (all sections conditional):
1. **Описание** — `intro` + `composition` + `body` + bullet list (`properties` or `bullets`)
2. **Температурный диапазон** — `temp_range`
3. **Способ нанесения** — `method`
4. **Поверхности** — `surfaces`
5. **Использование** — `usage`
6. **Срок годности** — `shelf_life`
7. **ТУ** — `tu`
8. **Применение** — `application_industrial` (list) + `application_domestic` (text)

### SilikonTemplateData — `silikon` (compounds)
```json
{
  "intro": "двухкомпонентный силиконовый компаунд...",
  "body": "Отличается низкой вязкостью (12 000 мПа·с)...",
  "bullets": [
    "Точно воспроизводит мелкие детали рельефа",
    "Легко смешивается в пропорции 100:3"
  ],
  "application": "для изготовления литьевых форм"
}
```

### OilTemplateData — `oil` (PMS oils)
```json
{
  "intro": "жидкое силиконовое масло полиметилсилоксановой основы...",
  "body": "Применяется как присадка в эластомерные компаунды...",
  "bullets": ["Низкая вязкость", "Химическая инертность"],
  "viscosity_note": "вязкость масла по выбору заказчика",
  "applications": ["смазка подшипников", "гидравлические системы"]
}
```

### SealantTemplateData — `sealant` (silicone sealants)
```json
{
  "intro": "высокотемпературный нейтральный однокомпонентный силиконовый герметик...",
  "body": "устойчив к УФ-излучению, воздействию воды, масел...",
  "bullets": ["Температурный диапазон -60...+300 °C", "Нейтральная система отверждения"],
  "usage": "для герметизации швов, стыков и примыканий в строительстве",
  "temp_range": "от -60 до +300 °C"
}
```

### GreaseTemplateData — `grease` (high-temp lubricants)
```json
{
  "intro": "высокотемпературная смазка на основе силиконового масла...",
  "body": "Сохраняет смазывающие свойства при высоких температурах...",
  "bullets": ["Работает до +250 °C", "Водостойкая"],
  "temp_range": "от -40 до +250 °C",
  "method": "наносится тонким слоем кистью или распылением"
}
```

### DefaultTemplateData — fallback
```json
{
  "intro": "вспомогательный технологический продукт...",
  "body": "Применяется в различных технологических процессах...",
  "bullets": ["Универсальное применение"],
  "composition": "синтетические компоненты",
  "method": "в соответствии с технологической картой",
  "temp_range": "от -20 до +80 °C",
  "application": "универсальное технологическое применение"
}
```

## Conditional Rendering Rule

**Every field in every template is wrapped in a guard.** If data is missing, the section does not render — no empty headings, no blank paragraphs.

```tsx
// ReleaseTemplate.tsx — example of conditional rendering
{templateData.intro && (
  <section aria-labelledby="desc-heading">
    <h2 id="desc-heading">Описание</h2>
    <p><strong>{product.name}</strong> — {templateData.intro}</p>
    {templateData.composition && (
      <p><strong>Состав:</strong> {templateData.composition}</p>
    )}
    {templateData.body && <p>{templateData.body}</p>}
    {(templateData.bullets || templateData.properties) && (
      <ul>
        {(templateData.properties || templateData.bullets).map((b, i) => (
          <li key={i}><i className="bi bi-check2" /> {b}</li>
        ))}
      </ul>
    )}
  </section>
)}

{templateData.temp_range && (
  <section>
    <h2>Температурный диапазон</h2>
    <p>{templateData.temp_range}</p>
  </section>
)}

{templateData.application_industrial && (
  <section>
    <h2>Применение</h2>
    <ul>{templateData.application_industrial.map(...)}</ul>
    {templateData.application_domestic && <p>{templateData.application_domestic}</p>}
  </section>
)}
```

## Template Component Signature

Every template receives:

```typescript
interface TemplateProps {
  product: ProductForDetailPage;   // base fields (name, title, price, pack, image)
  templateData: Record<string, any>; // parsed JSON from DB
}
```

## Key Principles

1. **HTML structure in component, text in DB** — className strings live in `.tsx`, never in SQLite.
2. **Template data is flexible JSON** — different templates expect different keys, parsed dynamically.
3. **DefaultTemplate is always safe** — unknown template_type falls back gracefully.
4. **One template can serve multiple categories** — both `razdelitelnye-smazki` (smazka) and `smazki` (grease) use related but distinct templates.
5. **Conditional rendering per field** — no empty sections, no missing-data headings.

## Adding a New Template

1. Add entry to `templateMap` in `TemplateSelector.tsx`
2. Create component in `src/components/ProductTemplates/`
3. Define its `TemplateData` interface and field list
4. Add field definitions to `TemplateDataEditor` (see `references/template-data-editor-pattern.md`)
5. Add `template_type` to any products needing it (via migration or admin)
6. Ensure `DefaultTemplate` handles missing template_data fields gracefully

## Admin: Template Data Editor

The admin panel uses a dynamic `TemplateDataEditor` component that shows **different input fields depending on the selected `template_type`**.

See `references/template-data-editor-pattern.md` for full implementation: field definitions per template type, `lines` input handling, empty-field cleanup, and integration with product forms.

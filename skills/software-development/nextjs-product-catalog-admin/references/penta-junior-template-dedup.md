# Removing duplicate editable spec fields from SilikonTemplate

Session: 2026-06-14. Project `/home/natan/pentajunior-v2`.

## Goal
Stop maintaining numeric specifications twice: once in `template_data` fields rendered by `SilikonTemplate` and once in the `spec_table_id` comparison table. Keep only prose-friendly fields (`color`, `catalyst_type`) in the template; move all numeric specs to `spec_table_id`.

## Removed `templateData` keys
- `ratio`
- `viscosity`
- `hardness`
- `tensile_strength`
- `elongation`
- `tear_resistance`
- `pot_life`
- `cure_time`
- `shrinkage`
- `usage` (also removed from the template UI)

## Kept prose fields
- `color` (rendered as comma-separated list)
- `catalyst_type` (rendered as plain text paragraph)

## Files changed
- `src/components/ProductTemplates/SilikonTemplate.tsx` — removed keys from `Props`, removed the spec rendering block, added `color`/`catalyst_type` rendering, removed `usage` block.
- `src/components/admin/TemplateDataEditor.tsx` — updated the `silikon` fallback field list to match the DB contract.
- `src/components/ProductTemplates/index.tsx` — no shared-interface changes needed because the removed keys were local to `SilikonTemplate`.
- `pentajunior.db` — updated the `category_templates` row for `name='silikon'` via `scripts/update_silikon_template.py`.

## DB migration script
See `scripts/update_silikon_template.py` in the project repo (commit `4e237bd`). It filters `fields_json` by an explicit `KEEP` set and re-inserts missing `color`/`catalyst_type` fields if absent.

## Verification
- `npx tsc --noEmit`
- `npm run build`
- Checked that the admin product editor no longer shows the removed fields for existing `silikon` products.

## Lesson
The `category_templates` row is the real contract for the admin editor. Updating only the fallback list in `TemplateDataEditor.tsx` leaves old admin sessions unchanged. Always update the DB row and the fallback together in the same commit.

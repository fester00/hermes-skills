# Blog article published flag in pentajunior-v2

Blog articles are hardcoded in `src/data/blog/article-*.ts` and re-exported from `src/data/blog/index.ts`. To hide an article from the public site without deleting the source file, use the `published` boolean flag in the article object.

## Steps

1. Add `published: boolean` to `src/data/blog/types.ts`:
   ```ts
   export interface BlogArticle {
     ...
     published: boolean;
     content: string;
   }
   ```

2. Add `published: true` to every existing article file.

3. Set `published: false` in the article you want to hide.

4. Filter `published` in every consumer:
   - `src/app/blog/page.tsx` — JSON-LD `numberOfItems` and `itemListElement`
   - `src/app/blog/BlogList.tsx` — article grid and category filters
   - `src/app/blog/[articleId]/page.tsx`:
     - `generateStaticParams` → only published articles
     - `generateMetadata` → return 404 title if unpublished
     - page component → `notFound()` if unpublished
     - prev/next navigation → only over published articles
   - `src/app/production/[category]/[subcategory]/[product]/page.tsx` — `RelatedArticles` filters by `published`

## Important
Do not rely only on the article grid; the article page and JSON-LD must also be guarded, otherwise direct links and search engines still see the content.

## Verification
After toggling a flag:
```bash
npx tsc --noEmit && rm -rf .next && npm run build
```
The static page count for `/blog/[articleId]` should decrease when you unpublish an article.

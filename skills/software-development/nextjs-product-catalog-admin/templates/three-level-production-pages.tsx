> A ready-to-copy example of explicit three-level App Router pages for a product catalog where every product has a subcategory.
> Paste these into `src/app/production/[category]/page.tsx`, `src/app/production/[category]/[subcategory]/page.tsx`, and `src/app/production/[category]/[subcategory]/[product]/page.tsx`, then remove the old catch-all route.

## `src/app/production/[category]/page.tsx`

```tsx
import Link from "next/link";
import {
  getAllCategories,
  getCategoryBySlug,
  getSubcategoriesByCategoryId,
  getProductsByCategoryId,
} from "@/lib/db";
import { notFound } from "next/navigation";
import JsonData from "@/components/JsonLd";
import CONFIG from "@/app/syte-config";
import SubcategoryCard from "@/components/UI/Cards/SubcategoryCard";

const baseUrl = CONFIG.baseUrl;

export function generateStaticParams() {
  return getAllCategories().map((category) => ({
    category: category.slug,
  }));
}

interface PageProps {
  params: Promise<{ category: string }>;
}

export async function generateMetadata({ params }: PageProps) {
  const { category: categorySlug } = await params;
  const category = getCategoryBySlug(categorySlug);
  if (!category) return { title: "Категория не найдена" };

  return {
    title: `${category.title} — Пента Юниор`,
    description: category.meta_description,
    alternates: {
      canonical: `${baseUrl}/production/${category.slug}`,
    },
  };
}

function generateSubcategoryListJsonLd(
  category: any,
  subcategories: any[],
  pageUrl: string
) {
  return {
    "@type": "ItemList",
    "@id": `${pageUrl}/#subcategorylist`,
    name: `${category.title} — подкатегории`,
    numberOfItems: subcategories.length,
    itemListElement: subcategories.map((sub, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: sub.title,
      description: sub.meta_description,
      url: `${baseUrl}/production/${category.slug}/${sub.slug}`,
    })),
  };
}

export default async function CategoryPage({ params }: PageProps) {
  const { category: categorySlug } = await params;
  const category = getCategoryBySlug(categorySlug);
  if (!category) notFound();

  const subcategories = getSubcategoriesByCategoryId(category.id);
  const products = getProductsByCategoryId(category.id);
  const pageUrl = `${baseUrl}/production/${category.slug}`;

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "CollectionPage",
        "@id": `${pageUrl}/#webpage`,
        url: pageUrl,
        name: `${category.title} — Пента Юниор`,
        description: category.meta_description,
        mainEntity: { "@id": `${pageUrl}/#subcategorylist` },
      },
      generateSubcategoryListJsonLd(category, subcategories, pageUrl),
      {
        "@type": "BreadcrumbList",
        "@id": `${pageUrl}/#breadcrumb`,
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Главная", item: baseUrl },
          { "@type": "ListItem", position: 2, name: "Продукция", item: `${baseUrl}/production` },
          { "@type": "ListItem", position: 3, name: category.title, item: pageUrl },
        ],
      },
    ],
  };

  return (
    <>
      <JsonData data={jsonLd} />
      <div className="container py-5">
        <nav aria-label="Breadcrumb" className="mb-4">
          <ol className="breadcrumb category-breadcrumb">
            <li className="breadcrumb-item"><Link href="/">Главная</Link></li>
            <li className="breadcrumb-item"><Link href="/production">Продукция</Link></li>
            <li className="breadcrumb-item active" aria-current="page">{category.title}</li>
          </ol>
        </nav>

        <div className="row">
          <aside className="col-lg-4 d-none d-lg-block z-0">{/* nested category sidebar */}
          </aside>

          <div className="col-lg-8">
            <h1 className="category-header-title">{category.title}</h1>
            <p className="text-body-secondary">{category.page_description}</p>
            <span className="category-header-count">{products.length} товаров</span>

            {subcategories.length > 0 && (
              <section className="row g-4" aria-label="Подкатегории">
                {subcategories.map((s) => (
                  <SubcategoryCard
                    key={s.id}
                    subcategory={s}
                    categorySlug={category.slug}
                    productCount={products.filter((p) => p.subcategory_id === s.id).length}
                  />
                ))}
              </section>
            )}

            {category.seo_text && (
              <section
                className="category-seo-text mt-5 pt-4 border-top"
                dangerouslySetInnerHTML={{ __html: category.seo_text }}
              />
            )}
          </div>
        </div>
      </div>
    </>
  );
}
```

## `src/app/production/[category]/[subcategory]/page.tsx`

```tsx
import Image from "next/image";
import ProductImagePlaceholder from "@/components/ProductImagePlaceholder";
import Link from "next/link";
import {
  getAllCategories,
  getCategoryBySlug,
  getSubcategoryBySlug,
  getProductsBySubcategoryId,
  getProductCountBySubcategoryId,
  getSubcategoriesByCategoryId,
  formatPriceFull,
} from "@/lib/db";
import { notFound } from "next/navigation";
import JsonData from "@/components/JsonLd";
import CONFIG from "@/app/syte-config";

const baseUrl = CONFIG.baseUrl;

export function generateStaticParams() {
  const params: { category: string; subcategory: string }[] = [];
  for (const category of getAllCategories()) {
    for (const sub of getSubcategoriesByCategoryId(category.id)) {
      params.push({ category: category.slug, subcategory: sub.slug });
    }
  }
  return params;
}

interface PageProps {
  params: Promise<{ category: string; subcategory: string }>;
}

export default async function SubcategoryPage({ params }: PageProps) {
  const { category: categorySlug, subcategory: subcategorySlug } = await params;
  const category = getCategoryBySlug(categorySlug);
  const subcategory = getSubcategoryBySlug(subcategorySlug);

  if (!category || !subcategory || subcategory.category_id !== category.id) notFound();

  const products = getProductsBySubcategoryId(subcategory.id);
  const pageUrl = `${baseUrl}/production/${category.slug}/${subcategory.slug}`;

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "CollectionPage",
        "@id": `${pageUrl}/#webpage`,
        url: pageUrl,
        name: `${subcategory.title} — ${category.title}`,
        description: subcategory.meta_description,
      },
      {
        "@type": "BreadcrumbList",
        "@id": `${pageUrl}/#breadcrumb`,
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Главная", item: baseUrl },
          { "@type": "ListItem", position: 2, name: "Продукция", item: `${baseUrl}/production` },
          { "@type": "ListItem", position: 3, name: category.title, item: `${baseUrl}/production/${category.slug}` },
          { "@type": "ListItem", position: 4, name: subcategory.title, item: pageUrl },
        ],
      },
    ],
  };

  return (
    <>
      <JsonData data={jsonLd} />
      <div className="container py-5">
        <nav aria-label="Breadcrumb" className="mb-4">
          <ol className="breadcrumb category-breadcrumb">
            <li className="breadcrumb-item"><Link href="/">Главная</Link></li>
            <li className="breadcrumb-item"><Link href="/production">Продукция</Link></li>
            <li className="breadcrumb-item"><Link href={`/production/${category.slug}`}>{category.title}</Link></li>
            <li className="breadcrumb-item active" aria-current="page">{subcategory.title}</li>
          </ol>
        </nav>

        <div className="row">
          <aside className="col-lg-4 d-none d-lg-block z-0">{/* nested category sidebar */}
          </aside>

          <div className="col-lg-8">
            <h1>{subcategory.title}</h1>
            <p className="text-body-secondary">{subcategory.page_description}</p>
            <span className="category-header-count">{products.length} товаров</span>

            <div className="row g-2 mt-3">
              {products.map((product) => {
                const href = `/production/${category.slug}/${subcategory.slug}/${product.id}`;
                return (
                  <div className="col-md-6 col-xl-4" key={product.id}>
                    <div className="catalog-product-card h-100 d-flex flex-column">
                      <Link href={href} className="catalog-product-media position-relative d-block">
                        {product.image ? (
                          <Image src={product.image} alt={product.title} fill className="object-fit-cover" sizes="33vw" />
                        ) : (
                          <ProductImagePlaceholder title={product.title} className="h-100 w-100" />
                        )}
                      </Link>
                      <div className="catalog-product-body d-flex flex-column flex-grow-1">
                        <h2 className="catalog-product-title"><Link href={href}>{product.name}</Link></h2>
                        <ul className="catalog-product-features list-unstyled">
                          {product.features.slice(0, 3).map((f, i) => (
                            <li key={i}><i className="bi bi-dot" />{f}</li>
                          ))}
                        </ul>
                        <div className="catalog-product-footer mt-auto">
                          {product.price && (
                            <span className="catalog-product-price">
                              от {formatPriceFull(product.price, product.price_currency, product.price_unit)}
                            </span>
                          )}
                          <Link href={href} className="btn btn-sm btn-outline-primary rounded-pill px-3">Подробнее</Link>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
```

## `src/app/production/[category]/[subcategory]/[product]/page.tsx`

```tsx
import { getCategoryBySlug, getSubcategoryBySlug, getAllProducts, getAllCategories } from "@/lib/db";
import { notFound } from "next/navigation";
import ProductCard from "@/components/UI/Cards/ProductCard";
import JsonData from "@/components/JsonLd";
import CONFIG from "@/app/syte-config";

const baseUrl = CONFIG.baseUrl;

export function generateStaticParams() {
  const params: { category: string; subcategory: string; product: string }[] = [];
  for (const category of getAllCategories()) {
    for (const sub of getSubcategoriesByCategoryId(category.id)) {
      for (const product of getProductsBySubcategoryId(sub.id)) {
        params.push({
          category: category.slug,
          subcategory: sub.slug,
          product: product.id,
        });
      }
    }
  }
  return params;
}

interface PageProps {
  params: Promise<{ category: string; subcategory: string; product: string }>;
}

function generateProductJsonLd(product: any, category: any, subcategory: any) {
  const pageUrl = `${baseUrl}/production/${category.slug}/${subcategory.slug}/${product.id}`;
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Product",
        "@id": `${pageUrl}/#product`,
        name: product.title,
        description: product.meta_description || product.features.slice(0, 5).join(". "),
        url: pageUrl,
        image: product.image ? `${baseUrl}${product.image}` : `${baseUrl}/images/hero.webp`,
        brand: { "@type": "Brand", name: "Пента Юниор" },
        offers: product.price
          ? {
              "@type": "Offer",
              url: pageUrl,
              priceCurrency: product.price_currency === "USD" ? "USD" : "RUB",
              price: String(product.price).replace(/\s/g, ""),
              availability: "https://schema.org/InStock",
            }
          : undefined,
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Главная", item: baseUrl },
          { "@type": "ListItem", position: 2, name: "Продукция", item: `${baseUrl}/production` },
          { "@type": "ListItem", position: 3, name: category.title, item: `${baseUrl}/production/${category.slug}` },
          { "@type": "ListItem", position: 4, name: subcategory.title, item: `${baseUrl}/production/${category.slug}/${subcategory.slug}` },
          { "@type": "ListItem", position: 5, name: product.title, item: pageUrl },
        ],
      },
    ],
  };
}

export default async function ProductPage({ params }: PageProps) {
  const { category, subcategory, product: productId } = await params;

  const categoryObj = getCategoryBySlug(category);
  const subcategoryObj = getSubcategoryBySlug(subcategory);
  const product = getAllProducts().find((p) => p.id === productId);

  if (!categoryObj || !subcategoryObj || !product) notFound();
  if (product.category_id !== categoryObj.id) notFound();
  if (product.subcategory_id !== subcategoryObj.id) notFound();

  return (
    <>
      <JsonData data={generateProductJsonLd(product, categoryObj, subcategoryObj)} />
      <div className="container py-5">
        <ProductCard
          product={product}
          categorySlug={categoryObj.slug}
          subcategorySlug={subcategoryObj.slug}
        />
      </div>
    </>
  );
}
```

## Notes

- These examples intentionally omit the full sidebar markup; reuse the nested-tree component from `references/nested-category-sidebar-tree.md`.
- Import paths (`@/lib/db`, `@/components/...`) must match the project aliases.
- Always call `notFound()` when the requested category/subcategory/product combination is inconsistent.

# JSON DB CRUD Library — Complete Implementation

Full `src/lib/db.ts` from PentaJunior project (2025-06-12). Copy and adapt for any Next.js project using JSON file storage.

## File: `src/lib/db.ts`

```typescript
import fs from 'fs';
import path from 'path';

const DB_PATH = path.join(process.cwd(), 'src', 'data', 'db.json');

// ─── Types ─────────────────────────────────────────────────────────

export interface Product {
  id: string;
  name: string;
  price: string;
  image: string;
  description: string;
  category: string;
  article: string;
  url: string;
  specs: Record<string, string>;
  advantages: string[];
  videoUrl: string;
  oldPrice?: string;      // ← promo: old price
  isNew?: boolean;        // ← new product flag
}

export interface Category {
  slug: string;
  name: string;
  description: string;
  image: string;
}

export interface DbSchema {
  products: Product[];
  categories: Category[];
}

// ─── Helpers ───────────────────────────────────────────────────────

function readDb(): DbSchema {
  const raw = fs.readFileSync(DB_PATH, 'utf-8');
  return JSON.parse(raw);
}

function writeDb(db: DbSchema): void {
  fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2), 'utf-8');
}

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substring(2, 7);
}

// ─── Products CRUD ────────────────────────────────────────────────

export function getAllProducts(): Product[] {
  return readDb().products;
}

export function getProductById(id: string): Product | undefined {
  return readDb().products.find(p => p.id === id);
}

export function getProductsByCategory(categorySlug: string): Product[] {
  return readDb().products.filter(p => p.category === categorySlug);
}

export function createProduct(product: Omit<Product, 'id'>): Product {
  const db = readDb();
  const newProduct: Product = { ...product, id: generateId() };
  db.products.push(newProduct);
  writeDb(db);
  return newProduct;
}

export function updateProduct(id: string, updates: Partial<Product>): Product | null {
  const db = readDb();
  const idx = db.products.findIndex(p => p.id === id);
  if (idx === -1) return null;
  db.products[idx] = { ...db.products[idx], ...updates };
  writeDb(db);
  return db.products[idx];
}

export function deleteProduct(id: string): boolean {
  const db = readDb();
  const beforeLen = db.products.length;
  db.products = db.products.filter(p => p.id !== id);
  writeDb(db);
  return db.products.length < beforeLen;
}

// ─── Categories CRUD ────────────────────────────────────────────────

export function getAllCategories(): Category[] {
  return readDb().categories;
}

export function getCategoryBySlug(slug: string): Category | undefined {
  return readDb().categories.find(c => c.slug === slug);
}

export function createCategory(category: Omit<Category, 'slug'> & { slug?: string }): Category {
  const db = readDb();
  const newCategory: Category = {
    ...category,
    slug: category.slug || category.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''),
  };
  db.categories.push(newCategory);
  writeDb(db);
  return newCategory;
}

export function updateCategory(slug: string, updates: Partial<Category>): Category | null {
  const db = readDb();
  const idx = db.categories.findIndex(c => c.slug === slug);
  if (idx === -1) return null;
  db.categories[idx] = { ...db.categories[idx], ...updates };
  writeDb(db);
  return db.categories[idx];
}

export function deleteCategory(slug: string): boolean {
  const db = readDb();
  const beforeLen = db.categories.length;
  db.categories = db.categories.filter(c => c.slug !== slug);
  writeDb(db);
  return db.categories.length < beforeLen;
}
```

## Usage in API Routes

```typescript
import { NextResponse } from 'next/server';
import { getAllProducts, createProduct, updateProduct, deleteProduct } from '@/lib/db';

export async function GET() {
  return NextResponse.json(getAllProducts());
}

export async function POST(request: Request) {
  const body = await request.json();
  return NextResponse.json(createProduct(body));
}

export async function PUT(request: Request) {
  const body = await request.json();
  return NextResponse.json(updateProduct(body.id, body));
}

export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');
  if (!id) return NextResponse.json({ error: 'No id' }, { status: 400 });
  return NextResponse.json({ success: deleteProduct(id) });
}
```

## Design Decisions

1. **Synchronous file I/O** — `readFileSync`/`writeFileSync` are used because API routes run server-side in Node.js. No async overhead needed for a single JSON file.
2. **No in-memory cache** — Every request reads fresh state from disk. This prevents stale data when multiple tabs edit the DB simultaneously. Trade-off: slightly higher I/O, acceptable for low-traffic admin panels.
3. **`JSON.stringify(db, null, 2)`** — Pretty-printed JSON makes git diffs readable and allows manual editing of `db.json` in a pinch.
4. **`generateId()`** — `Date.now()` + random suffix produces sortable, collision-resistant IDs without external dependencies.
5. **Slug generation** — `createCategory` auto-generates URL-friendly slugs from names if not provided, using the standard lowercase-hyphen pattern.

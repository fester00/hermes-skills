import { promises as fs } from 'fs';
import path from 'path';

const DB_PATH = path.join(process.cwd(), 'src', 'data', 'db.json');

export interface DbProduct {
  id: string;
  name: string;
  categoryId: number;
  title: string;
  price: string;
  image?: string;
  features: string[];
  pack?: string;
  metaDescription: string;
  description?: string;
  application?: string;
  specTableId?: string;
  news: boolean;
  stockInfo?: {
    newPrice: string;
    condition?: string;
  };
  keywords?: string[];
  colors?: string[];
}

export interface DbCategory {
  id: number;
  title: string;
  slug: string;
  href: string;
  image?: string;
  metaDescription: string;
  pageDescription: string;
  relatedCategories?: number[];
}

export interface Database {
  products: DbProduct[];
  categories: DbCategory[];
}

export async function readDb(): Promise<Database> {
  try {
    const data = await fs.readFile(DB_PATH, 'utf-8');
    return JSON.parse(data);
  } catch {
    return { products: [], categories: [] };
  }
}

export async function writeDb(db: Database): Promise<void> {
  await fs.writeFile(DB_PATH, JSON.stringify(db, null, 2), 'utf-8');
}

export async function getProducts(): Promise<DbProduct[]> {
  const db = await readDb();
  return db.products;
}

export async function getProductById(id: string): Promise<DbProduct | null> {
  const db = await readDb();
  return db.products.find((p) => p.id === id) || null;
}

export async function createProduct(product: DbProduct): Promise<DbProduct> {
  const db = await readDb();
  db.products.push(product);
  await writeDb(db);
  return product;
}

export async function updateProduct(id: string, updates: Partial<DbProduct>): Promise<DbProduct | null> {
  const db = await readDb();
  const index = db.products.findIndex((p) => p.id === id);
  if (index === -1) return null;
  db.products[index] = { ...db.products[index], ...updates };
  await writeDb(db);
  return db.products[index];
}

export async function deleteProduct(id: string): Promise<boolean> {
  const db = await readDb();
  const initialLength = db.products.length;
  db.products = db.products.filter((p) => p.id !== id);
  if (db.products.length !== initialLength) {
    await writeDb(db);
    return true;
  }
  return false;
}

export async function getCategories(): Promise<DbCategory[]> {
  const db = await readDb();
  return db.categories;
}

export async function getCategoryById(id: number): Promise<DbCategory | null> {
  const db = await readDb();
  return db.categories.find((c) => c.id === id) || null;
}

export async function createCategory(category: DbCategory): Promise<DbCategory> {
  const db = await readDb();
  db.categories.push(category);
  await writeDb(db);
  return category;
}

export async function updateCategory(id: number, updates: Partial<DbCategory>): Promise<DbCategory | null> {
  const db = await readDb();
  const index = db.categories.findIndex((c) => c.id === id);
  if (index === -1) return null;
  db.categories[index] = { ...db.categories[index], ...updates };
  await writeDb(db);
  return db.categories[index];
}

export async function deleteCategory(id: number): Promise<boolean> {
  const db = await readDb();
  const initialLength = db.categories.length;
  db.categories = db.categories.filter((c) => c.id !== id);
  if (db.categories.length !== initialLength) {
    await writeDb(db);
    return true;
  }
  return false;
}

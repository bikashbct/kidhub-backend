import Image from "next/image";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { getApiRoot, getRequestHostname, normalizeMediaUrl } from "@/lib/api";

type Category = {
  id: number;
  name: string;
  image?: string | null;
};

type Item = {
  id: number;
  category: number;
  name: string;
  content_name?: string | null;
  object_image?: string | null;
  audio?: string | null;
  order?: number | null;
};

type ApiResponse<T> = T[] | { results?: T[]; data?: T[] };

type ApiIndex = {
  categories?: string;
  items?: string;
  learningitems?: string;
};

const getColorFromString = (value: string): string => {
  let hash = 0;

  for (let i = 0; i < value.length; i += 1) {
    hash = value.charCodeAt(i) + ((hash << 5) - hash);
  }

  const color = (hash & 0x00ffffff).toString(16).toUpperCase();
  return `#${"000000".substring(0, 6 - color.length)}${color}`;
};

const normalizeList = <T,>(data: ApiResponse<T>): T[] => {
  if (Array.isArray(data)) {
    return data;
  }

  if (data && typeof data === "object") {
    if (Array.isArray((data as { results?: T[] }).results)) {
      return (data as { results: T[] }).results;
    }

    if (Array.isArray((data as { data?: T[] }).data)) {
      return (data as { data: T[] }).data;
    }
  }

  return [];
};

const getApiIndex = async (): Promise<ApiIndex> => {
  const response = await fetch(getApiRoot(), { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Unable to reach API root.");
  }

  return (await response.json()) as ApiIndex;
};

const getCategory = async (id: number): Promise<Category | null> => {
  const apiIndex = await getApiIndex();
  const categoriesUrl = apiIndex.categories ?? `${getApiRoot()}categories/`;
  const response = await fetch(categoriesUrl, { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Unable to load category.");
  }

  const data = (await response.json()) as ApiResponse<Category>;
  const categories = normalizeList(data);
  return categories.find((category) => category.id === id) ?? null;
};

const getItems = async (): Promise<Item[]> => {
  const apiIndex = await getApiIndex();
  const itemsUrl =
    apiIndex.items ?? apiIndex.learningitems ?? `${getApiRoot()}items/`;
  const response = await fetch(itemsUrl, { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Unable to load items.");
  }

  const data = (await response.json()) as ApiResponse<Item>;
  return normalizeList(data);
};

type PageProps = {
  params: Promise<{ id: string }> | { id: string };
  searchParams?: Promise<{ item?: string }> | { item?: string };
};

export default async function CategoryPage({ params, searchParams }: PageProps) {
  const resolvedParams = await params;
  const resolvedSearch = searchParams ? await searchParams : undefined;
  const categoryId = Number(resolvedParams.id);

  if (Number.isNaN(categoryId)) {
    throw new Error("Invalid category id.");
  }

  const [category, items] = await Promise.all([
    getCategory(categoryId),
    getItems(),
  ]);
  const requestHostname = await getRequestHostname();

  const categoryItems = items
    .filter((item) => item.category === categoryId)
    .sort((a, b) => (a.order ?? 0) - (b.order ?? 0));

  const currentItemId = resolvedSearch?.item
    ? Number(resolvedSearch.item)
    : categoryItems[0]?.id;

  const currentIndex = categoryItems.findIndex(
    (item) => item.id === currentItemId,
  );

  const safeIndex = currentIndex >= 0 ? currentIndex : 0;
  const currentItem = categoryItems[safeIndex];
  const prevItem = categoryItems[safeIndex - 1];
  const nextItem = categoryItems[safeIndex + 1];
  const currentImageUrl = currentItem
    ? normalizeMediaUrl(currentItem.object_image, requestHostname)
    : null;
  const fallbackColor = currentItem
    ? getColorFromString(currentItem.content_name ?? currentItem.name)
    : "#A3E635";

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-100 text-slate-900 dark:from-zinc-950 dark:via-zinc-950 dark:to-zinc-900 dark:text-zinc-50">
      <main className="mx-auto flex w-full max-w-6xl flex-col gap-10 px-6 pb-20 pt-16">
        <header className="flex flex-col gap-6">
          <div className="flex flex-wrap items-center gap-3">
            <Badge className="px-3 py-1 text-sm">Category</Badge>
            {category ? (
              <Badge variant="secondary" className="px-3 py-1 text-sm">
                {category.name}
              </Badge>
            ) : null}
          </div>
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div className="space-y-3">
              <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
                {category?.name ?? "Learning category"}
              </h1>
              <p className="max-w-2xl text-base text-slate-600 dark:text-zinc-300">
                Follow the lessons in the order defined by your API. Use the
                navigation to move through the content.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Button asChild variant="outline">
                <Link href="/">Back to categories</Link>
              </Button>
              <Button variant="outline">
                Items: {categoryItems.length}
              </Button>
            </div>
          </div>
        </header>

        <Separator />

        {categoryItems.length === 0 || !currentItem ? (
          <Card>
            <CardHeader>
              <CardTitle>No items yet</CardTitle>
              <CardDescription>
                Create items for this category in the API to start learning.
              </CardDescription>
            </CardHeader>
          </Card>
        ) : (
          <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
            <Card className="relative overflow-hidden border-slate-200/70 bg-white/90 shadow-sm backdrop-blur dark:border-zinc-800/70 dark:bg-zinc-950/70">
              <div className="pointer-events-none absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-sky-500 via-blue-500 to-indigo-500" />
              <CardHeader className="space-y-4">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="secondary" className="px-3 py-1 text-sm">
                    {category?.name ?? "Category"}
                  </Badge>
                  {currentItem.order !== undefined && currentItem.order !== null ? (
                    <Badge className="px-3 py-1 text-sm">
                      Lesson {currentItem.order + 1}
                    </Badge>
                  ) : null}
                </div>
                <CardTitle className="text-2xl font-semibold tracking-tight sm:text-3xl">
                  {currentItem.name}
                </CardTitle>
                <CardDescription className="text-base text-slate-600 dark:text-zinc-300">
                  Big, clear learning cards made for kids.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {currentImageUrl ? (
                  <div className="relative aspect-[4/3] w-full overflow-hidden rounded-xl border border-slate-200/70 dark:border-zinc-800/70">
                    <Image
                      src={currentImageUrl}
                      alt={currentItem.content_name ?? currentItem.name}
                      fill
                      unoptimized
                      className="object-cover"
                    />
                  </div>
                ) : (
                  <div
                    className="flex aspect-[4/3] w-full flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-slate-200/70 text-center text-slate-700 dark:border-zinc-800/70 dark:text-zinc-200"
                    style={{ backgroundColor: `${fallbackColor}22` }}
                  >
                    <span className="text-base font-semibold sm:text-lg">
                      Color card
                    </span>
                    <span className="rounded-full bg-white/80 px-4 py-1 text-sm font-semibold text-slate-700 shadow-sm dark:bg-zinc-900/70 dark:text-zinc-100">
                      {fallbackColor}
                    </span>
                  </div>
                )}
                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="rounded-2xl border border-slate-200/70 bg-white/80 p-4 text-center shadow-sm dark:border-zinc-800/70 dark:bg-zinc-950/70">
                    <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-zinc-400">
                      Name
                    </p>
                    <p className="text-xl font-semibold text-slate-900 sm:text-2xl dark:text-zinc-50">
                      {currentItem.name}
                    </p>
                  </div>
                  <div className="rounded-2xl border border-slate-200/70 bg-white/80 p-4 text-center shadow-sm dark:border-zinc-800/70 dark:bg-zinc-950/70">
                    <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-zinc-400">
                      Content name
                    </p>
                    <p className="text-xl font-semibold text-slate-900 sm:text-2xl dark:text-zinc-50">
                      {currentItem.content_name ?? currentItem.name}
                    </p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-3">
                  {prevItem ? (
                    <Button
                      asChild
                      variant="outline"
                      className="h-12 rounded-full px-6 text-base font-semibold"
                    >
                      <Link href={`/category/${categoryId}?item=${prevItem.id}`}>
                        ⬅️ Previous
                      </Link>
                    </Button>
                  ) : (
                    <Button
                      variant="outline"
                      disabled
                      className="h-12 rounded-full px-6 text-base font-semibold"
                    >
                      ⬅️ Previous
                    </Button>
                  )}
                  {nextItem ? (
                    <Button asChild className="h-12 rounded-full px-6 text-base font-semibold">
                      <Link href={`/category/${categoryId}?item=${nextItem.id}`}>
                        Next ➡️
                      </Link>
                    </Button>
                  ) : (
                    <Button
                      disabled
                      className="h-12 rounded-full px-6 text-base font-semibold"
                    >
                      Next ➡️
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="border-slate-200/70 bg-white/80 shadow-sm backdrop-blur dark:border-zinc-800/70 dark:bg-zinc-950/70">
              <CardHeader>
                <CardTitle className="text-lg">All items</CardTitle>
                <CardDescription>
                  Jump to any item in this category.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {categoryItems.map((item, index) => (
                  <Button
                    key={item.id}
                    asChild
                    variant={item.id === currentItem.id ? "default" : "outline"}
                    className="w-full justify-start"
                  >
                    <Link href={`/category/${categoryId}?item=${item.id}`}>
                      {index + 1}. {item.content_name ?? item.name}
                    </Link>
                  </Button>
                ))}
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}

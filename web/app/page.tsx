import Image from "next/image";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { getApiRoot, getRequestHostname, normalizeMediaUrl } from "@/lib/api";

type Category = {
  id: number;
  name: string;
  image?: string | null;
};

type ApiResponse = Category[] | { results?: Category[]; data?: Category[] };

type ApiIndex = {
  categories?: string;
  items?: string;
  learningitems?: string;
};

const normalizeCategories = (data: ApiResponse): Category[] => {
  if (Array.isArray(data)) {
    return data;
  }

  if (data && typeof data === "object") {
    if (Array.isArray((data as { results?: Category[] }).results)) {
      return (data as { results: Category[] }).results;
    }

    if (Array.isArray((data as { data?: Category[] }).data)) {
      return (data as { data: Category[] }).data;
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

const getCategories = async (): Promise<Category[]> => {
  const apiIndex = await getApiIndex();
  const categoriesUrl = apiIndex.categories ?? `${getApiRoot()}categories/`;
  const response = await fetch(categoriesUrl, { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Unable to load categories.");
  }

  const data = (await response.json()) as ApiResponse;
  return normalizeCategories(data);
};

export default async function Home() {
  const categories = await getCategories();
  const requestHostname = await getRequestHostname();

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-100 text-slate-900 dark:from-zinc-950 dark:via-zinc-950 dark:to-zinc-900 dark:text-zinc-50">
      <main className="mx-auto flex w-full max-w-6xl flex-col gap-10 px-6 pb-20 pt-16">
        <header className="flex flex-col gap-6">
          <div className="flex flex-wrap items-center gap-3">
            <Badge className="px-3 py-1 text-sm">Lets Learn</Badge>
            <Badge variant="secondary" className="px-3 py-1 text-sm">
              API Connected
            </Badge>
          </div>
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div className="space-y-3">
              <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
                Pick a category to start learning
              </h1>
              <p className="max-w-2xl text-base text-slate-600 dark:text-zinc-300">
                Select a category to view its lessons in a focused reader with
                next and previous navigation.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Button asChild>
                <Link href="/">Refresh</Link>
              </Button>
              <Button variant="outline">Categories: {categories.length}</Button>
            </div>
          </div>
        </header>

        <Separator />

        <section className="grid gap-6 md:grid-cols-2">
          {categories.length === 0 ? (
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>No categories found</CardTitle>
                <CardDescription>
                  Add categories in the API to populate this homepage.
                </CardDescription>
              </CardHeader>
            </Card>
          ) : (
            categories.map((category) => {
              const imageUrl = normalizeMediaUrl(
                category.image,
                requestHostname,
              );

              return (
                <Card
                  key={category.id}
                  className="group relative overflow-hidden border-slate-200/70 bg-white/80 shadow-sm backdrop-blur transition hover:-translate-y-0.5 hover:shadow-md dark:border-zinc-800/70 dark:bg-zinc-950/70"
                >
                  <div className="pointer-events-none absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-emerald-400 via-sky-500 to-indigo-500" />
                  {imageUrl ? (
                    <div className="relative h-44 w-full overflow-hidden">
                      <Image
                        src={imageUrl}
                        alt={category.name}
                        fill
                        unoptimized
                        className="object-cover transition duration-500 group-hover:scale-105"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-slate-950/60 via-slate-950/10 to-transparent" />
                    </div>
                  ) : null}
                  <CardHeader className="space-y-3">
                    <CardTitle className="text-xl">{category.name}</CardTitle>
                    <CardDescription className="text-sm text-slate-600 dark:text-zinc-300">
                      Explore lessons inside this category.
                    </CardDescription>
                    <Button asChild className="w-fit">
                      <Link href={`/category/${category.id}`}>Open category</Link>
                    </Button>
                  </CardHeader>
                </Card>
              );
            })
          )}
        </section>
      </main>
    </div>
  );
}

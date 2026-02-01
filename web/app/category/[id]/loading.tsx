import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-100 text-slate-900 dark:from-zinc-950 dark:via-zinc-950 dark:to-zinc-900 dark:text-zinc-50">
      <main className="mx-auto flex w-full max-w-6xl flex-col gap-10 px-6 pb-20 pt-16">
        <div className="space-y-4">
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-10 w-2/3" />
          <Skeleton className="h-4 w-1/2" />
        </div>
        <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
          <Card>
            <CardHeader className="space-y-3">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-2/3" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-64 w-full" />
              <div className="flex gap-3">
                <Skeleton className="h-10 w-28" />
                <Skeleton className="h-10 w-24" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="space-y-3">
              <Skeleton className="h-5 w-32" />
              <Skeleton className="h-4 w-2/3" />
            </CardHeader>
            <CardContent className="space-y-2">
              {Array.from({ length: 4 }).map((_, index) => (
                <Skeleton key={`item-${index}`} className="h-9 w-full" />
              ))}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

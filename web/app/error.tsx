"use client";

import { useEffect } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type ErrorProps = {
  error: Error & { digest?: string };
  reset: () => void;
};

export default function ErrorState({ error, reset }: ErrorProps) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-100 text-slate-900 dark:from-zinc-950 dark:via-zinc-950 dark:to-zinc-900 dark:text-zinc-50">
      <main className="mx-auto flex w-full max-w-2xl flex-col items-center justify-center px-6 py-24">
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Unable to load lessons</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-slate-600 dark:text-zinc-300">
              The API could not be reached. Confirm the backend is running at
              127.0.0.1:8000 and try again.
            </p>
            <Button onClick={reset}>Try again</Button>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

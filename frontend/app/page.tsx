import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-center font-mono text-sm">
        <h1 className="text-4xl font-bold mb-6">داشبورد تحلیلی زرین‌پال</h1>
        <p className="mb-8">درباره ما</p>
        <div className="mb-4">
          <Link 
            href="/dashboard" 
            className="text-blue-500 hover:text-blue-700 underline text-xl"
          >
            ورود به داشبورد تحلیلی
          </Link>
        </div>
      </div>
    </main>
  );
}
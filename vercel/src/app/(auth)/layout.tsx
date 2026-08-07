import { BarChart3 } from "lucide-react";
import Link from "next/link";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen grid grid-cols-1 md:grid-cols-2">
      <div className="flex items-center justify-center p-8">
        <div className="w-full max-w-sm space-y-6">
          <div className="flex items-center justify-center gap-2 mb-8">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground group-hover:bg-primary/90 transition-colors">
                <BarChart3 className="h-5 w-5" />
              </div>
              <span className="text-xl font-semibold tracking-tight">Skylark BI</span>
            </Link>
          </div>
          {children}
        </div>
      </div>
      <div className="hidden md:flex flex-col justify-center bg-muted/30 p-12 lg:p-24 border-l">
        <div className="max-w-md">
          <div className="inline-flex items-center justify-center rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary mb-6">
            Enterprise Intelligence
          </div>
          <h2 className="text-3xl font-bold tracking-tight mb-4">
            Transform your monday.com data into actionable insights.
          </h2>
          <p className="text-muted-foreground text-lg">
            Join thousands of executives using Skylark BI to make faster, data-driven decisions without looking at a single dashboard.
          </p>
        </div>
      </div>
    </div>
  );
}

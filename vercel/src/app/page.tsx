import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, BarChart3, Lock, Zap, MessageSquare, Database, ShieldCheck } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-background selection:bg-primary/20">
      {/* Navbar */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <BarChart3 className="h-5 w-5" />
            </div>
            <span className="text-xl font-semibold tracking-tight">Skylark BI</span>
          </div>
          <nav className="hidden md:flex gap-6 text-sm font-medium text-muted-foreground">
            <Link href="#features" className="hover:text-foreground transition-colors">Features</Link>
            <Link href="#how-it-works" className="hover:text-foreground transition-colors">How It Works</Link>
            <Link href="#security" className="hover:text-foreground transition-colors">Security</Link>
          </nav>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm font-medium hover:text-foreground transition-colors">Login</Link>
            <Link href="/register">
              <Button size="sm" className="rounded-full px-4">Start Free</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden pt-32 pb-24 md:pt-48 md:pb-32">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background" />
          <div className="container relative mx-auto max-w-5xl px-4 text-center sm:px-6 lg:px-8">
            <h1 className="text-5xl font-bold tracking-tight sm:text-7xl mb-6">
              Ask Your Business <br className="hidden sm:block" />
              <span className="text-primary">Anything.</span>
            </h1>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground sm:text-xl mb-10 leading-relaxed">
              An AI Business Intelligence Agent that connects to monday.com and delivers executive insights in seconds. No dashboards, just answers.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/register">
                <Button size="lg" className="rounded-full h-14 px-8 text-base">
                  Start Free <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="#demo">
                <Button size="lg" variant="outline" className="rounded-full h-14 px-8 text-base bg-background/50 backdrop-blur-sm">
                  View Demo
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-24 bg-muted/30">
          <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mb-16 text-center">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Intelligence at scale</h2>
              <p className="mt-4 text-lg text-muted-foreground">Everything you need to understand your business.</p>
            </div>
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {[
                { title: "Conversational Analytics", desc: "Chat naturally with your data.", icon: MessageSquare },
                { title: "Live monday.com Data", desc: "Real-time sync with your boards.", icon: Database },
                { title: "AI Insights", desc: "Proactive bottleneck detection.", icon: Zap },
                { title: "Confidence Scores", desc: "Transparent data quality metrics.", icon: ShieldCheck },
                { title: "Executive Reports", desc: "Instant summaries for leadership.", icon: BarChart3 },
                { title: "Secure by Design", desc: "Enterprise-grade data protection.", icon: Lock },
              ].map((feature, i) => (
                <div key={i} className="group relative rounded-3xl border bg-card p-8 shadow-sm transition-all hover:shadow-md hover:border-primary/20">
                  <div className="mb-6 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary group-hover:scale-110 transition-transform">
                    <feature.icon className="h-6 w-6" />
                  </div>
                  <h3 className="mb-3 text-xl font-semibold">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t py-12 md:py-16">
        <div className="container mx-auto flex flex-col items-center justify-between gap-6 px-4 md:flex-row max-w-7xl sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary" />
            <span className="text-lg font-semibold tracking-tight">Skylark BI</span>
          </div>
          <p className="text-sm text-muted-foreground">© 2026 Skylark BI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

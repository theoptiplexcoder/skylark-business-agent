"use client";

import { useAppStore } from "@/lib/store";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Database, Key, LayoutTemplate, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function DashboardPage() {
  const { workspace } = useAppStore();

  return (
    <div className="flex-1 overflow-auto p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Dashboard</h1>
          <p className="text-muted-foreground">
            Overview of your {workspace?.name || "Workspace"} connection and usage.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Connected Boards</CardTitle>
              <LayoutTemplate className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{workspace?.connectedBoards || 0}</div>
              <p className="text-xs text-muted-foreground">+1 this week</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Data Rows Syncing</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">14,231</div>
              <p className="text-xs text-muted-foreground">Updated 2 mins ago</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">8</div>
              <p className="text-xs text-muted-foreground">Across 3 teams</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">API Status</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-500">Healthy</div>
              <p className="text-xs text-muted-foreground">99.9% uptime</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Card className="col-span-1">
            <CardHeader>
              <CardTitle>Recent Insights</CardTitle>
              <CardDescription>
                AI-generated summaries from your boards.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-lg border p-3 text-sm">
                <span className="font-semibold text-primary">Sales Pipeline:</span> 3 deals in 'Negotiation' have been idle for &gt;14 days. Risk of churn increased by 15%.
              </div>
              <div className="rounded-lg border p-3 text-sm">
                <span className="font-semibold text-primary">Marketing ROI:</span> Q3 campaign spend is 20% under budget while yielding a 5% higher conversion rate than Q2.
              </div>
              <Link href="/chat" className="block pt-2">
                <Button variant="outline" className="w-full">Ask follow-up questions</Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="col-span-1">
            <CardHeader>
              <CardTitle>Connection Status</CardTitle>
              <CardDescription>
                Manage your monday.com integration.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="h-10 w-10 rounded-full bg-emerald-100 flex items-center justify-center">
                    <Key className="h-5 w-5 text-emerald-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium leading-none">monday.com API Key</p>
                    <p className="text-sm text-muted-foreground mt-1">Valid and connected</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">Rotate</Button>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="h-10 w-10 rounded-full bg-emerald-100 flex items-center justify-center">
                    <Database className="h-5 w-5 text-emerald-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium leading-none">Webhook Webhooks</p>
                    <p className="text-sm text-muted-foreground mt-1">Receiving live updates</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">View Logs</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

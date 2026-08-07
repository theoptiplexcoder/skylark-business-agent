"use client";

import { useAppStore } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useTheme } from "next-themes";

export default function SettingsPage() {
  const { user, workspace } = useAppStore();
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex-1 overflow-auto p-8">
      <div className="max-w-3xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Settings</h1>
          <p className="text-muted-foreground">
            Manage your account, workspace, and integration settings.
          </p>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Profile</CardTitle>
              <CardDescription>
                Update your personal information.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input id="name" defaultValue={user?.name || "Executive User"} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" defaultValue={user?.email || "user@acme.com"} disabled />
                <p className="text-[0.8rem] text-muted-foreground">Your email is tied to your account and cannot be changed here.</p>
              </div>
            </CardContent>
            <CardFooter className="border-t px-6 py-4">
              <Button>Save Changes</Button>
            </CardFooter>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Appearance</CardTitle>
              <CardDescription>
                Customize how Skylark BI looks on your device.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-4">
                <Button 
                  variant={theme === "light" ? "default" : "outline"}
                  onClick={() => setTheme("light")}
                >
                  Light
                </Button>
                <Button 
                  variant={theme === "dark" ? "default" : "outline"}
                  onClick={() => setTheme("dark")}
                >
                  Dark
                </Button>
                <Button 
                  variant={theme === "system" ? "default" : "outline"}
                  onClick={() => setTheme("system")}
                >
                  System
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>monday.com Integration</CardTitle>
              <CardDescription>
                Configure your API key and workspace connection.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="workspace">Workspace Name</Label>
                <Input id="workspace" defaultValue={workspace?.name || "Acme Corp"} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="apikey">API Key</Label>
                <Input id="apikey" type="password" defaultValue="*************************" />
                <p className="text-[0.8rem] text-muted-foreground">Requires 'boards:read', 'users:read', and 'workspaces:read' scopes.</p>
              </div>
            </CardContent>
            <CardFooter className="border-t px-6 py-4 flex justify-between">
              <Button variant="outline">Test Connection</Button>
              <Button>Save Configuration</Button>
            </CardFooter>
          </Card>

          <Card className="border-destructive/50">
            <CardHeader>
              <CardTitle className="text-destructive">Danger Zone</CardTitle>
              <CardDescription>
                Irreversible actions for your account.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center p-4 border rounded-lg border-destructive/20 bg-destructive/5">
                <div>
                  <h4 className="font-semibold text-sm">Delete Workspace</h4>
                  <p className="text-sm text-muted-foreground">Remove all data, connections, and insights.</p>
                </div>
                <Button variant="destructive">Delete Workspace</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

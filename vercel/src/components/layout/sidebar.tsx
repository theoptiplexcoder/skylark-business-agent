"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  BarChart3, 
  MessageSquare, 
  Settings, 
  LayoutDashboard, 
  Plus, 
  ChevronLeft,
  ChevronRight,
  LogOut,
  Search,
  Pin
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Settings", href: "/settings", icon: Settings },
];

const recentChats = [
  { id: 1, title: "Q3 Revenue Analysis", pinned: true },
  { id: 2, title: "Marketing Spend vs ROI", pinned: false },
  { id: 3, title: "Sales Pipeline Bottlenecks", pinned: false },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isSidebarOpen, toggleSidebar, user } = useAppStore();

  return (
    <div
      className={cn(
        "relative flex flex-col border-r bg-muted/10 transition-all duration-300",
        isSidebarOpen ? "w-72" : "w-[72px]"
      )}
    >
      <div className="flex h-16 items-center justify-between px-4 py-4 border-b">
        <div className={cn("flex items-center gap-2 overflow-hidden transition-all", isSidebarOpen ? "w-auto opacity-100" : "w-0 opacity-0")}>
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <BarChart3 className="h-5 w-5" />
          </div>
          <span className="text-lg font-semibold truncate">Skylark BI</span>
        </div>
        <Button variant="ghost" size="icon" onClick={toggleSidebar} className="shrink-0">
          {isSidebarOpen ? <ChevronLeft className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
        </Button>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col gap-2 p-3">
        <Link href="/chat">
          <Button variant="default" className={cn("w-full justify-start shadow-sm", !isSidebarOpen && "px-2 justify-center")}>
            <Plus className={cn("h-4 w-4", isSidebarOpen && "mr-2")} />
            {isSidebarOpen && "New Chat"}
          </Button>
        </Link>

        {isSidebarOpen && (
          <div className="mt-4 px-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search history..."
                className="w-full rounded-md border border-input bg-background py-2 pl-9 pr-3 text-sm outline-none placeholder:text-muted-foreground focus:ring-1 focus:ring-ring"
              />
            </div>
          </div>
        )}

        <ScrollArea className="flex-1 mt-4 -mx-1 px-1">
          <div className="space-y-6">
            <div className="space-y-1">
              {navItems.map((item) => {
                const isActive = pathname.startsWith(item.href);
                return (
                  <Link key={item.name} href={item.href}>
                    <Button
                      variant={isActive ? "secondary" : "ghost"}
                      className={cn(
                        "w-full justify-start",
                        isActive ? "bg-secondary text-secondary-foreground" : "text-muted-foreground",
                        !isSidebarOpen && "px-2 justify-center"
                      )}
                    >
                      <item.icon className={cn("h-4 w-4 shrink-0", isSidebarOpen && "mr-3")} />
                      {isSidebarOpen && <span className="truncate">{item.name}</span>}
                    </Button>
                  </Link>
                );
              })}
            </div>

            {isSidebarOpen && (
              <div className="space-y-1">
                <h4 className="px-3 text-xs font-semibold uppercase text-muted-foreground tracking-wider mb-2">
                  Recent Chats
                </h4>
                {recentChats.map((chat) => (
                  <Link key={chat.id} href={`/chat/${chat.id}`}>
                    <Button variant="ghost" className="w-full justify-start text-muted-foreground font-normal overflow-hidden h-9 px-3">
                      {chat.pinned ? (
                        <Pin className="h-3.5 w-3.5 mr-2 shrink-0 text-primary" />
                      ) : (
                        <MessageSquare className="h-3.5 w-3.5 mr-2 shrink-0 opacity-50" />
                      )}
                      <span className="truncate text-sm">{chat.title}</span>
                    </Button>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      <div className="border-t p-3">
        <div className={cn("flex items-center", isSidebarOpen ? "justify-between" : "justify-center")}>
          <div className={cn("flex items-center gap-3 overflow-hidden", isSidebarOpen ? "opacity-100" : "opacity-0 hidden")}>
            <Avatar className="h-9 w-9 border">
              <AvatarImage src="" />
              <AvatarFallback className="bg-primary/10 text-primary font-medium">
                {user?.name?.substring(0, 2).toUpperCase() || "EX"}
              </AvatarFallback>
            </Avatar>
            <div className="flex flex-col overflow-hidden">
              <span className="text-sm font-medium truncate">{user?.name || "Executive User"}</span>
              <span className="text-xs text-muted-foreground truncate">{user?.email || "user@acme.com"}</span>
            </div>
          </div>
          <Link href="/login">
            <Button variant="ghost" size="icon" className="shrink-0 text-muted-foreground hover:text-foreground">
              <LogOut className="h-5 w-5" />
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}

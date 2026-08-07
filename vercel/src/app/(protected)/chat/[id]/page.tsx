"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Send,
  Bot,
  User,
  Sparkles,
  Filter,
  ChevronRight,
  AlertTriangle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  ResponsiveContainer,
} from "recharts";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  charts?: any[];
  insights?: string[];
  recommendations?: string[];
  warnings?: string[];
  confidence?: number;
  execution_time?: number;
}

const COLORS = [
  "#4f46e5",
  "#06b6d4",
  "#22c55e",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#ec4899",
  "#14b8a6",
];

function ChartRenderer({ chart }: { chart: any }) {
  if (chart.type === "kpi") {
    return (
      <div className="grid grid-cols-3 md:grid-cols-6 gap-3 mt-4">
        {chart.data.items.map((item: any, i: number) => (
          <div
            key={i}
            className="bg-card border rounded-xl p-3 text-center shadow-sm"
          >
            <div
              className="text-xl font-bold"
              style={{ color: item.color }}
            >
              {item.value}
            </div>
            <div className="text-[11px] text-muted-foreground uppercase tracking-wide mt-1">
              {item.label}
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (chart.type === "bar") {
    return (
      <Card className="mt-3 shadow-none">
        <CardHeader className="py-2 px-4">
          <CardTitle className="text-xs font-semibold text-muted-foreground uppercase">
            {chart.title}
          </CardTitle>
        </CardHeader>
        <CardContent className="px-4 pb-4">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart
              data={chart.data.labels.map((l: string, i: number) => ({
                name: l,
                value: chart.data.datasets[0].data[i],
              }))}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 11, fill: "#94a3b8" }}
              />
              <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} />
              <Tooltip
                contentStyle={{
                  background: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <Bar
                dataKey="value"
                fill={chart.data.datasets[0].backgroundColor || "#4f46e5"}
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    );
  }

  if (chart.type === "pie" || chart.type === "doughnut") {
    const data = chart.data.labels.map((l: string, i: number) => ({
      name: l,
      value: chart.data.datasets[0].data[i],
    }));
    return (
      <Card className="mt-3 shadow-none">
        <CardHeader className="py-2 px-4">
          <CardTitle className="text-xs font-semibold text-muted-foreground uppercase">
            {chart.title}
          </CardTitle>
        </CardHeader>
        <CardContent className="px-4 pb-4">
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={chart.type === "doughnut" ? 60 : 0}
                outerRadius={90}
                paddingAngle={3}
                dataKey="value"
                label={({ name, percent }) =>
                  `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
                }
                labelLine={false}
              >
                {data.map((_: any, i: number) => (
                  <Cell
                    key={i}
                    fill={
                      chart.data.datasets[0].backgroundColor?.[i] ||
                      COLORS[i % COLORS.length]
                    }
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    );
  }

  if (chart.type === "line") {
    const data = chart.data.labels.map((l: string, i: number) => ({
      name: l,
      value: chart.data.datasets[0].data[i],
    }));
    return (
      <Card className="mt-3 shadow-none">
        <CardHeader className="py-2 px-4">
          <CardTitle className="text-xs font-semibold text-muted-foreground uppercase">
            {chart.title}
          </CardTitle>
        </CardHeader>
        <CardContent className="px-4 pb-4">
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 11, fill: "#94a3b8" }}
              />
              <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} />
              <Tooltip
                contentStyle={{
                  background: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#4f46e5"
                strokeWidth={2}
                dot={{ fill: "#4f46e5", r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    );
  }

  return null;
}

export default function ChatConversationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isRightPanelOpen, setIsRightPanelOpen] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [conversationId, setConversationId] = useState<string>("");

  useEffect(() => {
    params.then((p) => setConversationId(p.id));
  }, [params]);

  const suggestedPrompts = [
    "How is our sales pipeline?",
    "Which sector is underperforming?",
    "Revenue this quarter",
    "Deals closing this month",
  ];

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    try {
      const res = await fetch(`${API_URL}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.content }),
      });
      const data = await res.json();

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer || "No answer received.",
        charts: data.charts || [],
        insights: data.insights || [],
        recommendations: data.recommendations || [],
        warnings: data.warnings || [],
        confidence: data.confidence,
        execution_time: data.execution_time,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Error connecting to backend: ${err.message}. Make sure the API server is running on ${API_URL}.`,
      };
      setMessages((prev) => [...prev, errMsg]);
    }
    setIsTyping(false);
  };

  return (
    <div className="flex h-full overflow-hidden">
      <div className="flex-1 flex flex-col min-w-0 bg-background relative h-full">
        {/* Scrollable messages area */}
        <div className="flex-1 overflow-y-auto min-h-0">
          {messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center max-w-3xl mx-auto w-full min-h-full">
              <div className="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center mb-6">
                <Sparkles className="h-8 w-8 text-primary" />
              </div>
              <h2 className="text-3xl font-bold mb-3">
                Conversation {conversationId}
              </h2>
              <p className="text-muted-foreground mb-10 max-w-md">
                Ask any question about your business data. I&apos;m connected to
                your monday.com workspace in real-time.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full">
                {suggestedPrompts.map((prompt, i) => (
                  <Button
                    key={i}
                    variant="outline"
                    className="justify-start h-auto py-3 px-4 rounded-xl text-left font-normal bg-card hover:border-primary/50"
                    onClick={() => setInput(prompt)}
                  >
                    {prompt}
                  </Button>
                ))}
              </div>
            </div>
          ) : (
            <div ref={scrollRef} className="max-w-3xl mx-auto space-y-8 p-4 md:p-8 pb-4">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={cn(
                    "flex gap-4",
                    msg.role === "user" ? "justify-end" : "justify-start"
                  )}
                >
                  {msg.role === "assistant" && (
                    <div className="h-8 w-8 shrink-0 rounded-md bg-primary/10 flex items-center justify-center">
                      <Bot className="h-5 w-5 text-primary" />
                    </div>
                  )}

                  <div
                    className={cn(
                      "rounded-2xl px-5 py-3.5 max-w-[85%] text-[15px] leading-relaxed shadow-sm",
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground rounded-tr-sm"
                        : "bg-card border rounded-tl-sm"
                    )}
                  >
                    <div className="whitespace-pre-wrap">{msg.content}</div>

                    {msg.insights && msg.insights.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-border/50">
                        <div className="text-xs font-semibold uppercase text-muted-foreground mb-1">
                          Insights
                        </div>
                        <ul className="list-disc list-inside text-sm space-y-1">
                          {msg.insights.map((ins, i) => (
                            <li key={i}>{ins}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {msg.recommendations && msg.recommendations.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-border/50">
                        <div className="text-xs font-semibold uppercase text-muted-foreground mb-1">
                          Recommendations
                        </div>
                        <ul className="list-disc list-inside text-sm space-y-1">
                          {msg.recommendations.map((rec, i) => (
                            <li key={i}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {msg.warnings && msg.warnings.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-border/50">
                        <div className="text-xs font-semibold uppercase text-amber-500 mb-1 flex items-center gap-1">
                          <AlertTriangle className="h-3 w-3" /> Warnings
                        </div>
                        <ul className="list-disc list-inside text-sm space-y-1 text-amber-600">
                          {msg.warnings.map((w, i) => (
                            <li key={i}>{w}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {msg.charts && msg.charts.length > 0 && (
                      <div className="mt-4 pt-3 border-t border-border/50">
                        {msg.charts.map((chart: any, i: number) => (
                          <ChartRenderer key={i} chart={chart} />
                        ))}
                      </div>
                    )}

                    {msg.confidence !== undefined && (
                      <div className="mt-3 pt-3 border-t border-border/50 flex items-center gap-4 text-xs text-muted-foreground">
                        <span>
                          Confidence: {(msg.confidence * 100).toFixed(0)}%
                        </span>
                        {msg.execution_time !== undefined && (
                          <span>Time: {msg.execution_time}s</span>
                        )}
                      </div>
                    )}
                  </div>

                  {msg.role === "user" && (
                    <div className="h-8 w-8 shrink-0 rounded-md bg-secondary flex items-center justify-center">
                      <User className="h-5 w-5 text-secondary-foreground" />
                    </div>
                  )}
                </div>
              ))}
              {isTyping && (
                <div className="flex gap-4 justify-start">
                  <div className="h-8 w-8 shrink-0 rounded-md bg-primary/10 flex items-center justify-center">
                    <Bot className="h-5 w-5 text-primary" />
                  </div>
                  <div className="bg-card border rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm flex gap-1 items-center">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary/40 animate-bounce" />
                    <div className="w-1.5 h-1.5 rounded-full bg-primary/40 animate-bounce [animation-delay:0.2s]" />
                    <div className="w-1.5 h-1.5 rounded-full bg-primary/40 animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Sticky input at bottom */}
        <div className="shrink-0 p-4 bg-background border-t sticky bottom-0 z-10">
          <div className="max-w-3xl mx-auto relative flex items-end gap-2">
            <div className="relative flex-1 bg-card rounded-2xl border shadow-sm focus-within:ring-1 focus-within:ring-ring focus-within:border-primary transition-all">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Ask your business anything..."
                className="border-0 bg-transparent focus-visible:ring-0 rounded-2xl py-6 pl-4 pr-12 shadow-none"
              />
              <div className="absolute right-2 top-1/2 -translate-y-1/2">
                <Button
                  size="icon"
                  className="rounded-xl h-8 w-8"
                  onClick={handleSend}
                  disabled={!input.trim() || isTyping}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
          <div className="text-center mt-2 text-xs text-muted-foreground">
            Skylark BI may produce inaccurate information about boards, people,
            or facts.
          </div>
        </div>
      </div>

      <div
        className={cn(
          "border-l bg-muted/10 flex flex-col transition-all duration-300",
          isRightPanelOpen ? "w-80" : "w-0 hidden md:flex md:w-12 items-center"
        )}
      >
        {isRightPanelOpen ? (
          <>
            <div className="flex h-16 items-center justify-between px-4 border-b">
              <span className="font-semibold flex items-center gap-2">
                <Filter className="h-4 w-4" /> Active Context
              </span>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsRightPanelOpen(false)}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-6">
                <Card className="shadow-none bg-background/50 border-dashed">
                  <CardHeader className="py-3 px-4">
                    <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Data Quality
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <div className="flex items-center gap-3 text-sm">
                      <div className="flex-1 bg-secondary rounded-full h-2">
                        <div className="bg-emerald-500 h-2 rounded-full w-[92%]" />
                      </div>
                      <span className="font-medium">92%</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-2 flex gap-1 items-start">
                      <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-amber-500" />
                      3 columns have missing critical data.
                    </p>
                  </CardContent>
                </Card>

                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3 px-1">
                    Connected Boards
                  </h4>
                  <div className="space-y-2">
                    {["Work Order", "Deals"].map((board) => (
                      <div
                        key={board}
                        className="flex items-center gap-2 text-sm bg-card border rounded-lg px-3 py-2 shadow-sm"
                      >
                        <div className="h-2 w-2 rounded-full bg-emerald-500" />
                        <span className="truncate">{board}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </ScrollArea>
          </>
        ) : (
          <div className="pt-4 h-full flex flex-col items-center">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsRightPanelOpen(true)}
            >
              <Filter className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

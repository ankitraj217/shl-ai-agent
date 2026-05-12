import { useEffect, useRef, useState } from "react";
import { ChatInput , ChatMessage ,EmptyState , Header , RecommendationList } from "../components";
import { sendChatMessage } from "../services/chatApi";
import type { ChatMessage as ChatMessageType, Recommendation } from "../types/chat";

export function RecruiterAssistantPage() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollAnchorRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isLoading]);

  async function handleSend(content: string) {
    const nextMessages: ChatMessageType[] = [...messages, { role: "user", content }];
    setMessages(nextMessages);
    setError(null);
    setIsLoading(true);

    try {
      const response = await sendChatMessage({ messages: nextMessages });
      const assistantMessage: ChatMessageType = {
        role: "assistant",
        content: response.reply,
      };
      setMessages([...nextMessages, assistantMessage]);
      setRecommendations(response.recommendations);
    } catch (caught) {
      setMessages(messages);
      setError(caught instanceof Error ? caught.message : "Something went wrong.");
    } finally {
      setIsLoading(false);
    }
  }

  function clearConversation() {
    if (isLoading) {
      return;
    }
    setMessages([]);
    setRecommendations([]);
    setError(null);
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950">
      <Header />

      <main className="mx-auto grid max-w-7xl gap-5 px-4 py-5 sm:px-6 lg:grid-cols-[minmax(0,1fr)_400px] lg:px-8">
        <section className="flex min-h-[720px] flex-col rounded-2xl border border-slate-200 bg-white shadow-soft">
          <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
            <div>
              <h2 className="text-sm font-semibold text-slate-950">Assessment conversation</h2>
              <p className="mt-1 text-xs text-slate-500">
                Ask for recommendations, refinements, or catalog-grounded comparisons.
              </p>
            </div>
            <button
              type="button"
              onClick={clearConversation}
              disabled={isLoading || messages.length === 0}
              className="rounded-xl border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 focus:outline-none focus:ring-4 focus:ring-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Clear
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-4 py-5 sm:px-5">
            {messages.length === 0 ? (
              <EmptyState />
            ) : (
              <div className="space-y-4">
                {messages.map((message, index) => (
                  <ChatMessage key={`${message.role}-${index}`} message={message} />
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600 shadow-sm">
                      Reviewing the SHL catalog...
                    </div>
                  </div>
                )}
                <div ref={scrollAnchorRef} />
              </div>
            )}
          </div>

          {error && (
            <div className="mx-5 mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error} Check that the FastAPI backend is running on http://127.0.0.1:8080.
            </div>
          )}

          <ChatInput disabled={isLoading} onSubmit={handleSend} />
        </section>

        <RecommendationList recommendations={recommendations} />
      </main>
    </div>
  );
}

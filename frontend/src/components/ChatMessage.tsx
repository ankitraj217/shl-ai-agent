import type { ChatMessage as ChatMessageType } from "../types/chat";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <article
        className={`max-w-[88%] rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm sm:max-w-[76%] ${
          isUser
            ? "bg-slate-950 text-white"
            : "border border-slate-200 bg-slate-100 text-slate-800"
        }`}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
      </article>
    </div>
  );
}

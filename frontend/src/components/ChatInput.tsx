import { KeyboardEvent, useState } from "react";

interface ChatInputProps {
  disabled: boolean;
  onSubmit: (message: string) => void;
}

export function ChatInput({ disabled, onSubmit }: ChatInputProps) {
  const [value, setValue] = useState("");

  function submitMessage() {
    const trimmed = value.trim();
    if (!trimmed || disabled) {
      return;
    }
    onSubmit(trimmed);
    setValue("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submitMessage();
    }
  }

  return (
    <div className="border-t border-slate-200 bg-white p-4 sm:p-5">
      <label htmlFor="chat-input" className="sr-only">
        Message
      </label>
      <div className="flex flex-col gap-3 sm:flex-row">
        <textarea
          id="chat-input"
          value={value}
          disabled={disabled}
          rows={2}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe the role, seniority, skills, or assessment constraints..."
          className="min-h-14 flex-1 resize-none rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm outline-none placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-slate-50"
        />
        <button
          type="button"
          disabled={disabled || value.trim().length === 0}
          onClick={submitMessage}
          className="inline-flex min-h-14 items-center justify-center rounded-xl bg-blue-700 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-800 focus:outline-none focus:ring-4 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {disabled ? "Working..." : "Send"}
        </button>
      </div>
      <p className="mt-2 text-xs text-slate-500">Press Enter to send. Use Shift+Enter for a new line.</p>
    </div>
  );
}

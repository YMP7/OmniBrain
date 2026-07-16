import { ArrowRight, CircleNotch } from "@phosphor-icons/react";
import { useState } from "react";

interface QueryPanelProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

export function QueryPanel({ onSubmit, isLoading }: QueryPanelProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query.trim());
      setQuery("");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="sticky bottom-6 z-10 mx-auto w-full max-w-3xl">
      <div className="relative flex items-center shadow-2xl">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask OmniBrain..."
          disabled={isLoading}
          className="glass-input w-full py-4 pl-6 pr-14 text-base text-zinc-100 placeholder-zinc-500 shadow-xl"
        />
        <button
          type="submit"
          disabled={!query.trim() || isLoading}
          className="absolute right-2 p-2 bg-white text-zinc-950 rounded-lg hover:bg-zinc-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <CircleNotch size={20} className="animate-spin" />
          ) : (
            <ArrowRight size={20} weight="bold" />
          )}
        </button>
      </div>
    </form>
  );
}

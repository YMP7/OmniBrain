import { useState } from "react";
import { IngestionPanel } from "./components/IngestionPanel";
import { QueryPanel } from "./components/QueryPanel";
import { FindingsDisplay } from "./components/FindingsDisplay";
import { Brain } from "@phosphor-icons/react";

interface QueryResult {
  answer: string | null;
  findings: string | null;
  citations: string | null;
}

export default function App() {
  const [isQuerying, setIsQuerying] = useState(false);
  const [result, setResult] = useState<QueryResult>({
    answer: null,
    findings: null,
    citations: null,
  });
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleQuery = async (query: string) => {
    setIsQuerying(true);
    setError(null);
    setResult({ answer: null, findings: null, citations: null });

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`Query failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResult({
        answer: data.answer || null,
        findings: data.findings || null,
        citations: data.citations || null,
      });
    } catch (err: any) {
      setError(err.message || "An error occurred during querying.");
    } finally {
      setIsQuerying(false);
    }
  };

  return (
    <div className="min-h-100dvh flex flex-col bg-zinc-950 text-zinc-100 font-sans antialiased">
      {/* Header */}
      <header className="sticky top-0 z-20 w-full bg-zinc-950/80 backdrop-blur-md border-b border-zinc-900 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain size={28} weight="duotone" className="text-violet-400" />
            <span className="font-semibold text-lg tracking-tight">OmniBrain</span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-5xl mx-auto px-6 py-12 flex flex-col gap-12 relative">
        {/* Error State */}
        {error && (
          <div className="p-4 bg-red-950/30 border border-red-900/50 rounded-xl text-red-200 text-sm">
            {error}
          </div>
        )}
        
        {/* Upload Success State */}
        {uploadMessage && !error && (
          <div className="p-4 bg-emerald-950/30 border border-emerald-900/50 rounded-xl text-emerald-200 text-sm">
            {uploadMessage}
          </div>
        )}

        {/* Ingestion Section */}
        <section>
          <IngestionPanel
            onUploadStart={() => {
              setError(null);
              setUploadMessage(null);
            }}
            onUploadComplete={(res) => setUploadMessage(res.message || "File uploaded successfully.")}
            onUploadError={(err) => setError(err)}
          />
        </section>

        {/* Findings Section */}
        <section className="flex-1 pb-32">
          <FindingsDisplay
            answer={result.answer}
            findings={result.findings}
            citations={result.citations}
          />
        </section>
      </main>

      {/* Sticky Footer / Query Panel */}
      <div className="fixed bottom-0 left-0 w-full p-6 bg-linear-to-t from-zinc-950 via-zinc-950/90 to-transparent pointer-events-none z-30">
        <div className="max-w-3xl mx-auto pointer-events-auto">
          <QueryPanel onSubmit={handleQuery} isLoading={isQuerying} />
        </div>
      </div>
    </div>
  );
}

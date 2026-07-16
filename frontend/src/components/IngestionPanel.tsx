import { UploadSimple, FileArrowUp } from "@phosphor-icons/react";
import { useState } from "react";

interface IngestionPanelProps {
  onUploadStart: () => void;
  onUploadComplete: (result: { message: string; filename: string }) => void;
  onUploadError: (error: string) => void;
}

export function IngestionPanel({ onUploadStart, onUploadComplete, onUploadError }: IngestionPanelProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [currentFile, setCurrentFile] = useState<string | null>(null);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    onUploadStart();
    setCurrentFile(file.name);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      onUploadComplete(data);
    } catch (err: any) {
      onUploadError(err.message || "An error occurred during upload");
      setCurrentFile(null);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="bento-card p-6 flex flex-col gap-4">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-zinc-800 rounded-lg">
          <UploadSimple size={24} className="text-zinc-300" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-zinc-100 tracking-tight">Ingest Documents</h2>
          <p className="text-sm text-zinc-400">Upload PDFs to OmniBrain's knowledge base.</p>
        </div>
      </div>

      <label
        className={`mt-2 flex flex-col items-center justify-center h-32 border border-dashed rounded-xl cursor-pointer transition-colors duration-200 ${
          isDragging
            ? "border-violet-400 bg-violet-400/5"
            : "border-zinc-700 bg-zinc-950/50 hover:bg-zinc-800/30 hover:border-zinc-500"
        } ${isUploading ? "opacity-50 pointer-events-none" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          const file = e.dataTransfer.files?.[0];
          if (file) handleUpload(file);
        }}
      >
        <FileArrowUp size={32} className={isDragging ? "text-violet-400 mb-2" : "text-zinc-500 mb-2"} />
        <span className="text-sm text-zinc-300 font-medium">
          {isUploading ? "Uploading..." : currentFile ? currentFile : "Drag & drop a PDF or click to browse"}
        </span>
        <input
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleUpload(file);
          }}
          disabled={isUploading}
        />
      </label>
    </div>
  );
}

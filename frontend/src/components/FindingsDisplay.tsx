import { motion, useReducedMotion } from "motion/react";
import { Info, Database, ListChecks } from "@phosphor-icons/react";

interface FindingsDisplayProps {
  answer: string | null;
  findings: string | null;
  citations: string | null;
}

export function FindingsDisplay({ answer, findings, citations }: FindingsDisplayProps) {
  const reduce = useReducedMotion();

  if (!answer && !findings && !citations) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      {/* Primary Answer Card */}
      {answer && (
        <motion.div
          initial={reduce ? false : { opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
          className="bento-card col-span-1 md:col-span-3 p-8 flex flex-col gap-4"
        >
          <div className="flex items-center gap-2 mb-2">
            <Info size={20} className="text-zinc-500" />
            <h3 className="text-xs font-mono uppercase tracking-widest text-zinc-500">Synthesis</h3>
          </div>
          <div className="prose prose-invert prose-zinc max-w-none prose-p:leading-relaxed">
            {/* Since it's markdown-like, we could use a markdown parser, but for now we render as text or split by lines */}
            {answer.split('\n').map((line, i) => (
              <p key={i} className="text-zinc-200 text-lg mb-4">{line}</p>
            ))}
          </div>
        </motion.div>
      )}

      {/* Findings Card */}
      {findings && (
        <motion.div
          initial={reduce ? false : { opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1, ease: [0.23, 1, 0.32, 1] }}
          className="bento-card col-span-1 md:col-span-2 p-6 flex flex-col gap-4"
        >
          <div className="flex items-center gap-2 mb-2">
            <Database size={20} className="text-zinc-500" />
            <h3 className="text-xs font-mono uppercase tracking-widest text-zinc-500">Raw Findings</h3>
          </div>
          <div className="text-sm text-zinc-400 whitespace-pre-wrap leading-relaxed">
            {findings}
          </div>
        </motion.div>
      )}

      {/* Citations Card */}
      {citations && (
        <motion.div
          initial={reduce ? false : { opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2, ease: [0.23, 1, 0.32, 1] }}
          className="bento-card col-span-1 p-6 flex flex-col gap-4 bg-zinc-950/50"
        >
          <div className="flex items-center gap-2 mb-2">
            <ListChecks size={20} className="text-zinc-500" />
            <h3 className="text-xs font-mono uppercase tracking-widest text-zinc-500">Citations</h3>
          </div>
          <div className="text-sm text-zinc-400 whitespace-pre-wrap leading-relaxed">
            {citations}
          </div>
        </motion.div>
      )}
    </div>
  );
}

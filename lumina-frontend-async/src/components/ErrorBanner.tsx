import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, ChevronDown, ChevronUp, X, RotateCcw, XCircle } from 'lucide-react';
import { colors, typography } from '../styles/designTokens';
import { useAppStore } from '../store/useAppStore';

/**
 * Error Banner Component
 *
 * Displays errors from either a failed query or a failed data extraction.
 */
export const ErrorBanner: React.FC = () => {
  // 1. Get ALL relevant state from the store
  const { error, clearError, extractedData, confirmAndExtract } = useAppStore();
  const [isExpanded, setIsExpanded] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);

  const hasExtractionErrors = extractedData?.metadata.errors && extractedData.metadata.errors.length > 0;

  // If there are no errors of any kind, render nothing.
  if (!error && !hasExtractionErrors) {
    return null;
  }

  // --- RENDER QUERY ERROR ---
  // If a general query error exists, show the simple banner. This takes priority.
  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-20 max-w-6xl mx-auto px-4 py-4"
      >
        <div
          className="flex items-center justify-between gap-4 p-4 rounded-lg border bg-red-900/40 border-red-500/50"
          role="alert"
        >
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <p className="text-sm text-red-200">
              <strong className="font-medium text-red-100">Oops!</strong> {error}
            </p>
          </div>
          <button onClick={clearError} className="p-1 rounded-full hover:bg-red-500/20 transition-colors flex-shrink-0">
            <XCircle className="w-5 h-5 text-red-300" />
          </button>
        </div>
      </motion.div>
    );
  }

  // --- RENDER EXTRACTION ERROR ---
  // If no query error, fall back to showing the detailed extraction error UI.
  const extractionErrors = extractedData.metadata.errors;
  const hasRecords = extractedData.records.length > 0;

  const handleRetry = async () => {
    setIsRetrying(true);
    try {
      await confirmAndExtract();
    } catch (err) {
      console.error('Retry failed:', err);
    } finally {
      setIsRetrying(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="relative z-20">
      <div className="mx-auto max-w-6xl px-4 py-4" style={{ backgroundColor: hasRecords ? `${colors.apollo.accent}15` : '#ff444415' }}>
        <div className="rounded-lg border p-4" style={{ backgroundColor: colors.midnight.light, borderColor: hasRecords ? `${colors.apollo.primary}40` : '#ff444440' }}>
          {/* Header */}
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3 flex-1">
              <AlertTriangle size={20} style={{ color: hasRecords ? colors.apollo.primary : '#ff4444' }} />
              <div>
                <p style={{ ...typography.label, color: colors.text.primary }}>
                  {hasRecords ? `Partial Extraction` : `Extraction Failed`}
                </p>
                <p style={{ fontSize: typography.sizes.bodySmall, color: colors.text.secondary }}>
                  {hasRecords ? `Some files had errors.` : 'No data was extracted.'}
                </p>
              </div>
            </div>
            {/* Actions */}
            <div className="flex items-center gap-2">
              <button onClick={handleRetry} disabled={isRetrying} className="flex items-center gap-2 px-3 py-1.5 rounded transition-all hover:opacity-80 disabled:opacity-50" style={{ backgroundColor: hasRecords ? colors.apollo.primary : '#ff4444', color: colors.midnight.deep }}>
                <RotateCcw size={14} className={isRetrying ? 'animate-spin' : ''} />
                {isRetrying ? 'Retrying...' : 'Retry'}
              </button>
              <button onClick={() => setIsExpanded(!isExpanded)} className="p-1.5 rounded hover:bg-white/10 transition-colors">
                {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </button>
            </div>
          </div>
          {/* Error Details (Expandable) */}
          <AnimatePresence>
            {isExpanded && (
              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                <div className="mt-4 pt-4 border-t" style={{ borderColor: `${colors.silver.warm}20` }}>
                  {extractionErrors.map((err, idx) => (
                    <div key={idx} className="p-3 mb-2 rounded" style={{ backgroundColor: `${colors.midnight.mid}80` }}>
                      <p style={{ ...typography.label, color: colors.text.primary }}>{err.filename}</p>
                      <p style={{ fontSize: typography.sizes.caption, color: colors.text.tertiary, fontFamily: 'monospace' }}>{err.error}</p>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
};
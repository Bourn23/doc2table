import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Send, Sparkles, ExternalLink, Download, Network, Loader2 } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { colors, typography, personalityModes } from '../styles/designTokens';
import { AppPhase } from '../types';
import { ErrorBanner } from '../components/ErrorBanner';
import ErrorBoundary from '../components/ErrorBoundary';
import { GraphVisualization } from '../components/GraphVisualization';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
// import API_BASE_URL from '../utils/api';

/**
 * ExplorationView - Hermes Mode
 * The main interface for querying and exploring data
 */
export const ExplorationView: React.FC = () => {
  const {
    submitQuery,
    currentResult,
    phase,
    extractedData,
    personalityMode,
    generateGraphFromQuery,
    isGeneratingGraph,
    graphData,
    currentJobService,
    jobStatus,
    jobMessage,
  } = useAppStore();
  const [queryInput, setQueryInput] = useState('');

  // --- DEBUGGING: Log state changes ---
  // This helps you see the exact data structures in the browser's developer console
  // whenever they are updated from the backend or your store.
  useEffect(() => {
    console.log('✅ [State Update] Current Result:', currentResult);
  }, [currentResult]);

  useEffect(() => {
    console.log('✅ [State Update] Extracted Data:', extractedData);
  }, [extractedData]);
  // ------------------------------------

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (queryInput.trim()) {
      submitQuery(queryInput.trim());
      setQueryInput('');
    }
  };

  const handleDownload = (filepath: string) => {
    // Extract filename from filepath
    const filename = filepath.split('/').pop() || filepath;

    // Create a simple relative URL
    // Nginx will catch this and proxy it to your backend
    const downloadUrl = `/download/${filename}`;

    // Open in new tab to trigger download
    window.open(downloadUrl, '_blank');
  };

  const isQuerying = phase === AppPhase.QUERYING;
  const isInsight = phase === AppPhase.INSIGHT;

  // Determine border colors based on personality mode
  const getBorderColors = () => {
    switch (personalityMode) {
      case 'apollo':
        return colors.apollo.primary;
      case 'hermes':
        return colors.hermes.cyan;
      default:
        return colors.silver.warm;
    }
  };

  const borderColor = getBorderColors();

  // Use real extracted data (fallback to empty array, not mock data)
  // const mockData = extractedData?.records || [];
  // const extractedData = useAppStore((state) => state.extractedData);
  const hasRecords = extractedData && extractedData.records.length > 0;

  // Filter this list to hide any columns you don't want the user to see.
  const visibleFields = (extractedData?.fields || []).filter(
    (field) => field.name !== 'id'
  );

  // const visibleFields = extractedData?.fields.map(f => ({ name: f })) || [];

  return (
    <div className="min-h-screen relative z-10 p-6">
      {/* Error Banner - Shows extraction errors with retry button */}
      <ErrorBanner />

      <div className="max-w-7xl mx-auto">

        {/* Dynamic Extraction Progress Indicator */}
        {currentJobService === 'dynamic_extraction' && jobStatus && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 rounded-lg border flex items-center gap-4"
            style={{
              backgroundColor: `${colors.apollo.primary}10`,
              borderColor: `${colors.apollo.primary}40`,
            }}
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            >
              <Loader2 className="w-5 h-5" style={{ color: colors.apollo.primary }} />
            </motion.div>
            <div className="flex-1">
              <p style={{
                fontSize: typography.sizes.bodySmall,
                color: colors.text.primary,
                fontWeight: typography.weights.medium,
                marginBottom: '4px',
              }}>
                {jobMessage || 'Extracting new column...'}
              </p>
              <p style={{
                fontSize: typography.sizes.caption,
                color: colors.text.tertiary,
              }}>
                Status: {jobStatus}
              </p>
            </div>
          </motion.div>
        )}

        {/* Query Interface */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <form onSubmit={handleSubmit}>
            <div
              className="flex items-center gap-3 px-6 py-4 rounded-xl border-2 transition-all"
              style={{
                backgroundColor: colors.midnight.light,
                borderColor: isQuerying
                  ? `${borderColor}80`
                  : `${borderColor}30`,
                boxShadow: isQuerying ? `0 0 20px ${borderColor}20` : 'none',
              }}
            >
              <Search
                className="w-5 h-5 flex-shrink-0"
                style={{
                  color: isQuerying ? borderColor : colors.text.secondary,
                }}
              />
              <input
                type="text"
                value={queryInput}
                onChange={(e) => setQueryInput(e.target.value)}
                placeholder="Ask Lumina anything about your data..."
                disabled={isQuerying}
                className="flex-1 bg-transparent outline-none"
                style={{
                  fontSize: typography.sizes.bodyLarge,
                  color: colors.text.primary,
                  fontWeight: typography.weights.light,
                }}
              />
              <button
                type="submit"
                disabled={!queryInput.trim() || isQuerying}
                className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105"
                style={{
                  backgroundColor: borderColor,
                  color: colors.midnight.deep,
                }}
              >
                {isQuerying ? (
                  <>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    >
                      <Sparkles className="w-4 h-4" />
                    </motion.div>
                    <span>Thinking...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Query</span>
                  </>
                )}
              </button>
            </div>
          </form>
        
          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="mt-1 flex items-center gap-1"
          >
            <span
              style={{
                fontSize: typography.sizes.caption,
                color: colors.text.tertiary,
              }}
            >
              Try asking:
            </span>
            {['Summarize column', 'Create a new column', 'Find correlations', 'Export as CSV'].map((query) => (
              <button
                key={query}
                onClick={() => setQueryInput(query)}
                className="px-3 py-1 rounded-full text-xs transition-all hover:scale-105"
                style={{
                  backgroundColor: `${colors.hermes.violet}20`,
                  color: colors.hermes.violet,
                  border: `1px solid ${colors.hermes.violet}30`,
                }}
              >
                {query}
              </button>
            ))}
          </motion.div>
        </motion.div>

        

        {/* Query Result (Insight Bloom or Function Result) */}
        {(isInsight || currentResult) && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            className="mb-8 p-6 rounded-xl border"
            style={{
              backgroundColor: isInsight
                ? `${colors.insight.bloom}10`
                : `${colors.midnight.light}80`,
              borderColor: isInsight
                ? `${colors.insight.bloom}40`
                : currentResult?.result_type === 'function'
                ? `${colors.apollo.primary}40`
                : `${colors.hermes.cyan}20`,
            }}
          >
            <div className="flex items-start gap-4">
              <div
                className="p-2 rounded-lg flex-shrink-0"
                style={{
                  backgroundColor: isInsight
                    ? `${colors.insight.bloom}20`
                    : currentResult?.result_type === 'function'
                    ? `${colors.apollo.primary}20`
                    : `${colors.hermes.cyan}20`,
                }}
              >
                <Sparkles
                  className="w-6 h-6"
                  style={{
                    color: isInsight
                      ? colors.insight.bloom
                      : currentResult?.result_type === 'function'
                      ? colors.apollo.primary
                      : colors.hermes.cyan,
                  }}
                />
              </div>
              <div className="flex-1">
                <h3
                  className="mb-2"
                  style={{
                    fontSize: typography.sizes.h3,
                    fontWeight: typography.weights.light,
                    color: colors.text.primary,
                  }}
                >
                  {currentResult?.query || 'Processing your query...'}
                </h3>

                {/* Markdown Rendering */}
                <div 
                  className="prose prose-invert prose-sm md:prose-base max-w-none"
                  style={{
                    color: colors.text.secondary, // Set a base color
                  }}
                >
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {currentResult?.answer || 'Lumina is exploring your knowledge tree...'}
                    </ReactMarkdown>
                </div>

                {/* Function-specific result display */}
                {currentResult?.result_type === 'function' && currentResult.function_result && (
                  <div className="mt-4">
                    {currentResult.function_result.success ? (
                      <div
                        className="p-3 rounded-lg"
                        style={{
                          backgroundColor: `${colors.apollo.primary}10`,
                          border: `1px solid ${colors.apollo.primary}30`,
                        }}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <p style={{
                              fontSize: typography.sizes.bodySmall,
                              color: colors.text.primary,
                              fontWeight: typography.weights.medium,
                            }}>
                              ✅ {currentResult.function_result.message}
                            </p>
                            {currentResult.function_result.filepath && (
                              <p style={{
                                fontSize: typography.sizes.caption,
                                color: colors.text.tertiary,
                                fontFamily: typography.fonts.mono,
                                marginTop: '4px',
                              }}>
                                📁 {currentResult.function_result.filepath}
                              </p>
                            )}
                            {currentResult.function_result.record_count && (
                              <p style={{
                                fontSize: typography.sizes.caption,
                                color: colors.text.tertiary,
                                marginTop: '4px',
                              }}>
                                Exported {currentResult.function_result.record_count} records
                              </p>
                            )}
                          </div>

                          {/* Download Button */}
                          {currentResult.function_result.filepath && (
                            <button
                              onClick={() => handleDownload(currentResult.function_result!.filepath!)}
                              className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all hover:scale-105 hover:opacity-90"
                              style={{
                                backgroundColor: colors.apollo.primary,
                                color: colors.midnight.deep,
                                fontSize: typography.sizes.bodySmall,
                                fontWeight: typography.weights.medium,
                              }}
                            >
                              <Download className="w-4 h-4" />
                              Download
                            </button>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div
                        className="p-3 rounded-lg"
                        style={{
                          backgroundColor: '#ff444410',
                          border: '1px solid #ff444430',
                        }}
                      >
                        <p style={{
                          fontSize: typography.sizes.bodySmall,
                          color: '#ff4444',
                        }}>
                          ❌ {currentResult.function_result.message}
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* RAG sources (only for RAG queries) */}
                {currentResult?.result_type !== 'function' && currentResult?.sources && currentResult.sources.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {currentResult.sources.map((source, idx) => (
                      <button
                        key={source.rowId || idx}
                        className="px-3 py-1 rounded-full text-xs flex items-center gap-1 transition-all hover:scale-105"
                        style={{
                          backgroundColor: `${colors.hermes.cyan}20`,
                          color: colors.hermes.cyan,
                          border: `1px solid ${colors.hermes.cyan}40`,
                        }}
                      >
                        <ExternalLink className="w-3 h-3" />
                        {source.documentName}
                        {source.page && ` (p.${source.page})`}
                      </button>
                    ))}
                  </div>
                )}

                {/* Analyze Deeper button (only for RAG queries with results) */}
                {currentResult?.result_type !== 'function' && currentResult?.relevantRecords && currentResult.relevantRecords.length > 0 && (
                  <div className="mt-4">
                    <button
                      onClick={generateGraphFromQuery}
                      disabled={isGeneratingGraph}
                      className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                      style={{
                        backgroundColor: `${colors.insight.bloom}20`,
                        color: colors.insight.bloom,
                        border: `2px solid ${colors.insight.bloom}40`,
                      }}
                    >
                      {isGeneratingGraph ? (
                        <>
                          <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                          >
                            <Network className="w-4 h-4" />
                          </motion.div>
                          <span>Generating Graph...</span>
                        </>
                      ) : (
                        <>
                          <Network className="w-4 h-4" />
                          <span>Visual Summary</span>
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {/* Data Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h2
              style={{
                fontSize: typography.sizes.h3,
                fontWeight: typography.weights.light,
                color: colors.text.primary,
              }}
            >
              Extracted Data
            </h2>
            <span
              style={{
                fontSize: typography.sizes.bodySmall,
                color: colors.text.tertiary,
              }}
            >
              {extractedData?.metadata.totalRecords ?? 0} records
            </span>
          </div>
          

          <div
            className="rounded-xl border overflow-hidden"
            style={{
              backgroundColor: colors.midnight.light,
              borderColor: `${colors.silver.warm}10`,
            }}
          >
            {hasRecords ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr
                      style={{
                        borderBottom: `1px solid ${colors.silver.warm}10`,
                        backgroundColor: `${colors.midnight.mid}80`,
                      }}
                    >
                      {/* CHANGE 1: Iterate over our new 'visibleFields' array for the headers */}
                      {visibleFields.map((field) => (
                        <th
                          key={field.name}
                          className="px-6 py-4 text-left"
                          style={{
                            fontSize: typography.sizes.bodySmall,
                            fontWeight: typography.weights.medium,
                            color: colors.text.secondary,
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                          }}
                        >
                          {field.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {extractedData.records.map((row, idx) => (
                      <motion.tr
                        key={row.rowId || idx}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className="transition-colors hover:bg-white/5"
                        style={{
                          borderBottom: `1px solid ${colors.silver.warm}05`,
                        }}
                      >
                        {/* CHANGE 2: Iterate over 'visibleFields' again to ensure cells match headers */}
                        {visibleFields.map((field) => {
                        // Handle nested objects ---
                        const cellValue = row[field.name] ?? null;
                        let displayValue;

                        if (cellValue === null) {
                          displayValue = ''; // Render nothing for null
                        } else if (typeof cellValue === 'object') {
                          // If it's an object or array, stringify it
                          displayValue = JSON.stringify(cellValue);
                        } else {
                          // Otherwise, convert to string
                          displayValue = String(cellValue);
                        }
                        return (
                          <td
                            key={field.name}
                            className="px-6 py-4 truncate-cell"
                            title={displayValue} // Tooltip for full content
                            style={{
                              fontSize: typography.sizes.body,
                              color: colors.text.primary,
                              fontFamily: (typeof cellValue === 'number' || typeof cellValue === 'object')
                                ? typography.fonts.mono
                                : typography.fonts.primary,
                              // whiteSpace: 'pre-wrap', // Good for showing stringified JSON
                              // wordBreak: 'break-word', // Prevents long strings from breaking layout
                            }}
                          >
                            {displayValue}
                          </td>
                        );
                      })}
                    </motion.tr>
                  ))}
                </tbody>
                </table>
              </div>
            ) : (
              <div className="p-16 text-center">
                <p
                  className="mb-2"
                  style={{
                    fontSize: typography.sizes.h3,
                    fontWeight: typography.weights.light,
                    color: colors.text.secondary,
                  }}
                >
                  No data extracted yet
                </p>
                <p
                  style={{
                    fontSize: typography.sizes.body,
                    color: colors.text.tertiary,
                  }}
                >
                  Check the error message above for details, then click Retry.
                </p>
              </div>
            )}
          </div>
        </motion.div>


      </div>

      {/* Graph Visualization Modal */}
      {graphData && (
        <GraphVisualization
          graphData={graphData}
          onClose={() => useAppStore.setState({ graphData: null })}
        />
      )}
    </div>
  );
};

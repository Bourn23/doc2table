import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { colors, typography, animation } from '../styles/designTokens';


/**
 * ProcessingView - Apollo Mode
 * Strategic, methodical processing visualization
 * Now handles both ANALYZING and PROCESSING phases
 */
export const ProcessingView: React.FC = () => {
  const { 
    uploadedFiles, 
    processingSteps, 
    phase,
    jobStatus,
    jobMessage,
    currentJobService
  } = useAppStore();

  const isAnalyzing = phase === 'analyzing';
  const title = isAnalyzing ? 'Analyzing Documents' : 'Processing Pipeline';
  
  // Show current job message if available
  const description = jobMessage || (isAnalyzing
    ? 'Lumina is analyzing your documents to understand their content and recommend the best extraction strategy.'
    : 'Lumina is methodically extracting structured data and preparing it for exploration.');

  // Determine current service for better messaging
  const serviceLabel = currentJobService === 'extraction' 
    ? 'Extracting Data' 
    : currentJobService === 'indexing'
    ? 'Indexing for Search'
    : title;

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative z-10">
      <div className="max-w-4xl w-full">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Left: File List */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: animation.duration.base / 1000 }}
          >
            <h2
              className="mb-6"
              style={{
                fontSize: typography.sizes.h3,
                fontWeight: typography.weights.light,
                color: colors.text.primary,
              }}
            >
              Documents
            </h2>

            <div className="space-y-3">
              {uploadedFiles.map((file) => (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 rounded-lg border"
                  style={{
                    backgroundColor: `${colors.midnight.light}60`,
                    borderColor: `${colors.apollo.primary}40`,
                  }}
                >
                  <div className="flex items-start gap-3">
                    <CheckCircle
                      className="w-5 h-5 mt-0.5 flex-shrink-0"
                      style={{ color: colors.apollo.primary }}
                    />
                    <div className="flex-1 min-w-0">
                      <p
                        className="truncate mb-1"
                        style={{
                          fontSize: typography.sizes.body,
                          color: colors.text.primary,
                        }}
                      >
                        {file.name}
                      </p>
                      <div className="flex items-center gap-2">
                        <span
                          style={{
                            fontSize: typography.sizes.caption,
                            color: colors.text.tertiary,
                          }}
                        >
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </span>
                        <span style={{ color: colors.text.tertiary }}>•</span>
                        <span
                          style={{
                            fontSize: typography.sizes.caption,
                            color: colors.apollo.primary,
                          }}
                        >
                          Uploaded
                        </span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Right: Processing Pipeline */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: animation.duration.base / 1000, delay: 0.2 }}
          >
            <h2
              className="mb-6"
              style={{
                fontSize: typography.sizes.h3,
                fontWeight: typography.weights.light,
                color: colors.text.primary,
              }}
            >
              {serviceLabel}
            </h2>

            <div className="space-y-4">
              {processingSteps.map((step, index) => (
                <motion.div
                  key={step.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-4"
                >
                  {/* Status indicator */}
                  <div className="flex-shrink-0">
                    {step.complete ? (
                      <div
                        className="w-6 h-6 rounded-full flex items-center justify-center"
                        style={{ backgroundColor: colors.apollo.primary }}
                      >
                        <svg
                          className="w-4 h-4"
                          fill="none"
                          stroke={colors.midnight.mid}
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      </div>
                    ) : (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                      >
                        <Loader2
                          className="w-6 h-6"
                          style={{ color: colors.apollo.primary }}
                        />
                      </motion.div>
                    )}
                  </div>

                  {/* Step label */}
                  <div className="flex-1">
                    <p
                      style={{
                        fontSize: typography.sizes.body,
                        color: step.complete ? colors.text.primary : colors.apollo.primary,
                        fontWeight: step.complete ? typography.weights.regular : typography.weights.medium,
                      }}
                    >
                      {step.label}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Real-time status message */}
            <div className="mt-8 p-6 rounded-lg border" style={{
              backgroundColor: `${colors.midnight.light}40`,
              borderColor: jobStatus === 'FAILED' 
                ? '#ff444440'
                : `${colors.apollo.primary}20`,
            }}>
              <div className="flex items-center gap-3 mb-3">
                {jobStatus === 'FAILED' ? (
                  <AlertCircle className="w-5 h-5" style={{ color: '#ff4444' }} />
                ) : (
                  <div
                    className="w-2 h-2 rounded-full animate-pulse"
                    style={{ backgroundColor: colors.apollo.primary }}
                  />
                )}
                <p style={{
                  fontSize: typography.sizes.bodySmall,
                  color: jobStatus === 'FAILED' ? '#ff4444' : colors.text.secondary,
                  fontWeight: typography.weights.medium,
                }}>
                  {jobStatus === 'FAILED' ? 'Error' : serviceLabel}
                </p>
              </div>
              <p style={{
                fontSize: typography.sizes.caption,
                color: colors.text.tertiary,
                lineHeight: 1.6,
              }}>
                {description}
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};
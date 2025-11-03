import React, { useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, Sparkles, AlertCircle } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { colors, typography, animation } from '../styles/designTokens';

/**
 * IdleView - EVE Neutral State
 * The resting state where users begin their journey
 */
export const IdleView: React.FC = () => {
  const { uploadFiles, toggleCommandPalette, jobStatus, jobMessage } = useAppStore();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      uploadFiles(files);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      uploadFiles(files);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const getFriendlyErrorMessage = (msg: string | null): string => {
    if (!msg) return 'An unknown error occurred.';

    // Check for the specific Gemini error from your logs
    if (msg.includes('geminiException') && msg.includes('model is overloaded')) {
      return 'The analysis model is overloaded. Please try again in a few moments.';
    }

    // Try to find a JSON error message
    const jsonMatch = msg.match(/{.*}/s);
    if (jsonMatch) {
      try {
        const errorObj = JSON.parse(jsonMatch[0]);
        if (errorObj.error && errorObj.error.message) {
          return errorObj.error.message;
        }
      } catch (e) {
        /* ignore parse error */
      }
    }

    // Fallback: Show the first part of the message before any stack trace
    const cleanMsg = msg.split('↵')[0].trim();
    if (cleanMsg && cleanMsg.length > 5) {
      return cleanMsg;
    }

    return 'An unexpected processing error occurred. Please try again.'; // Generic fallback
  };

  const friendlyErrorMessage = getFriendlyErrorMessage(jobMessage);

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative z-10">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: animation.duration.base / 1000 }}
        className="text-center max-w-3xl mx-auto"
      >
        {/* +++ ERROR ALERT +++ */}
        {jobStatus === 'FAILED' && jobMessage && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mb-8 p-4 rounded-lg border w-full text-left"
            style={{
              // Using the same error colors from your ProcessingView for consistency
              backgroundColor: '#ff444410',
              borderColor: '#ff444440',
            }}
          >
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0" style={{ color: '#ff4444' }} />
              <div>
                <p
                  style={{
                    fontSize: typography.sizes.body,
                    fontWeight: typography.weights.medium,
                    color: '#ff4444',
                  }}
                >
                  Analysis Failed
                </p>
                <p
                  className="mt-1"
                  style={{
                    fontSize: typography.sizes.bodySmall,
                    color: colors.text.secondary,
                    lineHeight: 1.6,
                  }}
                >
                  {friendlyErrorMessage}
                </p>
              </div>
            </div>
          </motion.div>
        )}
        {/* +++ END ERROR ALERT +++ */}

        {/* Logo/Icon */}
        <motion.div
          className="mb-8 flex justify-center"
          animate={{
            scale: [1, 1.02, 1],
            opacity: [0.9, 1, 0.9],
          }}
          transition={{
            duration: animation.duration.breathing / 1000,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          <div className="relative w-24 h-24">
            <div
              className="absolute inset-0 rounded-full blur-2xl"
              style={{
                background: `linear-gradient(135deg, ${colors.silver.warm}, ${colors.hermes.cyan})`,
                opacity: 0.2,
              }}
            />
            <div
              className="absolute inset-4 rounded-full blur-xl"
              style={{
                background: `linear-gradient(135deg, ${colors.silver.warm}, ${colors.hermes.cyan})`,
                opacity: 0.4,
              }}
            />
            <div
              className="absolute inset-8 rounded-full flex items-center justify-center"
              style={{ backgroundColor: colors.silver.warm }}
            >
              <Sparkles className="w-8 h-8" style={{ color: colors.midnight.mid }} />
            </div>
          </div>
        </motion.div>

        {/* Greeting */}
        <h1
          className="mb-6"
          style={{
            fontSize: typography.sizes.h1,
            fontWeight: typography.weights.light,
            color: colors.text.primary,
            letterSpacing: '-0.02em',
          }}
        >
          Illuminate your data
        </h1>

        <p
          className="mb-4"
          style={{
            fontSize: typography.sizes.bodyLarge,
            color: colors.text.secondary,
            fontWeight: typography.weights.light,
          }}
        >
          Powered by Lumina
        </p>

        <p
          className="mb-12 leading-relaxed max-w-2xl mx-auto"
          style={{
            fontSize: typography.sizes.body,
            color: colors.text.tertiary,
          }}
        >
          Transform your PDFs into structured data. Upload documents to extract meaningful data,
          explore connections, and discover insights through natural conversation.
        </p>

        {/* Upload Area */}
        <div
          className="mb-8 p-12 rounded-2xl border-2 border-dashed cursor-pointer transition-all hover:border-opacity-50"
          style={{
            borderColor: `${colors.silver.warm}30`,
            backgroundColor: `${colors.midnight.light}40`,
          }}
          onClick={() => fileInputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          <Upload
            className="w-12 h-12 mx-auto mb-4"
            style={{ color: colors.text.secondary }}
          />
          <p
            className="mb-2"
            style={{
              fontSize: typography.sizes.bodyLarge,
              color: colors.text.primary,
            }}
          >
            Drop PDFs here or click to upload
          </p>
          <p style={{ fontSize: typography.sizes.bodySmall, color: colors.text.tertiary }}>
            Supports PDF, CSV, TXT, and Markdown files
          </p>
        </div>

        <input
          ref={fileInputRef}
          id="file-upload"
          type="file"
          multiple
          accept=".pdf,.csv,.txt,.md"
          onChange={handleFileSelect}
          className="hidden"
        />

        {/* Alternative action */}
        <div className="flex items-center justify-center gap-4">
          <div
            className="h-px flex-1"
            style={{ backgroundColor: `${colors.silver.warm}10` }}
          />
          <span style={{ fontSize: typography.sizes.caption, color: colors.text.tertiary }}>
            or
          </span>
          <div
            className="h-px flex-1"
            style={{ backgroundColor: `${colors.silver.warm}10` }}
          />
        </div>

        <button
          onClick={toggleCommandPalette}
          className="mt-6 px-6 py-3 rounded-lg transition-all hover:scale-105"
          style={{
            backgroundColor: `${colors.silver.warm}10`,
            color: colors.text.primary,
            fontSize: typography.sizes.body,
            border: `1px solid ${colors.silver.warm}30`,
          }}
        >
          Open Command Palette <kbd className="ml-2 px-2 py-1 rounded text-xs" style={{
            backgroundColor: `${colors.silver.warm}20`,
            fontFamily: typography.fonts.mono
          }}>⌘K</kbd>
        </button>

        {/* Hint */}
        <p
          className="mt-8"
          style={{
            fontSize: typography.sizes.caption,
            color: colors.text.subtle,
          }}
        >
          Your data remains private and secure
        </p>
      </motion.div>
    </div>
  );
};

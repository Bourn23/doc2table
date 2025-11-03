import React from 'react';
import { motion } from 'framer-motion';
import { useAppStore } from '../store/useAppStore';
import { colors, personalityModes, animation } from '../styles/designTokens';

/**
 * PersonalityAura Component
 * Subtle screen-edge glow that pulsates to indicate current personality mode
 */
export const PersonalityAura: React.FC = () => {
  const { personalityMode, phase } = useAppStore();

  const modeConfig = personalityModes[personalityMode];
  const tempo = modeConfig.tempo;

  // Convert BPM to milliseconds per beat
  const beatDuration = (60 / tempo) * 1000;

  // Determine colors based on mode
  const getAuraColors = () => {
    switch (personalityMode) {
      case 'apollo':
        return {
          primary: colors.apollo.primary,
          secondary: colors.apollo.highlight,
          opacity: 0.15,
        };
      case 'hermes':
        return {
          primary: colors.hermes.cyan,
          secondary: colors.hermes.violet,
          opacity: 0.12,
        };
      default: // neutral/EVE
        return {
          primary: colors.silver.warm,
          secondary: colors.silver.warmer,
          opacity: 0.08,
        };
    }
  };

  const auraColors = getAuraColors();

  return (
    <>
      {/* Top Edge Aura */}
      <motion.div
        className="fixed top-0 left-0 right-0 h-32 pointer-events-none z-[5]"
        style={{
          background: `linear-gradient(to bottom, ${auraColors.primary}${Math.round(auraColors.opacity * 255).toString(16).padStart(2, '0')}, transparent)`,
        }}
        animate={{
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: beatDuration / 1000,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />

      {/* Bottom Edge Aura */}
      <motion.div
        className="fixed bottom-0 left-0 right-0 h-32 pointer-events-none z-[5]"
        style={{
          background: `linear-gradient(to top, ${auraColors.primary}${Math.round(auraColors.opacity * 255).toString(16).padStart(2, '0')}, transparent)`,
        }}
        animate={{
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: beatDuration / 1000,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: beatDuration / 2000, // Offset by half a beat
        }}
      />

      {/* Left Edge Aura */}
      <motion.div
        className="fixed top-0 left-0 bottom-0 w-32 pointer-events-none z-[5]"
        style={{
          background: `linear-gradient(to right, ${auraColors.secondary}${Math.round(auraColors.opacity * 0.8 * 255).toString(16).padStart(2, '0')}, transparent)`,
        }}
        animate={{
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: beatDuration / 1000,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: beatDuration / 4000, // Quarter beat offset
        }}
      />

      {/* Right Edge Aura */}
      <motion.div
        className="fixed top-0 right-0 bottom-0 w-32 pointer-events-none z-[5]"
        style={{
          background: `linear-gradient(to left, ${auraColors.secondary}${Math.round(auraColors.opacity * 0.8 * 255).toString(16).padStart(2, '0')}, transparent)`,
        }}
        animate={{
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: beatDuration / 1000,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: (beatDuration * 3) / 4000, // Three-quarter beat offset
        }}
      />

      {/* Corner Accent Glows (Hermes mode gets extra dynamic corners) */}
      {personalityMode === 'hermes' && (
        <>
          {/* Top-left corner */}
          <motion.div
            className="fixed top-0 left-0 w-48 h-48 pointer-events-none z-[5]"
            style={{
              background: `radial-gradient(circle at top left, ${colors.hermes.cyan}20, transparent 70%)`,
            }}
            animate={{
              opacity: [0.4, 0.8, 0.4],
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: beatDuration / 1000,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />

          {/* Bottom-right corner */}
          <motion.div
            className="fixed bottom-0 right-0 w-48 h-48 pointer-events-none z-[5]"
            style={{
              background: `radial-gradient(circle at bottom right, ${colors.hermes.violet}20, transparent 70%)`,
            }}
            animate={{
              opacity: [0.4, 0.8, 0.4],
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: beatDuration / 1000,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: beatDuration / 2000,
            }}
          />
        </>
      )}

      {/* Mode Indicator Label (optional, subtle) */}
      <motion.div
        className="fixed top-6 right-6 pointer-events-none z-[5]"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
      >
        <div
          className="px-4 py-2 rounded-full backdrop-blur-sm border"
          style={{
            backgroundColor: `${auraColors.primary}10`,
            borderColor: `${auraColors.primary}30`,
            color: auraColors.primary,
            fontSize: '0.75rem',
            fontWeight: 300,
            letterSpacing: '0.05em',
          }}
        >
          <motion.div
            animate={{
              opacity: [0.6, 1, 0.6],
            }}
            transition={{
              duration: beatDuration / 1000,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          >
            {modeConfig.name}
          </motion.div>
        </div>
      </motion.div>
    </>
  );
};

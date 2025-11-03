import React, { useEffect } from 'react';
import { AnimatedBackground } from './components/AnimatedBackground';
import { PersonalityAura } from './components/PersonalityAura';
import { CommandPalette } from './components/CommandPalette';
import { IdleView } from './phases/IdleView';
import { ProcessingView } from './phases/ProcessingView';
import { SchemaEditorView } from './phases/SchemaEditorView';
import { ExplorationView } from './phases/ExplorationView';
import { useAppStore } from './store/useAppStore';
import { AppPhase } from './types';
import { getColors, getTypography } from './styles/designTokens';

/**
 * Main App Component
 * Orchestrates phase-based UI and personality transitions
 */
function App() {
  const { phase, personalityMode, accessibility } = useAppStore();

  // Get theme colors and typography based on accessibility preferences
  const colors = getColors(accessibility.lightMode, accessibility.highContrast);
  const typography = getTypography(accessibility.fontSize);

  // Log phase changes for debugging
  useEffect(() => {
    console.log(`Phase changed to: ${phase}, Personality: ${personalityMode}`);
  }, [phase, personalityMode]);

  // Apply font size to document root
  useEffect(() => {
    document.documentElement.style.fontSize = accessibility.fontSize === 'large' ? '20px' : '16px';
  }, [accessibility.fontSize]);

  // Render appropriate view based on phase
  const renderPhaseView = () => {
    switch (phase) {
      case AppPhase.IDLE:
        return <IdleView />;

      case AppPhase.UPLOADING:
      case AppPhase.ANALYZING:
      case AppPhase.PROCESSING:
        return <ProcessingView />;

      case AppPhase.SCHEMA_REVIEW:
        return <SchemaEditorView />;

      case AppPhase.READY:
      case AppPhase.QUERYING:
      case AppPhase.INSIGHT:
        return <ExplorationView />;

      default:
        return <IdleView />;
    }
  };

  return (
    <div
      className="relative min-h-screen overflow-hidden transition-colors duration-1000"
      style={{
        backgroundColor: colors.midnight.deep,
        color: colors.text.primary,
      }}
    >
      {/* Animated Background Layer */}
      <AnimatedBackground />

      {/* Personality Aura - Screen edge glow that indicates current mode */}
      {/* <PersonalityAura /> */}

      {/* Main Content Layer */}
      <div className="relative z-10">
        {renderPhaseView()}
      </div>

      {/* Command Palette (Always mounted, controlled by state) */}
      <CommandPalette />

      {/* Screen reader announcements for phase changes */}
      <div className="sr-only" aria-live="polite" aria-atomic="true">
        {phase === AppPhase.ANALYZING && 'Analyzing documents...'}
        {phase === AppPhase.SCHEMA_REVIEW && 'Review AI recommendations'}
        {phase === AppPhase.PROCESSING && 'Processing your documents...'}
        {phase === AppPhase.READY && 'Data ready for exploration'}
        {phase === AppPhase.QUERYING && 'Processing your query...'}
        {phase === AppPhase.INSIGHT && 'Insight discovered'}
      </div>
    </div>
  );
}

export default App;

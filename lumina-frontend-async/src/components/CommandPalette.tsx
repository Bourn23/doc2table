import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Upload,
  Download,
  FileJson,
  RotateCcw,
  BarChart3,
  FileText,
  Zap,
  ArrowRight,
  X,
  Command as CommandIcon,
  Type,
  Contrast,
  Sun,
  Moon
} from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { colors, animation, typography } from '../styles/designTokens';
import { AppPhase } from '../types';

interface Command {
  id: string;
  label: string;
  description: string;
  category: 'actions' | 'queries' | 'data' | 'accessibility';
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  action: () => void;
  keywords?: string[];
  enabled?: boolean;
  isToggle?: boolean;
  toggleState?: boolean;
}

/**
 * CommandPalette Component
 * Palantir-inspired command interface (⌘K / Ctrl+K)
 */
export const CommandPalette: React.FC = () => {
  const {
    commandPaletteOpen,
    toggleCommandPalette,
    submitQuery,
    phase,
    extractedData,
    confirmAndExtract,
    setPhase,
    accessibility,
    setAccessibilityOption,
  } = useAppStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Define all available commands
  const allCommands: Command[] = [
    // Quick Actions
    {
      id: 'upload',
      label: 'Upload Documents',
      description: 'Upload new documents for extraction',
      category: 'actions',
      icon: Upload,
      action: () => {
        setPhase(AppPhase.IDLE);
        toggleCommandPalette();
      },
      keywords: ['file', 'pdf', 'document', 'new'],
      enabled: phase === AppPhase.IDLE || phase === AppPhase.READY
    },
    {
      id: 'export-csv',
      label: 'Export as CSV',
      description: 'Export extracted data as CSV file',
      category: 'actions',
      icon: Download,
      action: () => {
        submitQuery('Export as CSV');
        toggleCommandPalette();
      },
      keywords: ['download', 'save', 'csv', 'export'],
      enabled: extractedData?.records.length > 0
    },
    {
      id: 'export-json',
      label: 'Export as JSON',
      description: 'Export extracted data as JSON file',
      category: 'actions',
      icon: FileJson,
      action: () => {
        submitQuery('Export as JSON');
        toggleCommandPalette();
      },
      keywords: ['download', 'save', 'json', 'export'],
      enabled: extractedData?.records.length > 0
    },
    {
      id: 'retry-extraction',
      label: 'Retry Extraction',
      description: 'Re-run the extraction process',
      category: 'actions',
      icon: RotateCcw,
      action: () => {
        confirmAndExtract();
        toggleCommandPalette();
      },
      keywords: ['retry', 'redo', 'again'],
      enabled: phase === AppPhase.READY
    },

    // Query Templates
    // {
    //   id: 'query-averages',
    //   label: 'Create a Column',
    //   description: 'Creates a new column based on available documents or columns.',
    //   category: 'queries',
    //   icon: BarChart3,
    //   action: () => {
    //     submitQuery('Create a new column to extract <DESCRIPTION>');
    //     toggleCommandPalette();
    //   },
    //   keywords: ['calculate', 'mean', 'statistics', 'stats'],
    //   enabled: extractedData?.records.length > 0
    // },
    // {
    //   id: 'query-correlations',
    //   label: 'Find Correlations',
    //   description: 'Discover relationships in the data',
    //   category: 'queries',
    //   icon: Zap,
    //   action: () => {
    //     submitQuery('Find correlations between <COLUMN_A> and <COLUMN_B>');
    //     toggleCommandPalette();
    //   },
    //   keywords: ['relationship', 'pattern', 'connection'],
    //   enabled: extractedData?.records.length > 0
    // },
    // {
    //   id: 'query-summary',
    //   label: 'Summarize column',
    //   description: 'Get an overview of extracted data',
    //   category: 'queries',
    //   icon: FileText,
    //   action: () => {
    //     submitQuery('Summarize the extracted data from <COLUMN_NAMES>');
    //     toggleCommandPalette();
    //   },
    //   keywords: ['overview', 'summary', 'describe'],
    //   enabled: extractedData?.records.length > 0
    // },

    // Accessibility Options
    {
      id: 'toggle-font-size',
      label: accessibility.fontSize === 'default' ? 'Enable Large Font' : 'Disable Large Font',
      description: accessibility.fontSize === 'default'
        ? 'Increase font size for better readability'
        : 'Return to default font size',
      category: 'accessibility',
      icon: Type,
      action: () => {
        setAccessibilityOption('fontSize', accessibility.fontSize === 'default' ? 'large' : 'default');
        toggleCommandPalette();
      },
      keywords: ['font', 'text', 'size', 'larger', 'bigger', 'readability', 'accessibility', 'a11y'],
      enabled: true,
      isToggle: true,
      toggleState: accessibility.fontSize === 'large'
    },
    // {
    //   id: 'toggle-high-contrast',
    //   label: accessibility.highContrast ? 'Disable High Contrast' : 'Enable High Contrast',
    //   description: accessibility.highContrast
    //     ? 'Return to standard contrast'
    //     : 'Increase contrast for better visibility',
    //   category: 'accessibility',
    //   icon: Contrast,
    //   action: () => {
    //     setAccessibilityOption('highContrast', !accessibility.highContrast);
    //     toggleCommandPalette();
    //   },
    //   keywords: ['contrast', 'visibility', 'accessibility', 'a11y', 'vision'],
    //   enabled: true,
    //   isToggle: true,
    //   toggleState: accessibility.highContrast
    // },
    // {
    //   id: 'toggle-light-mode',
    //   label: accessibility.lightMode ? 'Switch to Dark Mode' : 'Switch to Light Mode',
    //   description: accessibility.lightMode
    //     ? 'Use dark theme with light text'
    //     : 'Use light theme with dark text',
    //   category: 'accessibility',
    //   icon: accessibility.lightMode ? Moon : Sun,
    //   action: () => {
    //     setAccessibilityOption('lightMode', !accessibility.lightMode);
    //     toggleCommandPalette();
    //   },
    //   keywords: ['theme', 'dark', 'light', 'mode', 'brightness', 'accessibility', 'a11y'],
    //   enabled: true,
    //   isToggle: true,
    //   toggleState: accessibility.lightMode
    // }
  ];

  // Filter commands based on search query and enabled state
  const filteredCommands = allCommands.filter(cmd => {
    if (cmd.enabled === false) return false;

    if (!searchQuery) return true;

    const query = searchQuery.toLowerCase();
    const matchesLabel = cmd.label.toLowerCase().includes(query);
    const matchesDescription = cmd.description.toLowerCase().includes(query);
    const matchesKeywords = cmd.keywords?.some(kw => kw.toLowerCase().includes(query));

    return matchesLabel || matchesDescription || matchesKeywords;
  });

  // Group commands by category
  const groupedCommands = filteredCommands.reduce((acc, cmd) => {
    if (!acc[cmd.category]) acc[cmd.category] = [];
    acc[cmd.category].push(cmd);
    return acc;
  }, {} as Record<string, Command[]>);

  const categoryLabels: Record<string, string> = {
    actions: 'Quick Actions',
    queries: 'Query Templates',
    data: 'Data Operations',
    accessibility: 'Accessibility'
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd+K (Mac) or Ctrl+K (Windows/Linux)
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        toggleCommandPalette();
      }

      // Escape to close
      if (e.key === 'Escape' && commandPaletteOpen) {
        toggleCommandPalette();
      }

      if (!commandPaletteOpen) return;

      // Arrow navigation
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => Math.min(prev + 1, filteredCommands.length - 1));
      }

      if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => Math.max(prev - 1, 0));
      }

      // Enter to execute
      if (e.key === 'Enter') {
        e.preventDefault();
        const selectedCommand = filteredCommands[selectedIndex];
        if (selectedCommand) {
          selectedCommand.action();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [commandPaletteOpen, selectedIndex, filteredCommands, toggleCommandPalette]);

  // Focus input when opened
  useEffect(() => {
    if (commandPaletteOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [commandPaletteOpen]);

  // Reset state when closed
  useEffect(() => {
    if (!commandPaletteOpen) {
      setSearchQuery('');
      setSelectedIndex(0);
    }
  }, [commandPaletteOpen]);

  if (!commandPaletteOpen) return null;

  return (
    <AnimatePresence>
      <div
        className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]"
        style={{ backgroundColor: 'rgba(0, 0, 0, 0.6)' }}
        onClick={toggleCommandPalette}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -20 }}
          transition={{ duration: 0.15 }}
          className="w-full max-w-2xl mx-4"
          onClick={(e) => e.stopPropagation()}
        >
          <div
            className="rounded-xl border shadow-2xl overflow-hidden"
            style={{
              backgroundColor: colors.midnight.mid,
              borderColor: `${colors.silver.warm}20`,
            }}
          >
            {/* Search Input */}
            <div
              className="flex items-center gap-3 px-4 py-4 border-b"
              style={{ borderColor: `${colors.silver.warm}10` }}
            >
              <Search
                className="w-5 h-5 flex-shrink-0"
                style={{ color: colors.text.tertiary }}
              />
              <input
                ref={inputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setSelectedIndex(0);
                }}
                placeholder="Search commands..."
                className="flex-1 bg-transparent outline-none"
                style={{
                  fontSize: typography.sizes.body,
                  color: colors.text.primary,
                }}
              />
              <button
                onClick={toggleCommandPalette}
                className="p-1 rounded hover:bg-white/10 transition-colors"
                style={{ color: colors.text.tertiary }}
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Commands List */}
            <div
              className="max-h-96 overflow-y-auto"
              style={{
                backgroundColor: colors.midnight.light,
              }}
            >
              {filteredCommands.length === 0 ? (
                <div className="px-4 py-8 text-center">
                  <p style={{ color: colors.text.tertiary, fontSize: typography.sizes.body }}>
                    No commands found
                  </p>
                </div>
              ) : (
                Object.entries(groupedCommands).map(([category, commands]) => (
                  <div key={category}>
                    {/* Category Header */}
                    <div
                      className="px-4 py-2 sticky top-0"
                      style={{
                        backgroundColor: colors.midnight.mid,
                        fontSize: typography.sizes.caption,
                        color: colors.text.tertiary,
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        fontWeight: typography.weights.medium,
                      }}
                    >
                      {categoryLabels[category]}
                    </div>

                    {/* Commands */}
                    {commands.map((cmd) => {
                      const globalIndex = filteredCommands.indexOf(cmd);
                      const isSelected = globalIndex === selectedIndex;

                      return (
                        <button
                          key={cmd.id}
                          onClick={() => cmd.action()}
                          onMouseEnter={() => setSelectedIndex(globalIndex)}
                          className="w-full px-4 py-3 flex items-center gap-3 transition-colors"
                          style={{
                            backgroundColor: isSelected
                              ? `${colors.hermes.cyan}10`
                              : 'transparent',
                            borderLeft: isSelected
                              ? `3px solid ${colors.hermes.cyan}`
                              : '3px solid transparent',
                          }}
                        >
                          <div
                            className="p-2 rounded-lg flex-shrink-0"
                            style={{
                              backgroundColor: isSelected
                                ? `${colors.hermes.cyan}20`
                                : `${colors.silver.warm}10`,
                            }}
                          >
                            <cmd.icon
                              className="w-4 h-4"
                              style={{
                                color: isSelected ? colors.hermes.cyan : colors.text.secondary,
                              }}
                            />
                          </div>
                          <div className="flex-1 text-left">
                            <div className="flex items-center gap-2">
                              <p
                                style={{
                                  fontSize: typography.sizes.body,
                                  color: colors.text.primary,
                                  fontWeight: typography.weights.medium,
                                }}
                              >
                                {cmd.label}
                              </p>
                              {cmd.isToggle && (
                                <div
                                  className="px-2 py-0.5 rounded-full text-xs"
                                  style={{
                                    backgroundColor: cmd.toggleState
                                      ? `${colors.hermes.cyan}20`
                                      : `${colors.text.tertiary}20`,
                                    color: cmd.toggleState ? colors.hermes.cyan : colors.text.tertiary,
                                  }}
                                >
                                  {cmd.toggleState ? 'ON' : 'OFF'}
                                </div>
                              )}
                            </div>
                            <p
                              style={{
                                fontSize: typography.sizes.caption,
                                color: colors.text.tertiary,
                              }}
                            >
                              {cmd.description}
                            </p>
                          </div>
                          {isSelected && (
                            <ArrowRight
                              className="w-4 h-4 flex-shrink-0"
                              style={{ color: colors.hermes.cyan }}
                            />
                          )}
                        </button>
                      );
                    })}
                  </div>
                ))
              )}
            </div>

            {/* Footer Hint */}
            <div
              className="px-4 py-3 border-t flex items-center justify-between"
              style={{
                backgroundColor: colors.midnight.deep,
                borderColor: `${colors.silver.warm}10`,
              }}
            >
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1">
                  <kbd
                    className="px-2 py-1 rounded text-xs"
                    style={{
                      backgroundColor: colors.midnight.mid,
                      color: colors.text.tertiary,
                      border: `1px solid ${colors.silver.warm}20`,
                    }}
                  >
                    ↑↓
                  </kbd>
                  <span style={{ fontSize: typography.sizes.caption, color: colors.text.tertiary }}>
                    Navigate
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <kbd
                    className="px-2 py-1 rounded text-xs"
                    style={{
                      backgroundColor: colors.midnight.mid,
                      color: colors.text.tertiary,
                      border: `1px solid ${colors.silver.warm}20`,
                    }}
                  >
                    ↵
                  </kbd>
                  <span style={{ fontSize: typography.sizes.caption, color: colors.text.tertiary }}>
                    Execute
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <kbd
                    className="px-2 py-1 rounded text-xs"
                    style={{
                      backgroundColor: colors.midnight.mid,
                      color: colors.text.tertiary,
                      border: `1px solid ${colors.silver.warm}20`,
                    }}
                  >
                    Esc
                  </kbd>
                  <span style={{ fontSize: typography.sizes.caption, color: colors.text.tertiary }}>
                    Close
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <CommandIcon
                  className="w-3 h-3"
                  style={{ color: colors.text.tertiary }}
                />
                <span style={{ fontSize: typography.sizes.caption, color: colors.text.tertiary }}>
                  + K to open
                </span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

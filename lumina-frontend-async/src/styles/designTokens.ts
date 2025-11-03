/**
 * Lumina/EVE Design System Tokens
 * Based on the Grounded Transcendence philosophy
 */

export const darkColors = {
  // Base midnight palette
  midnight: {
    deep: '#0a0e27',
    mid: '#0f172a',
    light: '#1a2332',
  },

  // Primary light (Lumina)
  silver: {
    warm: '#93c5fd',
    warmer: '#e8eef2',
  },

  // Text hierarchy
  text: {
    primary: '#e8eef2',
    secondary: '#8a94a6',
    tertiary: '#6b7788',
    subtle: '#4a5568',
  },

  // Accent colors
  accent: {
    depth: '#3a4556',
  },

  // Apollo Mode (Wisdom/Strategy)
  apollo: {
    primary: '#d4a574',
    secondary: '#c49158',
    highlight: '#e8d4b8',
  },

  // Hermes Mode (Quick Connections/Exploration)
  hermes: {
    cyan: '#4a9fb0',
    cyanDark: '#3a8a99',
    violet: '#6b5b95',
    violetDark: '#5a4a7f',
  },

  // Insight/Discovery State
  insight: {
    bloom: '#e8f4dc',
    bloomSecondary: '#d4e8c4',
  },

  // Uncertainty
  uncertainty: {
    primary: '#8a94a6',
  },

  // User-generated content
  user: {
    content: '#f5e6d3',
  },
} as const;

export const lightColors = {
  // Base light palette
  midnight: {
    deep: '#ffffff',
    mid: '#f8f9fa',
    light: '#e9ecef',
  },

  // Primary dark
  silver: {
    warm: '#2563eb',
    warmer: '#1e293b',
  },

  // Text hierarchy (inverted)
  text: {
    primary: '#1e293b',
    secondary: '#475569',
    tertiary: '#64748b',
    subtle: '#94a3b8',
  },

  // Accent colors
  accent: {
    depth: '#cbd5e1',
  },

  // Apollo Mode (Wisdom/Strategy) - adjusted for light mode
  apollo: {
    primary: '#c49158',
    secondary: '#d4a574',
    highlight: '#b5864f',
  },

  // Hermes Mode (Quick Connections/Exploration) - adjusted for light mode
  hermes: {
    cyan: '#0891b2',
    cyanDark: '#0e7490',
    violet: '#7c3aed',
    violetDark: '#6d28d9',
  },

  // Insight/Discovery State - adjusted for light mode
  insight: {
    bloom: '#22c55e',
    bloomSecondary: '#16a34a',
  },

  // Uncertainty
  uncertainty: {
    primary: '#64748b',
  },

  // User-generated content
  user: {
    content: '#d97706',
  },
} as const;

// Default to dark colors
export const colors = darkColors;

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  '2xl': '48px',
  '3xl': '64px',
  '4xl': '96px',
  '5xl': '128px',
} as const;

export const typography = {
  fonts: {
    primary: '-apple-system, BlinkMacSystemFont, "Segoe UI", "SF Pro Display", sans-serif',
    mono: '"SF Mono", "Monaco", "Consolas", monospace',
  },
  sizes: {
    display: '4.5rem',
    h1: '3rem',
    h2: '2.25rem',
    h3: '1.5rem',
    bodyLarge: '1.25rem',
    body: '1rem',
    bodySmall: '0.875rem',
    caption: '0.75rem',
  },
  weights: {
    light: 200,
    regular: 300,
    medium: 400,
    semibold: 500,
  },
} as const;

export const largeTypography = {
  ...typography,
  sizes: {
    display: '5.5rem',
    h1: '3.75rem',
    h2: '2.75rem',
    h3: '1.875rem',
    bodyLarge: '1.5rem',
    body: '1.25rem',
    bodySmall: '1.125rem',
    caption: '1rem',
  },
} as const;

export const animation = {
  duration: {
    micro: 150,
    fast: 300,
    base: 500,
    slow: 800,
    breathing: 12000,
  },
  easing: {
    soft: 'cubic-bezier(0.4, 0, 0.2, 1)',
    confident: 'cubic-bezier(0.2, 0.8, 0.3, 1)',
    organic: 'cubic-bezier(0.45, 0.05, 0.55, 0.95)',
    quick: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
  },
  tempo: {
    lumina: 48,      // BPM for standard light movement 72
    apollo: 44,      // BPM for strategic mode 68
    hermes: 60,     // BPM for quick mode 100
  },
} as const;

export const shadows = {
  sm: '0 1px 3px rgba(0, 0, 0, 0.3)',
  md: '0 4px 6px rgba(0, 0, 0, 0.3), 0 2px 4px rgba(0, 0, 0, 0.2)',
  lg: '0 10px 15px rgba(0, 0, 0, 0.3), 0 4px 6px rgba(0, 0, 0, 0.2)',
  xl: '0 20px 25px rgba(0, 0, 0, 0.3), 0 10px 10px rgba(0, 0, 0, 0.2)',
  glow: {
    sm: '0 0 10px rgba(232, 238, 242, 0.2)',
    md: '0 0 20px rgba(232, 238, 242, 0.3)',
    lg: '0 0 40px rgba(232, 238, 242, 0.4)',
  },
} as const;

// Personality mode configurations
export const personalityModes = {
  neutral: {
    name: 'EVE',
    colors: {
      primary: colors.silver.warm,
      accent: colors.silver.warmer,
      background: colors.midnight.mid,
    },
    tempo: animation.tempo.lumina,
    warmth: 0, // neutral temperature
  },
  apollo: {
    name: 'Apollo',
    colors: {
      primary: colors.apollo.primary,
      accent: colors.apollo.highlight,
      background: colors.midnight.mid,
    },
    tempo: animation.tempo.apollo,
    warmth: 10, // +10% warmth
  },
  hermes: {
    name: 'Hermes',
    colors: {
      primary: colors.hermes.cyan,
      accent: colors.hermes.violet,
      background: colors.midnight.mid,
    },
    tempo: animation.tempo.hermes,
    warmth: -5, // -5% warmth (cooler)
  },
} as const;

export type PersonalityMode = keyof typeof personalityModes;

/**
 * Utility functions to get theme based on accessibility preferences
 */
export const getColors = (lightMode: boolean, highContrast: boolean) => {
  const baseColors = lightMode ? lightColors : darkColors;

  if (highContrast) {
    // Enhance contrast for better readability
    return {
      ...baseColors,
      text: {
        ...baseColors.text,
        primary: lightMode ? '#000000' : '#ffffff',
        secondary: lightMode ? '#1e293b' : '#cbd5e1',
        tertiary: lightMode ? '#475569' : '#94a3b8',
      },
      midnight: {
        ...baseColors.midnight,
        deep: lightMode ? '#ffffff' : '#000000',
      },
    };
  }

  return baseColors;
};

export const getTypography = (fontSize: 'default' | 'large') => {
  return fontSize === 'large' ? largeTypography : typography;
};

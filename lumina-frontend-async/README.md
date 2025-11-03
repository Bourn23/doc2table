# Lumina Frontend

A beautiful, Palantir-inspired UI for the Lumina/EVE knowledge system with phase-based personality transitions.

## 🎨 Design Philosophy

Lumina follows the **"Grounded Transcendence"** design principle:
- Beauty serves function, never obscures it
- Elegant restraint over flashy effects
- Trust through transparency
- Living but restful interface

## ✨ Features

### Phase-Based Personality System

The UI adapts its personality based on what the user is doing:

1. **EVE (Neutral)** - Idle/Resting state
   - Gentle breathing animations
   - Warm silver color palette
   - Tempo: 72-80 BPM

2. **Apollo Mode** - Processing/Strategic analysis
   - Amber-gold accents
   - Methodical, deliberate animations
   - Tempo: 68-75 BPM (contemplative)

3. **Hermes Mode** - Exploration/Quick connections
   - Cyan and violet accents
   - Dynamic, energetic animations
   - Tempo: 96-104 BPM (exploratory)

### UI Components

- **Animated Background**: Living tree visualization that grows with your knowledge
- **Command Palette**: Palantir-style command interface (⌘K / Ctrl+K)
- **Data Grid**: Clean, scannable table with hover interactions
- **Query Interface**: Natural language search with real-time processing
- **Insight Bloom**: Celebration state when insights are discovered

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python backend running (see main project README)

### Installation

```bash
# Navigate to frontend directory
cd lumina-frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Connection

Make sure your Python backend is running:

```bash
# In the parent directory
python app.py
```

The backend should be running at `http://localhost:7860` (default Gradio port).

## 📁 Project Structure

```
lumina-frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── AnimatedBackground.tsx
│   │   └── CommandPalette.tsx
│   ├── phases/              # Phase-specific views
│   │   ├── IdleView.tsx
│   │   ├── ProcessingView.tsx
│   │   └── ExplorationView.tsx
│   ├── store/               # State management (Zustand)
│   │   └── useAppStore.ts
│   ├── styles/              # Design system and global styles
│   │   ├── designTokens.ts
│   │   └── global.css
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts
│   ├── utils/               # Utilities and API client
│   │   └── api.ts
│   ├── App.tsx              # Main app component
│   └── main.tsx             # Entry point
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.js
```

## 🎯 User Flow

### 1. Idle State (EVE)
- User arrives at a peaceful, breathing interface
- Sapling tree visualization
- Upload documents or open command palette

### 2. Processing (Apollo Mode)
- UI shifts to amber-gold tones
- Methodical progress visualization
- Tree grows as documents are processed

### 3. Exploration (Hermes Mode)
- Cyan and violet accents
- Fast, dynamic animations
- Query interface and data grid
- Natural language search

### 4. Insight Bloom
- Pale luminous green-gold glow
- Celebration animation (3-5 seconds)
- Display answer with sources
- Return to exploration mode

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
VITE_API_BASE_URL=http://localhost:7860
```

### Design Tokens

All design tokens are centralized in `src/styles/designTokens.ts`:
- Colors (personality-specific palettes)
- Typography
- Spacing
- Animations
- Shadows

## 🎨 Customization

### Changing Colors

Edit `src/styles/designTokens.ts`:

```typescript
export const colors = {
  apollo: {
    primary: '#d4a574',  // Change Apollo's primary color
    // ...
  },
  // ...
};
```

### Adjusting Animations

Modify animation timings in `src/styles/designTokens.ts`:

```typescript
export const animation = {
  tempo: {
    apollo: 68,  // BPM for Apollo mode
    // ...
  },
};
```

## 🔌 Backend Integration

The frontend expects these backend endpoints:

### POST `/upload`
Upload PDF files for extraction
```typescript
FormData with 'files' field
```

### POST `/index`
Index extracted data for RAG
```typescript
FormData with optional 'csv_file'
```

### POST `/query`
Query indexed data
```typescript
{
  "query": string,
  "num_results": number
}
```

### GET `/export?format=json|csv`
Export extracted data

## 📦 Building for Production

```bash
# Build the app
npm run build

# Preview the build
npm run preview
```

The built files will be in the `dist/` directory.

## 🎭 Accessibility

- Keyboard navigation (Tab, Arrow keys, Enter, Esc)
- Screen reader support
- Reduced motion support (`prefers-reduced-motion`)
- High contrast support
- Focus indicators
- ARIA labels and live regions

## 🐛 Troubleshooting

### Backend connection issues

Make sure the backend is running and CORS is enabled:

```python
# In your Python backend
demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False
)
```

### Slow animations

Check if your browser supports hardware acceleration for canvas rendering.

## 🎯 For Hackathon Demo

Focus on these flows:

1. **Upload Demo**: Show the phase transition from idle → processing → ready
2. **Query Demo**: Demonstrate natural language queries with insight bloom
3. **Personality Modes**: Explain how the UI adapts (Apollo vs Hermes)
4. **Design System**: Showcase the beautiful, restrained aesthetic

## 📚 Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Zustand** - State management
- **Framer Motion** - Animations
- **Tailwind CSS** - Styling
- **Axios** - API client

## 🤝 Contributing

This is a hackathon project. Feel free to iterate and improve!

---

Built with ❤️ following the principles of **Grounded Transcendence**.

*"Wisdom doesn't showboat."*

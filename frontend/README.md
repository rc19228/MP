# 🎨 Frontend - Agentic RAG Dashboard

React-based dark-themed dashboard for financial report analysis with dynamic structured output rendering, glassmorphism UI, and real-time agent workflow visualization.

## ✨ Features

- 🌑 **Pure Black Theme** - Ultra-dark gradients (#000000 → #0a0c10 → #0f1117)
- 🔮 **Glassmorphism UI** - Backdrop blur, transparent cards, smooth transitions
- 📊 **Dynamic SOP Renderer** - Recursive structured output display for any JSON shape
- 🎯 **Upload Modal** - Prominent success popup with suggested prompts
- 📈 **Metrics Dashboard** - Real-time stats with animated cards
- 🤖 **Agent Workflow Viz** - Live pipeline status (Planner → Retriever → Analyzer → Generator → Critic)
- ⚡ **Smooth Animations** - Staggered entrance, hover effects, pulse animations

## 🏗️ Architecture

### Component Hierarchy

```
App.jsx
  │
  ├── Header.jsx                  # Top navigation with logo
  │
  ├── UploadPanel.jsx            # PDF upload with drag & drop
  │   ├── File input (hidden)
  │   ├── Drop zone (click + drag)
  │   └── Success modal
  │
  ├── QueryPanel.jsx             # Query input + submit
  │   ├── Text area
  │   ├── Submit button
  │   └── Loading spinner
  │
  ├── ResultDisplay.jsx          # Query results with SOP
  │   ├── Query header
  │   ├── Plan display
  │   ├── Executive summary
  │   ├── Recursive analysis renderer
  │   ├── Risk factors
  │   ├── Computed metrics table
  │   └── Additional output (unknown fields)
  │
  ├── MetricsPanel.jsx          # Statistics dashboard
  │   ├── Document count card
  │   ├── Chunk count card
  │   ├── Query count card
  │   └── Avg response time card
  │
  └── Footer.jsx                # Bottom credits
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── api.js              # Axios API client with fallbacks
│   │
│   ├── components/
│   │   ├── Header.jsx          # Top navigation bar
│   │   ├── UploadPanel.jsx     # PDF upload + success modal
│   │   ├── QueryPanel.jsx      # Query input interface
│   │   ├── ResultDisplay.jsx   # Dynamic SOP result renderer
│   │   ├── MetricsPanel.jsx    # Statistics cards
│   │   └── Footer.jsx          # Footer component
│   │
│   ├── App.jsx                 # Root component
│   ├── App.css                 # Global styles + animations
│   ├── index.css               # Tailwind imports
│   └── main.jsx                # React entry point
│
├── public/                     # Static assets
├── index.html                  # HTML shell
├── vite.config.js              # Vite config + API proxy
├── tailwind.config.js          # Tailwind theme config
├── postcss.config.js           # PostCSS setup
├── package.json                # Dependencies
└── package-lock.json           # Lock file
```

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `.env` file (optional):

```bash
# API endpoint (defaults to Vite proxy /api)
VITE_API_BASE_URL=http://localhost:8888
```

### 3. Start Development Server

```bash
npm run dev
```

Server will start on `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

Output will be in `dist/` folder.

### 5. Preview Production Build

```bash
npm run preview
```

## 🎨 Theme System

### Color Palette

```css
/* Background Gradients */
--bg-primary: #000000         /* Pure black */
--bg-secondary: #0a0c10       /* Slightly lighter */
--bg-tertiary: #0f1117        /* Card backgrounds */

/* Accents */
--primary: #3b82f6            /* Blue */
--primary-dark: #2563eb
--accent: #8b5cf6             /* Purple */
--accent-dark: #7c3aed

/* Text */
--text-primary: #ffffff       /* White */
--text-secondary: #9ca3af     /* Gray-400 */
--text-muted: #6b7280         /* Gray-500 */

/* Borders */
--border-subtle: #1f2937      /* Gray-800 */
--border-accent: #374151      /* Gray-700 */
```

### Glassmorphism Effects

```css
/* Standard glass card */
.glass-card {
  background: rgba(15, 17, 23, 0.8);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
}

/* Hover effect */
.glass-card:hover {
  background: rgba(15, 17, 23, 0.9);
  border-color: rgba(59, 130, 246, 0.3);
  transform: translateY(-2px);
}
```

### Animation System

```css
/* Entrance animations (staggered) */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeInUp {
  animation: fadeInUp 0.6s ease-out;
}

/* Pulse effect for loading states */
@keyframes pulse-glow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

## 🧩 Component Details

### UploadPanel.jsx

**Features:**
- Hidden file input with ref-based triggering
- Click-to-upload and drag & drop support
- File type validation (.pdf, application/pdf)
- Upload progress indicator
- Success modal popup with:
  - Upload metrics (filename, chunks, status)
  - Suggested query prompts
  - "Go to Query" CTA button
  - "Stay Here" dismiss button

**Key Methods:**
```javascript
handleFileSelect(file)     // Validates and uploads file
handleDrop(e)              // Handles drag & drop events
handleUpload()             // Triggers API upload
closeSuccessPopup()        // Dismisses modal
navigateToQuery()          // Scrolls to query section
```

**State:**
```javascript
const [file, setFile] = useState(null);
const [uploading, setUploading] = useState(false);
const [uploadStatus, setUploadStatus] = useState(null);
const [uploadResult, setUploadResult] = useState(null);
const [showSuccessPopup, setShowSuccessPopup] = useState(false);
const [dragActive, setDragActive] = useState(false);
```

### QueryPanel.jsx

**Features:**
- Multi-line text input
- Submit button with loading state
- Query validation (min 3 chars)
- Loading spinner with animated dots

**Key Methods:**
```javascript
handleSubmit()             // Validates and submits query
```

**State:**
```javascript
const [question, setQuestion] = useState('');
const [loading, setLoading] = useState(false);
```

### ResultDisplay.jsx

**Features:**
- **Dynamic SOP Rendering** - Recursively displays any JSON structure
- Sections: Query, Plan, Executive Summary, Analysis, Risk Factors, Metrics, Additional Output
- Type-based rendering:
  - **Arrays**: Indented divs with left border
  - **Objects**: Each key/value in glass card with uppercase label
  - **Primitives**: Wrapped span with pre-wrap whitespace

**Key Method:**
```javascript
renderValue(value, depth = 0) {
  if (Array.isArray(value)) {
    return value.map((item, i) => (
      <div key={i} className="pl-4 border-l-2" style={depth % 2 === 0 ? blueStyle : purpleStyle}>
        {renderValue(item, depth + 1)}
      </div>
    ));
  }
  
  if (typeof value === 'object' && value !== null) {
    return Object.entries(value).map(([key, val]) => (
      <div key={key} className="glass-card p-3">
        <div className="label">{key.toUpperCase()}</div>
        {renderValue(val, depth + 1)}
      </div>
    ));
  }
  
  return <span className="whitespace-pre-wrap">{String(value)}</span>;
}
```

**Confidence Color Coding:**
- `>= 0.8`: Green (text-green-400)
- `>= 0.6`: Yellow (text-yellow-400)
- `< 0.6`: Red (text-red-400)

### MetricsPanel.jsx

**Features:**
- Four animated stat cards
- Auto-refresh on mount
- Fallback to /health + /history if /stats endpoint unavailable
- Loading skeletons
- Hover effects with scale transform

**State:**
```javascript
const [stats, setStats] = useState({
  total_documents: 0,
  total_chunks: 0,
  queries_processed: 0,
  avg_response_time: 0
});
const [loading, setLoading] = useState(true);
```

## 🔌 API Integration (`api/api.js`)

### API Client Setup

```javascript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Key Functions

#### uploadPDF(file)
```javascript
// Uploads PDF, returns { filename, chunks_created, status }
const formData = new FormData();
formData.append('file', file);
const response = await api.post('/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
```

#### queryDocuments(question)
```javascript
// Queries backend, returns full structured response
const response = await api.post('/query', { question });
// Returns: { query, plan, executive_summary, analysis, risk_factors, confidence, ... }
```

#### getStats()
```javascript
// Gets statistics with fallback logic
try {
  return await api.get('/stats');  // Preferred endpoint
} catch (error) {
  if (error.response?.status === 404) {
    // Fallback: compute from /health + /history
    const [health, history] = await Promise.all([
      api.get('/health'),
      api.get('/history')
    ]);
    return computeStats(health.data, history.data);
  }
}
```

## 🎭 Vite Configuration

### API Proxy (`vite.config.js`)

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8888',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

**Benefits:**
- Avoids CORS issues in development
- Matches production URL structure
- Transparent API routing

## 🧪 Testing

### Manual Testing Checklist

- [ ] Upload PDF via click
- [ ] Upload PDF via drag & drop
- [ ] Success modal appears with metrics
- [ ] "Go to Query" navigates correctly
- [ ] Submit query with valid question
- [ ] Results display with structured output
- [ ] Arrays and objects render correctly
- [ ] Metrics dashboard loads and displays
- [ ] Stats fallback works when /stats unavailable
- [ ] Dark theme consistent across all components
- [ ] Animations play on entrance
- [ ] Hover effects work on all cards

### Browser Compatibility

Tested on:
- Chrome 120+
- Firefox 121+
- Safari 17+
- Edge 120+

## 🎯 Custom Styling

### TailwindCSS Config (`tailwind.config.js`)

```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3b82f6',
          dark: '#2563eb',
        },
        accent: {
          DEFAULT: '#8b5cf6',
          dark: '#7c3aed',
        }
      },
      backdropBlur: {
        'xs': '2px',
        'xl': '16px',
      }
    },
  },
  plugins: [],
}
```

### Custom CSS Classes (`App.css`)

```css
/* Glass effect base */
.glass {
  background: rgba(15, 17, 23, 0.8);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Gradient text */
.gradient-text {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* File upload hover effect */
.file-upload-area:hover {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.05);
}
```

## 🔍 Debugging

### View API Requests

```javascript
// In api.js, add interceptor
api.interceptors.request.use(request => {
  console.log('Starting Request:', request);
  return request;
});

api.interceptors.response.use(response => {
  console.log('Response:', response);
  return response;
});
```

### React DevTools

Install [React Developer Tools](https://react.dev/learn/react-developer-tools) browser extension.

### Vite Debug Mode

```bash
npm run dev -- --debug
```

## 📦 Build Optimization

### Reduce Bundle Size

1. **Code splitting** - Lazy load components:
```javascript
const ResultDisplay = lazy(() => import('./components/ResultDisplay'));
```

2. **Tree shaking** - Import only what you need:
```javascript
import { FileText } from 'lucide-react';  // ✅ Good
import * as Icons from 'lucide-react';     // ❌ Bad
```

3. **Analyze bundle**:
```bash
npm run build -- --mode analyze
```

## 🚨 Common Issues

### Issue: "Cannot connect to backend"
**Solution:** Check that backend is running on port 8888 and Vite proxy is configured correctly.

### Issue: "CORS errors"
**Solution:** Use Vite dev server proxy (already configured). Don't access backend directly at localhost:8888.

### Issue: "Upload modal not showing"
**Solution:** Check that `showSuccessPopup` state is being set to `true` after successful upload. Use React DevTools to inspect state.

### Issue: "Animations not playing"
**Solution:** Ensure `animation-delay` values are correct in CSS. Check browser developer console for CSS errors.

### Issue: "Dark theme looks washed out"
**Solution:** Verify background colors are pure black (`#000000`, not `#0a0a0a`). Check opacity values in glass cards.

## 🎨 Customization Guide

### Change Primary Color

1. Edit `tailwind.config.js`:
```javascript
colors: {
  primary: {
    DEFAULT: '#22c55e',  // Green instead of blue
    dark: '#16a34a',
  }
}
```

2. Update CSS gradients in `App.css`:
```css
.gradient-text {
  background: linear-gradient(135deg, #22c55e 0%, #8b5cf6 100%);
}
```

### Add New Component

1. Create file in `src/components/`
2. Import in `App.jsx`
3. Add to component hierarchy
4. Style with Tailwind + custom classes

### Modify SOP Renderer

Edit `renderValue()` function in `ResultDisplay.jsx`:

```javascript
// Example: Add special rendering for numbers
if (typeof value === 'number') {
  return <span className="text-green-400 font-bold">{value.toFixed(2)}</span>;
}
```

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [Vite Guide](https://vitejs.dev/guide/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)
- [Lucide Icons](https://lucide.dev/)
- [Axios Documentation](https://axios-http.com/docs/intro)

---

**For backend documentation, see [`../backend/README.md`](../backend/README.md)**

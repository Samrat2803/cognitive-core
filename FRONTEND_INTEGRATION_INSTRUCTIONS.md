# Frontend Integration: Live Monitor Dashboard

**Task:** Add Live Political Monitor dashboard to the homepage alongside existing chat interface

**Complexity:** Medium  
**Time Estimate:** 4-6 hours  
**Files to Create:** 3  
**Files to Modify:** 2

---

## 📋 Overview

### Current Layout
```
┌─────────────────────────────────────────┐
│           Header                        │
├─────────────────────────────────────────┤
│                                         │
│                                         │
│         Chat Panel                      │
│       (Master Agent Query)              │
│                                         │
│                                         │
│  [Message Input Box at bottom]          │
└─────────────────────────────────────────┘
```

### New Layout
```
┌─────────────────────────────────────────┐
│           Header                        │
├─────────────────────────────────────────┤
│  🔍 [Keyword Input] [Refresh] [⚙️]      │ ← NEW: Live Monitor Bar
├─────────────────────────────────────────┤
│  ╔═══════════╗  ╔═══════════╗           │
│  ║ 🔴 Topic1 ║  ║ 🟠 Topic2 ║           │ ← NEW: Topic Tiles
│  ║ Score: 85 ║  ║ Score: 72 ║           │
│  ╚═══════════╝  ╚═══════════╝           │
├─────────────────────────────────────────┤
│         Chat Panel                      │ ← EXISTING: Keep as is
│       (Master Agent Query)              │
│  [Message Input Box]                    │
└─────────────────────────────────────────┘
```

---

## 📁 Files to Create

### **1. `src/components/dashboard/LiveMonitorDashboard.tsx`**
### **2. `src/components/dashboard/LiveMonitorDashboard.css`**
### **3. `src/components/dashboard/TopicTile.tsx`**

---

## 📝 Step-by-Step Implementation

---

## **STEP 1: Create TopicTile Component**

**File:** `src/components/dashboard/TopicTile.tsx`

```tsx
import React from 'react';

interface Topic {
  rank: number;
  topic: string;
  explosiveness_score: number;
  classification: string;
  frequency: number;
  image_url?: string;  // NEW: Image from news source
  entities?: {
    people?: string[];
    countries?: string[];
    organizations?: string[];
  };
  reasoning: string;
}

interface TopicTileProps {
  topic: Topic;
}

export function TopicTile({ topic }: TopicTileProps) {
  // Determine color based on classification
  const getColorClasses = (classification: string) => {
    if (classification.includes('CRITICAL')) {
      return {
        bg: 'bg-red-50',
        border: 'border-red-400',
        badge: 'bg-red-500',
        text: 'text-red-900'
      };
    }
    if (classification.includes('EXPLOSIVE')) {
      return {
        bg: 'bg-orange-50',
        border: 'border-orange-400',
        badge: 'bg-orange-500',
        text: 'text-orange-900'
      };
    }
    if (classification.includes('TRENDING')) {
      return {
        bg: 'bg-yellow-50',
        border: 'border-yellow-400',
        badge: 'bg-yellow-500',
        text: 'text-yellow-900'
      };
    }
    return {
      bg: 'bg-green-50',
      border: 'border-green-400',
      badge: 'bg-green-500',
      text: 'text-green-900'
    };
  };

  const colors = getColorClasses(topic.classification);

  return (
    <div 
      className={`topic-tile ${colors.bg} border-2 ${colors.border} rounded-lg overflow-hidden hover:shadow-lg transition-shadow cursor-pointer`}
      style={{
        minHeight: '250px',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* Image (if available) */}
      {topic.image_url && (
        <div className="w-full h-32 bg-gray-200 overflow-hidden">
          <img 
            src={topic.image_url} 
            alt={topic.topic}
            className="w-full h-full object-cover"
            onError={(e) => {
              // Hide image if it fails to load
              e.currentTarget.style.display = 'none';
            }}
          />
        </div>
      )}
      
      <div className="p-4 flex-1 flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-start mb-3">
          <span className="text-sm font-semibold text-gray-500">
            #{topic.rank}
          </span>
          <span className="text-lg">
            {topic.classification.split(' ')[0]} {/* Emoji only */}
          </span>
        </div>

        {/* Title */}
        <h3 className={`text-base font-bold ${colors.text} mb-3 line-clamp-2`}>
          {topic.topic}
        </h3>

      {/* Metrics */}
      <div className="flex gap-2 mb-3">
        <span className={`${colors.badge} text-white text-xs font-bold px-2 py-1 rounded`}>
          {topic.explosiveness_score}/100
        </span>
        <span className="bg-gray-200 text-gray-700 text-xs px-2 py-1 rounded">
          {topic.frequency} articles
        </span>
      </div>

      {/* Entities */}
      {topic.entities && (
        <div className="text-xs text-gray-600 mb-3 space-y-1">
          {topic.entities.people && topic.entities.people.length > 0 && (
            <div className="truncate">
              👤 {topic.entities.people.slice(0, 2).join(', ')}
            </div>
          )}
          {topic.entities.countries && topic.entities.countries.length > 0 && (
            <div className="truncate">
              🌍 {topic.entities.countries.slice(0, 2).join(', ')}
            </div>
          )}
        </div>
      )}

        {/* Reasoning */}
        <p className="text-xs text-gray-600 line-clamp-3 mt-auto">
          {topic.reasoning}
        </p>
      </div>
    </div>
  );
}
```

---

## **STEP 2: Create LiveMonitorDashboard Component**

**File:** `src/components/dashboard/LiveMonitorDashboard.tsx`

```tsx
import React, { useState } from 'react';
import { TopicTile } from './TopicTile';
import './LiveMonitorDashboard.css';

interface Topic {
  rank: number;
  topic: string;
  explosiveness_score: number;
  classification: string;
  frequency: number;
  image_url?: string;  // NEW: Image from news source
  entities?: any;
  reasoning: string;
}

interface CacheInfo {
  source: string;
  cachedAt: string;
  expiresInMinutes: number;
}

export function LiveMonitorDashboard() {
  // State
  const [keywords, setKeywords] = useState('Bihar, corruption, India politics');
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cacheInfo, setCacheInfo] = useState<CacheInfo | null>(null);
  const [cacheHours, setCacheHours] = useState(3);

  // API call
  const handleRefresh = async () => {
    setLoading(true);
    setError(null);

    try {
      const keywordArray = keywords
        .split(',')
        .map(k => k.trim())
        .filter(k => k.length > 0);

      if (keywordArray.length === 0) {
        setError('Please enter at least one keyword');
        setLoading(false);
        return;
      }

      const response = await fetch('/api/live-monitor/explosive-topics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keywords: keywordArray,
          cache_hours: cacheHours,
          max_results: 10,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setTopics(data.topics);
        setCacheInfo({
          source: data.source,
          cachedAt: data.cached_at,
          expiresInMinutes: data.cache_expires_in_minutes,
        });
      } else {
        setError('Failed to fetch topics');
      }
    } catch (err) {
      console.error('Error fetching topics:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Handle Enter key in input
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !loading) {
      handleRefresh();
    }
  };

  return (
    <div className="live-monitor-dashboard">
      {/* Control Bar */}
      <div className="monitor-control-bar">
        <div className="control-left">
          <label className="control-label">🔍 Focus Keywords:</label>
          <input
            type="text"
            className="keyword-input"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter keywords (comma-separated)"
            disabled={loading}
          />
        </div>

        <div className="control-right">
          <select
            className="cache-select"
            value={cacheHours}
            onChange={(e) => setCacheHours(Number(e.target.value))}
            disabled={loading}
          >
            <option value={1}>1 hour</option>
            <option value={3}>3 hours</option>
            <option value={6}>6 hours</option>
            <option value={12}>12 hours</option>
            <option value={24}>24 hours</option>
          </select>

          <button
            className="refresh-button"
            onClick={handleRefresh}
            disabled={loading}
          >
            {loading ? (
              <>⏳ Loading...</>
            ) : (
              <>🔄 Refresh</>
            )}
          </button>
        </div>
      </div>

      {/* Cache Info */}
      {cacheInfo && !loading && (
        <div className="cache-info">
          {cacheInfo.source === 'cache' ? '📦 Cached' : '🔄 Fresh'} •
          Expires in {cacheInfo.expiresInMinutes} minutes •
          {topics.length} topics found
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {/* Topics Grid */}
      {!loading && topics.length > 0 && (
        <div className="topics-grid">
          {topics.map((topic) => (
            <TopicTile key={topic.rank} topic={topic} />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && topics.length === 0 && !error && (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <h3>No explosive topics yet</h3>
          <p>Enter keywords and click Refresh to discover trending political topics</p>
        </div>
      )}

      {/* Loading Skeleton */}
      {loading && (
        <div className="loading-skeleton">
          <div className="skeleton-grid">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="skeleton-tile"></div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## **STEP 3: Create Styles**

**File:** `src/components/dashboard/LiveMonitorDashboard.css`

```css
/* Live Monitor Dashboard Styles */
.live-monitor-dashboard {
  background: linear-gradient(to bottom, #fafafa, #ffffff);
  padding: 1.5rem;
  border-bottom: 2px solid #e5e5e5;
}

/* Control Bar */
.monitor-control-bar {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.control-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 300px;
}

.control-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
}

.keyword-input {
  flex: 1;
  padding: 0.6rem 1rem;
  border: 2px solid #d9f378; /* Aistra green */
  border-radius: 8px;
  font-size: 0.95rem;
  background: white;
  transition: all 0.2s;
}

.keyword-input:focus {
  outline: none;
  border-color: #5d535c; /* Aistra grey */
  box-shadow: 0 0 0 3px rgba(217, 243, 120, 0.2);
}

.keyword-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.control-right {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.cache-select {
  padding: 0.6rem 0.8rem;
  border: 2px solid #e5e5e5;
  border-radius: 8px;
  font-size: 0.9rem;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.cache-select:hover {
  border-color: #d9f378;
}

.refresh-button {
  padding: 0.6rem 1.5rem;
  background: #d9f378; /* Aistra green */
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  color: #1c1e20; /* Aistra black */
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.refresh-button:hover:not(:disabled) {
  background: #c9e368;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(217, 243, 120, 0.4);
}

.refresh-button:active:not(:disabled) {
  transform: translateY(0);
}

.refresh-button:disabled {
  background: #e5e5e5;
  color: #999;
  cursor: not-allowed;
}

/* Cache Info */
.cache-info {
  font-size: 0.85rem;
  color: #666;
  padding: 0.5rem 1rem;
  background: #f9f9f9;
  border-radius: 6px;
  margin-bottom: 1rem;
  text-align: center;
}

/* Error Message */
.error-message {
  padding: 1rem;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  color: #c33;
  margin-bottom: 1rem;
  text-align: center;
}

/* Topics Grid */
.topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
  max-height: 400px;
  overflow-y: auto;
  padding: 0.5rem;
}

/* Scrollbar Styling */
.topics-grid::-webkit-scrollbar {
  width: 8px;
}

.topics-grid::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.topics-grid::-webkit-scrollbar-thumb {
  background: #d9f378;
  border-radius: 4px;
}

.topics-grid::-webkit-scrollbar-thumb:hover {
  background: #c9e368;
}

/* Topic Tile (base styles, rest in component) */
.topic-tile {
  transition: all 0.2s;
}

.topic-tile:hover {
  transform: translateY(-2px);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #666;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin-bottom: 0.5rem;
  color: #333;
}

.empty-state p {
  color: #999;
  font-size: 0.9rem;
}

/* Loading Skeleton */
.loading-skeleton {
  margin-top: 1rem;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.skeleton-tile {
  height: 200px;
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
  border-radius: 8px;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .monitor-control-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .control-left,
  .control-right {
    width: 100%;
  }

  .topics-grid {
    grid-template-columns: 1fr;
    max-height: 300px;
  }
}
```

---

## **STEP 4: Modify MainLayout.tsx**

**File:** `src/components/layout/MainLayout.tsx`

**Changes:**
1. Import LiveMonitorDashboard
2. Add dashboard above ChatPanel

```tsx
import { useState } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { Header } from './Header';
import { ChatPanel } from '../chat/ChatPanel';
import { ArtifactPanel, type Artifact } from '../artifact/ArtifactPanel';
import { LiveMonitorDashboard } from '../dashboard/LiveMonitorDashboard'; // NEW
import './MainLayout.css';

export function MainLayout() {
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [selectedArtifactIndex, setSelectedArtifactIndex] = useState<number>(0);

  const handleArtifactReceived = (artifact: Artifact) => {
    console.log('📊 MainLayout: New artifact received:', {
      artifact_id: artifact.artifact_id,
      title: artifact.title,
      type: artifact.type,
      status: artifact.status,
      has_png: !!artifact.png_url,
      has_html: !!artifact.html_url
    });
    
    setArtifacts(prev => {
      const exists = prev.find(a => a.artifact_id === artifact.artifact_id);
      if (exists) {
        console.log('   ℹ️  Artifact already exists, skipping duplicate');
        return prev;
      }
      
      const updated = [...prev, artifact];
      console.log(`   ✅ Added artifact. Total artifacts: ${updated.length}`);
      console.log(`   🎯 Setting selected index to: ${updated.length - 1}`);
      
      setSelectedArtifactIndex(updated.length - 1);
      
      return updated;
    });
  };

  const handleCloseArtifact = () => {
    setArtifacts([]);
    setSelectedArtifactIndex(0);
  };

  const handleSelectArtifact = (index: number) => {
    setSelectedArtifactIndex(index);
    console.log(`📊 Switched to artifact ${index + 1} of ${artifacts.length}`);
  };

  const currentArtifact = artifacts[selectedArtifactIndex] || null;

  console.log('🔍 MainLayout State:', {
    artifactsCount: artifacts.length,
    selectedIndex: selectedArtifactIndex,
    hasCurrentArtifact: !!currentArtifact,
    panelShouldShow: artifacts.length > 0
  });

  return (
    <div className="main-layout">
      <Header />
      
      {/* NEW: Live Monitor Dashboard */}
      <LiveMonitorDashboard />
      
      <div className="content">
        <PanelGroup direction="horizontal">
          {/* Left Panel - Chat */}
          <Panel 
            defaultSize={artifacts.length > 0 ? 50 : 100} 
            minSize={30}
          >
            <ChatPanel onArtifactReceived={handleArtifactReceived} />
          </Panel>

          {/* Right Panel - Artifacts (conditional) */}
          {artifacts.length > 0 && (
            <>
              <PanelResizeHandle className="resize-handle">
                <div className="resize-handle-line" />
              </PanelResizeHandle>

              <Panel 
                defaultSize={50} 
                minSize={20}
                collapsible
                onCollapse={handleCloseArtifact}
              >
                <ArtifactPanel 
                  key={currentArtifact.artifact_id}
                  artifacts={artifacts}
                  selectedIndex={selectedArtifactIndex}
                  onSelectArtifact={handleSelectArtifact}
                  onClose={handleCloseArtifact} 
                />
              </Panel>
            </>
          )}
        </PanelGroup>
      </div>
    </div>
  );
}
```

---

## **STEP 5: Update MainLayout.css (Optional)**

**File:** `src/components/layout/MainLayout.css`

Add these styles if needed:

```css
/* Ensure dashboard doesn't take up too much space */
.main-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

/* Content area should flex */
.content {
  flex: 1;
  overflow: hidden;
}
```

---

## 🎨 Styling with Aistra Color Palette

The design uses your specified colors:

```css
/* Aistra Colors */
--aistra-green: #d9f378;
--aistra-grey: #5d535c;
--aistra-dark: #333333;
--aistra-black: #1c1e20;

/* Applied in:*/
- Input borders: #d9f378
- Button background: #d9f378
- Button text: #1c1e20
- Focus colors: #5d535c
```

---

## ✅ Testing Checklist

### **1. Visual Tests**
- [ ] Dashboard appears above chat panel
- [ ] Keyword input is visible and editable
- [ ] Refresh button is clickable
- [ ] Cache duration dropdown works
- [ ] Empty state shows when no topics

### **2. Functional Tests**
- [ ] Enter keywords "Bihar, corruption, India"
- [ ] Click Refresh
- [ ] Topics load within 30 seconds
- [ ] Tiles display with correct colors
- [ ] Scores and entities show correctly
- [ ] Click Refresh again → instant (cached)
- [ ] Change keywords → fetch fresh data

### **3. Error Handling**
- [ ] Empty keywords → shows error
- [ ] API down → shows error message
- [ ] Network timeout → graceful failure

### **4. Responsiveness**
- [ ] Mobile: Input stacks vertically
- [ ] Mobile: Grid becomes single column
- [ ] Tablet: 2-column grid
- [ ] Desktop: 3-4 column grid

---

## 🐛 Troubleshooting

### **Issue: "Failed to fetch"**
**Solution:** 
- Check backend is running on port 8001
- Verify API endpoint is correct
- Check CORS settings

### **Issue: "No topics returned"**
**Solution:**
- Try different keywords (e.g., "Ukraine, war")
- Check backend logs
- Verify Tavily API key is set

### **Issue: Tiles not rendering**
**Solution:**
- Check browser console for errors
- Verify `TopicTile` component is imported
- Check that `topics` state has data

---

## 📱 Example API Response (for reference)

```json
{
  "success": true,
  "source": "fresh",
  "cached_at": "2025-10-02T14:30:24",
  "cache_expires_in_minutes": 180,
  "keywords_used": ["Bihar", "corruption"],
  "topics": [
    {
      "rank": 1,
      "topic": "CBI raids 15 Bihar offices",
      "explosiveness_score": 76,
      "classification": "🔴 CRITICAL",
      "frequency": 5,
      "image_url": "https://example.com/news/image.jpg",
      "entities": {
        "people": ["Nitish Kumar"],
        "countries": ["India"],
        "organizations": ["CBI"]
      },
      "reasoning": "Major investigation..."
    }
  ],
  "total_articles_analyzed": 33,
  "processing_time_seconds": 25.9
}
```

---

## 🚀 Deployment Notes

1. **Build Test:** Run `npm run build` to ensure no TypeScript errors
2. **API Proxy:** Update `vite.config.ts` to proxy `/api` to `http://localhost:8001`
3. **Environment:** Set `VITE_API_URL` if deploying separately

---

## ⏱️ Estimated Timeline

| Task | Time |
|------|------|
| Create TopicTile component | 1 hour |
| Create LiveMonitorDashboard | 2 hours |
| Add to MainLayout | 30 min |
| Styling & polish | 1.5 hours |
| Testing & bug fixes | 1 hour |
| **Total** | **6 hours** |

---

## 📞 Need Help?

- Backend API documentation: `backend_v2/LIVE_MONITOR_COMPLETE.md`
- Test API: `curl -X POST http://localhost:8001/api/live-monitor/explosive-topics -H "Content-Type: application/json" -d '{"keywords": ["test"]}'`
- Check backend logs if API fails

---

**Status:** Ready for implementation ✅  
**Priority:** High  
**Dependencies:** Backend server must be running on port 8001


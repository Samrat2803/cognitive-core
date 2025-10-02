# Live Topic Carousel - Setup Instructions

## 🎯 Overview

A professional auto-scrolling horizontal carousel for displaying live explosive political topics with smooth animations, responsive design, and interactive features.

---

## 📦 Installation

### **File:** `Frontend_v2/package.json`

You need to install Swiper.js library (no version number per your rules):

```bash
cd Frontend_v2
source .venv/bin/activate  # If using Python venv
npm install swiper
```

Or if you prefer yarn:
```bash
yarn add swiper
```

---

## ✅ Files Created

The following files have been created in **`Frontend_v2/src/components/dashboard/`**:

1. ✅ **TopicCard.tsx** - Individual topic card component
2. ✅ **TopicModal.tsx** - Detailed view modal when card is clicked
3. ✅ **TopicCarousel.tsx** - Main carousel with Swiper integration
4. ✅ **TopicCarousel.css** - Carousel styling with Aistra colors
5. ✅ **LiveMonitorDashboard.tsx** - Dashboard container with controls
6. ✅ **LiveMonitorDashboard.css** - Dashboard styling

---

## ✅ Files Modified

1. ✅ **MainLayout.tsx** - Added LiveMonitorDashboard import and component

---

## 🎨 Features Implemented

### **Carousel Features:**
- ✅ Auto-scrolling every 4 seconds
- ✅ Pause on hover (for reading)
- ✅ Previous/Next navigation arrows
- ✅ Progress dots indicator
- ✅ Touch/swipe support for mobile
- ✅ Infinite loop (seamless)
- ✅ Smooth slide transitions (500ms)

### **Responsive Breakpoints:**
- **Mobile (< 640px):** 1 card visible
- **Tablet (640-1024px):** 2 cards visible
- **Desktop (1024-1280px):** 3 cards visible
- **Large Desktop (> 1280px):** 4 cards visible

### **Interactive Features:**
- ✅ Click card → Open detailed modal
- ✅ Modal shows full topic info, entities, analysis
- ✅ Press ESC or click outside to close modal
- ✅ Real-time pause indicator when hovering

### **Design:**
- ✅ Aistra color palette (#d9f378, #5d535c, #333333, #1c1e20)
- ✅ Roboto Flex font (Google Font)
- ✅ Gradient backgrounds with animations
- ✅ Glowing effects on hover
- ✅ Loading skeleton with shimmer effect
- ✅ Empty state with helpful message

---

## 🚀 Running the Application

### **1. Start Backend (Port 8001)**
```bash
cd backend_v2
source .venv/bin/activate
python app.py
```

### **2. Start Frontend (Port 5173)**
```bash
cd Frontend_v2
npm run dev
```

### **3. Open Browser**
Navigate to: `http://localhost:5173`

---

## 🧪 Testing the Carousel

### **Step 1: Test Default View**
1. Open the application
2. You should see the Live Monitor Dashboard at the top
3. Default keywords: "Bihar, corruption, India politics"
4. Click **"🔄 Refresh"** button

### **Step 2: Test Carousel**
1. Wait ~30 seconds for topics to load
2. Carousel should auto-scroll every 4 seconds
3. Hover over carousel → Should pause (see "⏸️ Paused" indicator)
4. Move mouse away → Auto-scroll resumes
5. Click arrow buttons → Manual navigation
6. Click pagination dots → Jump to specific slide

### **Step 3: Test Topic Card**
1. Click any topic card
2. Modal should open with full details
3. Check:
   - Title, rank, classification
   - Explosiveness score
   - Entity lists (people, countries, organizations)
   - Full reasoning/analysis
4. Press ESC or click outside → Modal closes

### **Step 4: Test Responsiveness**
1. Resize browser window
2. Watch cards adjust:
   - Large: 4 cards
   - Medium: 3 cards
   - Tablet: 2 cards
   - Mobile: 1 card

### **Step 5: Test Different Keywords**
1. Enter: "Ukraine, war, Russia"
2. Click Refresh
3. New topics should load in carousel
4. Carousel resets to first slide

---

## 🎨 Color Scheme (Aistra Palette)

```css
/* Used throughout the carousel */
--aistra-green: #d9f378;     /* Buttons, accents, highlights */
--aistra-grey: #5d535c;      /* Secondary elements */
--aistra-dark: #333333;      /* Text, borders */
--aistra-black: #1c1e20;     /* Background, containers */

/* Topic Card Colors (by classification) */
--critical-red: #ef4444;     /* 🔴 CRITICAL topics */
--explosive-orange: #f97316; /* 🟠 EXPLOSIVE topics */
--trending-yellow: #eab308;  /* 🟡 TRENDING topics */
--normal-green: #22c55e;     /* 🟢 NORMAL topics */
```

---

## 🐛 Troubleshooting

### **Issue 1: Swiper not defined**
**Error:** `Cannot find module 'swiper'`
**Solution:**
```bash
cd Frontend_v2
npm install swiper
```

### **Issue 2: Carousel not visible**
**Solution:**
- Check backend is running on port 8001
- Check browser console for errors
- Verify `LiveMonitorDashboard` is imported in `MainLayout.tsx`

### **Issue 3: Topics not loading**
**Solution:**
- Click Refresh button
- Check backend logs for errors
- Verify Tavily API key is set in backend `.env`
- Try different keywords

### **Issue 4: Auto-scroll not working**
**Solution:**
- Make sure you have more than 3 topics (loop requires > visible cards)
- Check browser console for Swiper errors
- Verify Swiper CSS is imported in `TopicCarousel.tsx`

### **Issue 5: Styling issues**
**Solution:**
- Clear browser cache (Cmd+Shift+R / Ctrl+Shift+R)
- Verify CSS files are imported
- Check for CSS conflicts in browser DevTools

---

## 📁 Project Structure

```
Frontend_v2/
├── src/
│   ├── components/
│   │   ├── dashboard/          ← NEW FOLDER
│   │   │   ├── TopicCard.tsx
│   │   │   ├── TopicModal.tsx
│   │   │   ├── TopicCarousel.tsx
│   │   │   ├── TopicCarousel.css
│   │   │   ├── LiveMonitorDashboard.tsx
│   │   │   └── LiveMonitorDashboard.css
│   │   │
│   │   └── layout/
│   │       └── MainLayout.tsx   ← MODIFIED
│   │
│   └── ...
└── package.json                 ← UPDATE (add swiper)
```

---

## 🔄 API Integration

### **Endpoint Used:**
```
POST /api/live-monitor/explosive-topics
```

### **Request Body:**
```json
{
  "keywords": ["Bihar", "corruption"],
  "cache_hours": 3,
  "max_results": 10
}
```

### **Response Format:**
```json
{
  "success": true,
  "source": "fresh",
  "cached_at": "2025-10-02T14:30:24",
  "cache_expires_in_minutes": 180,
  "topics": [
    {
      "rank": 1,
      "topic": "CBI raids 15 Bihar offices",
      "explosiveness_score": 76,
      "classification": "🔴 CRITICAL",
      "frequency": 5,
      "entities": {
        "people": ["Nitish Kumar"],
        "countries": ["India"],
        "organizations": ["CBI"]
      },
      "reasoning": "Major investigation..."
    }
  ]
}
```

---

## ⚡ Performance Notes

- **Lazy Loading:** Cards load only when visible
- **Smooth Animations:** Hardware-accelerated CSS transforms
- **Optimized Images:** No heavy assets
- **Debounced Scroll:** Prevents excessive re-renders
- **Cached Data:** Backend caches responses for faster loads

---

## 🎯 Next Steps (Optional Enhancements)

If you want to add more features later:

1. **WebSocket Integration:** Real-time topic updates without refresh
2. **Auto-Refresh:** Poll API every 5 minutes automatically
3. **Filtering:** Filter by classification (CRITICAL, EXPLOSIVE, etc.)
4. **Sorting:** Sort by score, frequency, or date
5. **Bookmarks:** Save favorite topics
6. **Share:** Share topic cards on social media
7. **Export:** Download topics as PDF/CSV
8. **Analytics:** Track which topics get the most clicks

---

## 📞 Support

If you encounter issues:
1. Check browser console for errors
2. Verify backend is running and accessible
3. Check backend logs: `backend_v2/app.py`
4. Test API directly: 
   ```bash
   curl -X POST http://localhost:8001/api/live-monitor/explosive-topics \
     -H "Content-Type: application/json" \
     -d '{"keywords": ["test"]}'
   ```

---

**Status:** ✅ Ready for Testing  
**Priority:** High  
**Estimated Setup Time:** 5 minutes  
**Estimated Testing Time:** 10 minutes

---

## 🎉 Final Checklist

Before considering this complete:

- [ ] Install Swiper: `npm install swiper`
- [ ] Backend running on port 8001
- [ ] Frontend running on port 5173
- [ ] Dashboard visible at top of page
- [ ] Can enter keywords and refresh
- [ ] Topics load in carousel
- [ ] Auto-scroll works (every 4s)
- [ ] Hover pauses carousel
- [ ] Navigation arrows work
- [ ] Click card opens modal
- [ ] Modal shows full details
- [ ] ESC closes modal
- [ ] Responsive on mobile/tablet/desktop

Enjoy your professional live topic carousel! 🚀


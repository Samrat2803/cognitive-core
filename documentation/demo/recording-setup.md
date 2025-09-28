# Demo Recording Setup Guide

## 🎥 **Required Software**

### **Screen Recording (Choose One)**
- **OBS Studio** (Free, Recommended)
  - Download: https://obsproject.com/
  - Professional features, customizable layouts
  - Best for high-quality recordings

- **Camtasia** (Paid)
  - Professional screen recording and editing
  - Built-in editing features
  - Easier for beginners

- **QuickTime Player** (Mac Only)
  - Simple, built-in option
  - Basic recording capabilities
  - Good for quick demos

### **Audio Editing (Optional)**
- **Audacity** (Free) - Basic audio editing
- **Adobe Audition** (Paid) - Professional audio editing
- **GarageBand** (Mac) - User-friendly audio editing

### **Video Editing (Optional)**
- **DaVinci Resolve** (Free) - Professional video editing
- **Adobe Premiere Pro** (Paid) - Industry standard
- **iMovie** (Mac) - Simple editing

## 🖥 **Screen & Display Setup**

### **Optimal Screen Configuration**
```bash
# Set screen resolution for recording
Resolution: 1920x1080 (Full HD)
Aspect Ratio: 16:9
Color Depth: 32-bit
Refresh Rate: 60Hz or higher

# Browser setup for recording
- Use Chrome or Firefox in full-screen mode (F11)
- Hide bookmarks bar (Ctrl+Shift+B / Cmd+Shift+B)  
- Clear browser cache and history
- Disable browser notifications
- Close unnecessary tabs
- Set zoom level to 100%
```

### **OBS Studio Configuration**
```yaml
# Scene Setup
Sources:
  - Display Capture (Full Screen 1920x1080)
  - Audio Input Capture (Microphone)
  - Audio Output Capture (Desktop Audio - optional)

# Recording Settings
Output Mode: Simple
Recording Quality: High Quality, Medium File Size
Recording Format: MP4
Encoder: Hardware (NVENC/QuickSync) or x264
Rate Control: CBR
Bitrate: 8000-12000 Kbps

# Video Settings
Base Resolution: 1920x1080
Output Resolution: 1920x1080
FPS: 60 (Common Values: 60)

# Audio Settings
Sample Rate: 44.1 kHz
Channels: Stereo
```

## 🎤 **Audio Setup**

### **Microphone Recommendations**
- **Built-in laptop mic:** Acceptable if clear
- **USB Microphone:** Blue Yeti, Audio-Technica ATR2100x-USB
- **Headset with mic:** Professional headset with noise cancellation
- **Smartphone earbuds:** Can work as backup option

### **Audio Environment**
```bash
# Recording Environment
- Choose quiet room with minimal echo
- Close windows to reduce outside noise
- Turn off fans, air conditioning during recording
- Use soft furnishings to reduce echo (blankets, pillows)
- Record during quiet hours

# Audio Testing
- Test microphone levels before recording
- Speak at consistent volume and pace
- Leave 2-second pauses between major sections
- Practice pronunciation of technical terms
```

### **Audio Settings Checklist**
- [ ] Microphone gain set appropriately (not too loud/soft)
- [ ] Background noise minimized
- [ ] Test recording 30 seconds of speech
- [ ] Check for echo or distortion
- [ ] Ensure consistent audio levels

## 🌐 **Browser & Application Setup**

### **Chrome/Firefox Configuration**
```javascript
// Browser settings for clean recording
Settings to configure:
- Disable "Translate" prompts
- Turn off password save prompts  
- Disable autofill suggestions
- Hide bookmark bar
- Set homepage to blank page
- Clear browsing data

// Developer Tools Setup (for mobile demo)
- Press F12 to open dev tools
- Click device simulation icon
- Select iPhone 12 Pro (390x844) or similar
- Test responsive layout before recording
```

### **Desktop Cleanup**
```bash
# Clean desktop for professional appearance
- Hide desktop icons
- Use clean, professional wallpaper  
- Close unnecessary applications
- Turn off notifications (Do Not Disturb mode)
- Hide system tray icons
- Set taskbar/dock to auto-hide (optional)
```

## 📱 **Mobile Responsiveness Demo**

### **Chrome DevTools Setup**
```bash
1. Open Chrome Developer Tools (F12)
2. Click "Toggle device toolbar" icon (Ctrl+Shift+M)
3. Select device: iPhone 12 Pro (390x844)
4. Set throttling to "No throttling" for smooth demo
5. Rotate to test landscape mode if needed

# Test interactions before recording:
- Touch/click responsiveness
- Scroll behavior  
- Button sizing and usability
- Text readability at mobile size
```

## 🎨 **Visual Assets Creation**

### **Architecture Diagram**
```bash
# Tools for creating diagrams
- Draw.io (free, online): https://app.diagrams.net/
- Lucidchart (paid): Professional diagrams
- Figma (free tier): Design and collaboration
- PowerPoint/Keynote: Simple diagrams

# Diagram Requirements:
- Show 4 agents in sequence
- Include LangGraph state transitions
- Add database and API connections
- Use consistent color scheme (optional: Aistra palette)
- Export as PNG at high resolution (300 DPI)
```

### **Title Cards and Overlays**
```bash
# Create title cards (1920x1080)
Tools: Canva, Adobe Photoshop, GIMP, PowerPoint

Required title cards:
- "Web Research Agent"
- "Multi-Agent System" 
- "Built with LangGraph + Tavily"
- "Production Ready"
- "Thank you!"

# Text overlay specifications:
Font: Roboto Flex (or clean sans-serif)
Colors: Professional palette
- Primary: #333333 (dark text)
- Accent: #d9f378 (highlight color)
- Background: White or transparent

# Export settings:
Format: PNG with transparency
Resolution: 1920x1080
DPI: 300 for crisp quality
```

## 📊 **Demo Data Preparation**

### **Test Queries**
```bash
# Primary demo queries (have these ready):
1. "What are the latest developments in quantum computing for 2024?"
2. "How does climate change affect renewable energy adoption?"

# Backup queries (in case of issues):
3. "What is the impact of artificial intelligence on healthcare?"
4. "What are the recent breakthroughs in renewable energy technology?"
5. "How is blockchain technology being used in supply chain management?"

# Pre-test all queries:
- Verify they return good results
- Check processing time (should be 45-90 seconds)
- Ensure diverse source types in results
- Confirm export functionality works
```

### **System Preparation**
```bash
# Before recording session:
- Clear browser cache and cookies
- Restart browser to ensure clean state
- Test API keys are working
- Verify database connection
- Check AWS deployment status
- Ensure all services are running

# Have ready in browser tabs:
1. Frontend application (primary tab)
2. MongoDB Atlas dashboard
3. AWS Elastic Beanstalk dashboard
4. Backup frontend URL (if available)
```

## 🎬 **Recording Best Practices**

### **Cursor and Mouse Movement**
```bash
# Professional cursor behavior:
- Move cursor smoothly, not too fast
- Pause briefly before clicking elements
- Don't wave cursor around unnecessarily
- Use keyboard shortcuts when appropriate
- Click precisely on buttons/elements
```

### **Timing and Pacing**
```bash
# Scene timing guidelines:
- Introduction: 30 seconds (tight, engaging)
- Architecture: 30 seconds (clear explanation)
- Demo 1: 75 seconds (complete workflow)
- Features: 45 seconds (focused showcase)  
- Backend/Analytics: 45 seconds (impressive infrastructure)
- Demo 2: 15 seconds (quick, sped up)
- Conclusion: 15 seconds (strong finish)

Total: 4 minutes exactly

# Narration tips:
- Speak clearly and at moderate pace
- Pause briefly between sentences
- Emphasize key technical terms
- Maintain professional, confident tone
- Practice transitions between sections
```

## 🔧 **Troubleshooting Common Issues**

### **Recording Problems**
```bash
# Video issues:
- Choppy recording: Lower frame rate to 30fps, close other apps
- Large file size: Adjust bitrate settings, use hardware encoding
- Audio sync: Record video and audio separately if needed

# Audio issues:  
- Background noise: Use noise suppression in OBS
- Low volume: Increase microphone gain (test first)
- Echo: Move closer to mic, add soft furnishings to room

# System performance:
- Close unnecessary applications
- Disable real-time antivirus scanning temporarily
- Use SSD storage for recording if available
- Monitor CPU/memory usage during recording
```

### **Demo Failures**
```bash
# If live system fails during recording:
- Have backup screen recordings ready
- Switch to localhost development version
- Prepare to narrate over pre-recorded footage
- Keep demo data and screenshots as backup

# Network issues:
- Test internet connection speed beforehand
- Use mobile hotspot as backup
- Have offline demo data prepared
- Consider recording in segments
```

## ✅ **Pre-Recording Checklist**

### **Technical Setup** (30 minutes before)
- [ ] Audio levels tested and optimized
- [ ] Screen resolution set to 1920x1080
- [ ] Recording software configured and tested
- [ ] Browser cleaned and configured
- [ ] Demo queries tested and working
- [ ] Backup plans prepared

### **Content Preparation** (15 minutes before)
- [ ] Script reviewed and practiced
- [ ] Demo flow rehearsed end-to-end
- [ ] Timing verified for each section
- [ ] MongoDB and AWS dashboards accessible
- [ ] Professional appearance confirmed

### **Final Check** (5 minutes before)
- [ ] Do Not Disturb mode enabled
- [ ] All notifications disabled
- [ ] Backup recording started (if possible)
- [ ] Water nearby for clear speech
- [ ] Timer/stopwatch ready for timing

## 🎯 **Quality Standards**

### **Video Quality**
- **Resolution:** 1920x1080 minimum
- **Frame Rate:** 60fps for smooth motion
- **Bitrate:** 8000+ kbps for clarity
- **Duration:** Exactly 4 minutes (±5 seconds)

### **Audio Quality**
- **Sample Rate:** 44.1kHz
- **Format:** WAV or high-quality MP3
- **Levels:** Consistent throughout, no clipping
- **Clarity:** Clear speech, minimal background noise

### **Content Quality**
- **Flow:** Smooth transitions, logical progression
- **Technical:** All features work as demonstrated
- **Professional:** Polished presentation, confident delivery
- **Complete:** Covers all required elements from script

**Following this setup guide ensures a professional, high-quality demo video that effectively showcases the multi-agent research system.**

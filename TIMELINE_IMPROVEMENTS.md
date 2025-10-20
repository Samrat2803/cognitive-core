# Timeline Visualization Improvements

## What Changed

### Before ❌
- **Iteration-based scatter plot** with X-axis showing iteration numbers
- Facts distributed across iterations (confusing)
- Y-axis showed truncated fact text (hard to read)
- Legend showing "Category: Discovery" (redundant)
- No clear chronological flow

### After ✅
- **Clean linear timeline** with vertical flow (top to bottom)
- Facts shown in discovery order (1, 2, 3, 4...)
- Visual timeline connector line in Aistra green (#d9f378)
- Full fact text visible on hover
- No iteration axis - just pure chronological order
- Dynamic height based on number of facts
- Cleaner, more intuitive design

## Key Improvements

1. **Removed Iteration Axis**: No more confusing X-axis with iteration numbers
2. **Linear Flow**: Facts flow from top to bottom in discovery order
3. **Better Readability**: Text positioned to the right of markers with proper spacing
4. **Hover for Details**: Full fact text shows on hover (for long facts)
5. **Visual Timeline Line**: Connected green line shows the progression
6. **Responsive Height**: Timeline height adjusts based on number of facts

## Technical Changes

**File Modified**: `backend_v2/langgraph_master_agent/sub_agents/investigative_journalist/tools/artifact_generator.py`

**Function**: `generate_timeline_visualization()`

### Changes:
- Replaced scatter plot with linear timeline using `go.Scatter` with `mode='lines'` and `mode='markers+text'`
- Removed iteration-based X-axis positioning
- Added vertical timeline connector line
- Positioned all facts on a single vertical line with text to the right
- Made Y-axis hidden (no labels needed)
- Made X-axis hidden (no iterations shown)
- Dynamic height calculation: `height=max(400, len(facts) * 80)`

## Usage

The timeline will automatically appear in the **Timeline tab** of the Investigative Journalist interface when an investigation completes.

To test locally:
```bash
python test_standalone_timeline.py
open test_new_timeline.html
```

## Design Philosophy

The new timeline follows these principles:
1. **Simplicity**: Remove unnecessary complexity (iteration numbers)
2. **Clarity**: Show what matters (facts in order)
3. **Visual Hierarchy**: Use Aistra color palette (#d9f378 for emphasis)
4. **Progressive Disclosure**: Short text visible, full text on hover
5. **Responsiveness**: Height adapts to content

## Color Palette (Aistra)

- **Primary Green**: `#d9f378` - Timeline line and markers
- **Dark Background**: `#1a1a1a` - Paper and plot background
- **Border**: `#1c1e20` - Marker border
- **Text**: `white` - Labels and titles
- **Hover Background**: `#333333` - Tooltip background


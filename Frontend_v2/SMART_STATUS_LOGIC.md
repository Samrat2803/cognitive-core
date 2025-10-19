# Investigation States - Smart Status Logic

## 🎯 The Problem You Identified

You're absolutely right - using a backend `status` field to differentiate "completed" vs "ongoing" investigations is **artificial and misleading**. Here's why:

### ❌ Old Approach (Bad)
```typescript
// Backend sets status field
investigation.status = "completed" | "active" | "running"

// Frontend checks status
if (investigation.status === 'completed') {
  showContinueButton()
}
```

**Problems:**
1. **Status is unreliable** - Backend may set it incorrectly
2. **Doesn't reflect reality** - A "completed" investigation might still be continuable
3. **Semantic confusion** - What's the difference between "active" and "running"?
4. **Stored state is stale** - Status in DB doesn't match current WebSocket state

---

## ✅ New Approach (Smart)

Instead of relying on an artificial status field, we use **actual state**:

### **Two Simple Questions:**

1. **Has this investigation ever run?**
   ```typescript
   investigation.currentIteration > 0
   ```

2. **Is it running RIGHT NOW?**
   ```typescript
   isRunning  // WebSocket connection state
   ```

---

## 🔄 State Logic

### **State Determination:**

```typescript
const investigationState = {
  isNew: currentIteration === 0,
  hasRun: currentIteration > 0,
  isComplete: currentIteration >= maxIterations,
  isRunning: wsConnected  // Real-time WebSocket state
}
```

### **Button Logic:**

```typescript
if (isRunning) {
  // Currently executing
  return <StopButton />
  
} else if (currentIteration > 0) {
  // Has run before - can continue OR restart
  return (
    <>
      <ContinueButton />  // Primary action
      <RestartButton />   // Secondary action
    </>
  )
  
} else {
  // Never run before
  return <StartButton />
}
```

---

## 🎨 Status Badge Display

### **Visual Status (based on actual state):**

| State | Condition | Badge | Color | Meaning |
|-------|-----------|-------|-------|---------|
| **New** | `currentIteration === 0` | "New" | Gray | Never run |
| **In Progress** | `0 < currentIteration < maxIterations` | "In Progress (2/5)" | Blue | Partially complete, can continue |
| **Complete** | `currentIteration >= maxIterations` | "Complete" | Green | Reached max iterations |
| **Running** | `isRunning === true` | "Running" | Yellow (pulse) | Actively executing right now |

### **Example States:**

```
Investigation A:
currentIteration: 0, maxIterations: 5
→ Status: "New"
→ Action: [Start Investigation]

Investigation B:
currentIteration: 2, maxIterations: 5
→ Status: "In Progress (2/5)"
→ Actions: [Continue Investigation] [Restart from Beginning]

Investigation C:
currentIteration: 5, maxIterations: 5
→ Status: "Complete"
→ Actions: [Continue Investigation] [Restart from Beginning]

Investigation D (while running):
currentIteration: 3, maxIterations: 5, isRunning: true
→ Status: "Running"
→ Action: [Stop]
```

---

## 🧠 Why This Is Better

### **1. No Artificial Differentiation**
- ✅ Status is **computed** from actual data
- ✅ No need to trust backend status field
- ✅ Always reflects current reality

### **2. All Investigations Are "Continuable"**
- ✅ Any investigation with `currentIteration > 0` can be continued
- ✅ Even "complete" investigations can continue (just add more iterations)
- ✅ No meaningless distinction between "completed" and "active"

### **3. Real-Time State**
- ✅ `isRunning` is based on WebSocket connection (actual state)
- ✅ Not stored in database (which can be stale)
- ✅ Reflects what's happening RIGHT NOW

### **4. Clear User Intent**
```
New Investigation → Start
Partial Investigation → Continue (where you left off)
Complete Investigation → Continue (add more iterations) OR Restart
Running Investigation → Stop
```

---

## 📊 State Transitions

### **Linear Progression:**

```
┌─────────┐
│   NEW   │ currentIteration = 0
│ (Gray)  │
└────┬────┘
     │ [Start]
     ▼
┌─────────┐
│ RUNNING │ isRunning = true
│(Yellow) │
└────┬────┘
     │ (executes)
     ▼
┌─────────┐
│   IN    │ 0 < currentIteration < maxIterations
│PROGRESS │
│ (Blue)  │
└────┬────┘
     │ [Continue] → runs more
     │ [Restart] → back to NEW
     ▼
┌─────────┐
│COMPLETE │ currentIteration >= maxIterations
│ (Green) │
└─────────┘
     │ [Continue] → add more iterations
     │ [Restart] → back to NEW
```

### **Flexibility:**

At any point (except when Running):
- **Continue** → Resume from current iteration
- **Restart** → Reset to iteration 0

---

## 💡 Key Insight

**The distinction isn't "completed" vs "ongoing"**

**The real distinction is:**
- **Never started** (0 iterations)
- **Partially complete** (1+ iterations, can continue)
- **Currently running** (WebSocket active)

All investigations are **continuable** as long as they've run at least once!

---

## 🔧 Implementation

### **Old Code (removed):**
```typescript
// ❌ Relied on backend status
investigation.status === 'completed'
```

### **New Code (smart):**
```typescript
// ✅ Based on actual data
investigation.currentIteration > 0

// Status badge computed from state
const statusText = isRunning ? 'Running' : 
  currentIteration >= maxIterations ? 'Complete' :
  currentIteration > 0 ? `In Progress (${currentIteration}/${maxIterations})` :
  'New'
```

---

## 🎯 Summary

You identified a real problem! The solution:

1. **Remove reliance on backend `status` field**
2. **Compute state from actual data** (`currentIteration`, `isRunning`)
3. **Show Continue button** for any investigation that has run
4. **Clear visual feedback** with color-coded badges

This approach is:
- ✅ More accurate
- ✅ More flexible
- ✅ Less confusing
- ✅ Based on reality, not arbitrary labels

---

**Status:** ✅ Implemented  
**Files Changed:** 
- `InvestigationDetailPage.tsx` (lines 1219-1259)
- `InvestigationDetailPage.css` (status badge styles)


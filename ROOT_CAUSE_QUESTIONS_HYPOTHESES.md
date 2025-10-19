# Questions & Hypotheses Not Appearing in UI - ROOT CAUSE FOUND

## 🎯 Root Cause

The investigative journalist agent runs ALL iterations, then saves to MongoDB ONCE at the end:

```python
# sub_agent_caller.py, line 592
result = await investigator.investigate(query)  # Runs ALL iterations

# sub_agent_caller.py, line 595  
investigation_id = await save_investigation(...)  # Saves ONCE at end
```

The WebSocket polling checks MongoDB every 2 seconds, but the data only appears AFTER the entire investigation completes (could be 5+ minutes).

##Fix needed: Save to MongoDB after EACH iteration

The agent needs to save incremental updates to MongoDB so the WebSocket polling can stream them to the frontend in real-time.

### Option 1: Pass investigation_id to investigate()
```python
# In sub_agent_caller.py
result = await investigator.investigate(
    query=query,
    investigation_id=investigation_id  # Pass ID for incremental saves
)

# In lean_investigator.py - after each iteration
if investigation_id:
    await save_investigation({...}, investigation_id)
```

### Option 2: Use a callback
```python
async def save_callback(state):
    await save_investigation(state)

result = await investigator.investigate(
    query=query,
    on_iteration_complete=save_callback
)
```

## Current Behavior
- Agent generates questions/hypotheses ✅
- Data saved to MongoDB ✅
- WebSocket polling working ✅
- BUT: Data appears only at END ❌

## Expected Behavior
- Iteration 1 completes → Save to MongoDB → WebSocket sends updates
- Iteration 2 completes → Save to MongoDB → WebSocket sends updates
- etc.

This way the frontend sees real-time progress!



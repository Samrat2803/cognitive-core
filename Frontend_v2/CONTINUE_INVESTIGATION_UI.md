# Continue Investigation UI - User Guide

## 🎯 Overview

The Continue Investigation feature allows users to resume a completed investigation with additional iterations, providing guidance to the AI agent for deeper analysis.

---

## 🖥️ User Interface

### **1. Button Location**

When viewing a **completed investigation**, you'll see two buttons in the header:

```
┌─────────────────────────────────────────────────────────┐
│  Investigation Detail                                   │
│  [← Back] Investigation Title                           │
│  Status: completed • 15 entities • 7 facts • $0.24     │
│                                                          │
│  [Archive] [Export] [Continue Investigation] [Restart]  │
└─────────────────────────────────────────────────────────┘
```

**Buttons:**
- **Continue Investigation** (Primary) - Opens modal to continue with more iterations
- **Restart** (Secondary) - Runs investigation from scratch (doesn't preserve state)

---

### **2. Continue Investigation Modal**

Clicking "Continue Investigation" opens a modal with the following options:

```
┌──────────────────────────────────────────────────┐
│  Continue Investigation                       × │
├──────────────────────────────────────────────────┤
│                                                  │
│  Resume this investigation with additional       │
│  iterations and optional guidance for the AI.    │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ Additional Iterations: 5                  │  │
│  │ [─────●───────────] (1-20)                │  │
│  │  1         10         20                  │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ Custom Instructions (Optional)            │  │
│  │ Guide the investigation direction         │  │
│  │ ┌────────────────────────────────────┐   │  │
│  │ │ e.g., Focus on financial           │   │  │
│  │ │ connections, Look into regulatory  │   │  │
│  │ │ violations...                      │   │  │
│  │ └────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ Suggest New Hypothesis (Optional)         │  │
│  │ Propose a new angle to explore            │  │
│  │ ┌────────────────────────────────────┐   │  │
│  │ │ The CEO had undisclosed conflicts  │   │  │
│  │ └────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ Suggest Question to Investigate (Optional)│  │
│  │ Ask a specific question                   │  │
│  │ ┌────────────────────────────────────┐   │  │
│  │ │ Who were the largest donors?       │   │  │
│  │ └────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  💰 Estimated additional cost: ~$0.30           │
│                                                  │
├──────────────────────────────────────────────────┤
│                         [Cancel] [▶ Continue]    │
└──────────────────────────────────────────────────┘
```

---

## 🎚️ Field Descriptions

### **1. Additional Iterations Slider** (Required)

- **Range:** 1-20 iterations
- **Default:** 5 iterations
- **Purpose:** Number of additional investigation cycles to run
- **Cost:** ~$0.06 per iteration (estimated)

**Use Cases:**
- **1-3 iterations:** Quick follow-up on a specific angle
- **5-10 iterations:** Standard continuation for deeper analysis
- **10-20 iterations:** Comprehensive investigation of complex topics

---

### **2. Custom Instructions** (Optional)

Provide free-text guidance to the AI investigator.

**Examples:**
```
✅ Good Instructions:
- "Focus on financial connections between the entities"
- "Look into regulatory violations in the past 5 years"
- "Investigate the timeline of events in detail"
- "Explore potential conflicts of interest"

❌ Avoid Vague Instructions:
- "Find more stuff"
- "Do better"
```

---

### **3. Suggest New Hypothesis** (Optional)

Propose a specific hypothesis for the AI to test.

**Format:** A clear statement that can be proven or disproven

**Examples:**
```
✅ Good Hypotheses:
- "The CEO had undisclosed financial conflicts of interest"
- "The company violated environmental regulations knowingly"
- "Political donations influenced policy decisions"

❌ Avoid Questions:
- "Did the CEO have conflicts?" (use the question field instead)
```

---

### **4. Suggest Question to Investigate** (Optional)

Ask a specific question you want answered.

**Examples:**
```
✅ Good Questions:
- "Who were the largest donors to the campaign?"
- "What were the exact dates of the violations?"
- "Which officials approved the permits?"
- "How much money changed hands?"

❌ Avoid General Questions:
- "What happened?" (too broad)
```

---

## 🔄 How It Works

### **Step-by-Step Flow:**

1. **User clicks "Continue Investigation"**
   - Modal opens with default values
   
2. **User adjusts slider** (e.g., 5 iterations)
   - Cost estimate updates automatically
   
3. **User optionally provides guidance**
   - Custom instructions
   - New hypothesis
   - Specific question
   
4. **User clicks "Continue"**
   - Modal closes
   - Backend receives:
     ```json
     {
       "additional_iterations": 5,
       "instructions": "Focus on financial connections",
       "suggested_hypothesis": "...",
       "suggested_question": "..."
     }
     ```
   
5. **Investigation resumes via WebSocket**
   - Loads previous state from MongoDB
   - Continues from where it left off
   - Accumulates new evidence on top of existing data
   
6. **Real-time updates stream to UI**
   - New hypotheses appear
   - New questions populate the tree
   - Entities and facts update live
   - Logs show progress
   
7. **Investigation completes**
   - Article updates with new findings
   - "Continue Investigation" button appears again

---

## 💬 Chat Input Alternative

The investigation detail page also has a chat input at the bottom of the Question Flow panel:

```
┌────────────────────────────────────────┐
│  Question Flow          Hypotheses     │
├────────────────────────────────────────┤
│                                        │
│  [Question tree visualization]         │
│                                        │
│                                        │
├────────────────────────────────────────┤
│ [Continue investigation, ask          │
│  follow-up questions...          Send]│
└────────────────────────────────────────┘
```

**Future Enhancement:**
Users can type commands like:
- `continue for 5 more iterations`
- `continue and focus on financial connections`
- `investigate who were the largest donors`

This will be parsed and trigger the continuation automatically without opening the modal.

---

## 🎨 Visual States

### **Before Investigation Completes**

```
[Archive] [Export] [Start Investigation]
```

### **After Investigation Completes**

```
[Archive] [Export] [Continue Investigation] [Restart]
                    ^^^^^^^^^^^^^^^^^^^^^^
                    Primary action button
```

### **During Continuation**

```
[Archive] [Export] [Stop]
                    ^^^^
                    Stops the running investigation
```

---

## 📊 Evidence Accumulation

When you continue an investigation, the evidence **accumulates** (doesn't reset):

### **Initial Run (2 iterations):**
```
Hypotheses: 2
Questions: 2
Entities: 8
Facts: 2
Cost: $0.12
```

### **After Continuation (+2 iterations):**
```
Hypotheses: 4 ✅ (+2 new)
Questions: 4 ✅ (+2 new)
Entities: 15 ✅ (+7 new)
Facts: 7 ✅ (+5 new)
Cost: $0.24 (total)
```

All previous evidence is preserved and new evidence is added on top!

---

## 🔑 Key Benefits

1. **Flexibility:** Resume investigations whenever you want
2. **Guidance:** Provide specific direction to the AI
3. **Cost Control:** Choose exactly how many iterations to add
4. **Accumulation:** Previous work is never lost
5. **Transparency:** Real-time cost estimates

---

## 🚀 Best Practices

### **When to Use Continue:**
- ✅ Investigation found something interesting, need more depth
- ✅ Want to explore a specific angle discovered
- ✅ Need to verify or refute a hypothesis
- ✅ Found new entities that need investigation

### **When to Use Restart:**
- ✅ Investigation went in wrong direction
- ✅ Want to start fresh with different parameters
- ✅ Testing different iteration counts

### **Iteration Count Guidelines:**
- **1-3:** Quick targeted follow-up
- **5-7:** Standard continuation
- **10+:** Deep dive investigation

---

## 💡 Pro Tips

1. **Use Custom Instructions** to guide the AI when you have domain knowledge
2. **Suggest Hypotheses** when you notice patterns the AI might have missed
3. **Ask Specific Questions** to get targeted answers
4. **Monitor Cost** - each iteration costs ~$0.06
5. **Review Evidence** before continuing to avoid redundant work

---

## 🎯 Example Workflow

### **Scenario:** Investigating corporate fraud

**Initial Investigation (5 iterations):**
- Query: "XYZ Corp financial irregularities"
- Results: Found suspicious transactions, identified 3 key executives

**User decides to continue:**
1. Clicks "Continue Investigation"
2. Sets iterations: 5
3. Custom instructions: "Focus on offshore accounts and shell companies"
4. Suggested question: "Which executives had undisclosed offshore accounts?"
5. Clicks "Continue"

**Continuation runs:**
- AI focuses search on offshore connections
- Discovers 2 shell companies
- Maps connections to executives
- Finds additional suspicious transactions

**Final Result:**
- Original 3 executives + 2 new entities (shell companies)
- Total: 15 entities, 12 facts, 6 connections
- Comprehensive report with offshore network visualization

---

## 📞 Support

For issues or questions:
- Check the Logs tab for error messages
- Review the Evidence tab to see what was found
- Monitor WebSocket connection status
- Verify backend is running on port 8000

---

**Status:** ✅ Fully Implemented  
**Version:** 1.0.0  
**Last Updated:** October 19, 2025


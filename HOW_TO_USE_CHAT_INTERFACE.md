# How to Use the Chat Interface

## 🚀 Starting an Investigation

### Default (5 iterations)
Just type your query naturally:
```
Investigate quantum computing breakthroughs
```
→ Runs for **5 iterations** (default)

### Specify Custom Iterations
Add the number of iterations you want:

**Format 1**: `"Query for X iterations"`
```
Investigate quantum computing for 10 iterations
```

**Format 2**: `"Query X iterations"`
```
Research SpaceX Starship 3 iterations
```

**Format 3**: `"Query X iteration"` (singular)
```
Analyze AI trends 7 iteration
```

## 🔄 Continuing an Investigation

Once an investigation has started, you can continue it:

**Format 1**: `"Continue for X more iterations"`
```
Continue for 5 more iterations
```

**Format 2**: `"Continue X iterations"`
```
Continue 10 iterations
```

**Default**: If you just say "continue" without a number, it adds **5 more iterations**.
```
Continue
```

## 📊 Examples

| Input | What Happens | Iterations |
|-------|--------------|------------|
| `"Investigate climate change"` | Starts new investigation | 5 (default) |
| `"Investigate climate change for 10 iterations"` | Starts new investigation | 10 |
| `"Research Tesla 3 iterations"` | Starts new investigation | 3 |
| `"Continue for 8 more iterations"` | Continues current investigation | +8 |
| `"Continue"` | Continues current investigation | +5 (default) |

## 🎯 How It Works

### Backend Parsing
1. **Extracts iteration count**: Uses regex `r'(\d+)\s+iterations?'`
2. **Cleans the query**: Removes iteration instructions from query text
3. **Runs investigation**: Passes cleaned query to investigator agent

### Example Parsing:
```
Input:  "Investigate quantum computing for 10 iterations"
↓
Query:  "Investigate quantum computing"
Iterations: 10
```

## 💡 Tips

1. **Be specific**: The more specific your query, the better the results
2. **Start small**: Try 2-3 iterations first to test (saves cost)
3. **Monitor progress**: Watch real-time logs in the chat
4. **Continue wisely**: If you need more depth, continue for 3-5 more iterations
5. **Cost awareness**: Each iteration costs money (API calls), so be mindful

## 🔍 What You'll See

### During Investigation:
- 💡 **Hypotheses**: New theories being formed
- ❓ **Questions**: Research questions discovered
- 👤 **Entities**: People, organizations, places mentioned
- 📌 **Facts**: Key findings recorded
- 🔍 **Search queries**: What the agent is searching for

### After Completion:
- ✅ **Final report**: Complete investigation summary
- 📊 **Artifacts**: Charts, graphs, visualizations (if any)
- 💰 **Cost**: Total API cost for the investigation

## 🚨 Cost Estimates

**Per iteration** (approximate):
- Strategist: ~$0.01
- Searcher: ~$0.02-0.05
- Extractor: ~$0.01-0.02 (if using free text extraction: $0)
- Analyzer: ~$0.01-0.02
- Synthesizer: ~$0.01

**Total per iteration**: ~$0.05-0.10

**5 iterations**: ~$0.25-0.50  
**10 iterations**: ~$0.50-1.00  
**20 iterations**: ~$1.00-2.00

*Note: Costs vary based on query complexity and content length*

## 🎨 UI Features

- **Real-time logs**: See everything as it happens
- **Status indicator**: Green dot = connected, Gray = disconnected
- **Auto-scroll**: Automatically scrolls to latest message
- **Markdown support**: Final reports render with formatting
- **Artifacts panel**: Generated charts/visualizations appear on the right
- **Compact layout**: Timestamps inline to save vertical space

---

**Need help?** Just ask the bot! It's designed to understand natural language.


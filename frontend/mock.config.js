// Mock Backend Configuration
// To enable mock backend, set environment variable: REACT_APP_USE_MOCK=true
// Or modify the useMockBackend flag in src/config.ts

module.exports = {
  // Toggle mock backend
  enabled: process.env.REACT_APP_USE_MOCK === 'true',
  
  // Mock settings
  streamingDelay: {
    min: 50,
    max: 200
  },
  
  // Mock data
  sampleQueries: [
    "Analyze Hamas sentiment in US, Iran, and Israel",
    "Compare Ukraine war coverage in Europe", 
    "Climate policy sentiment in G7 nations"
  ]
};

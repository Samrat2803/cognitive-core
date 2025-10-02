// Quick test script to verify mock functionality
import { 
  mockChatMessage, 
  mockConfirmAnalysis, 
  mockAnalysisExecute, 
  mockGetAnalysis,
  mockAnalysisHistory,
  mockExportCreate,
  mockGetExport 
} from './api/mocks.js';

async function testMocks() {
  console.log('Testing mock API functions...');
  
  try {
    // Test chat message
    const chatResponse = await mockChatMessage('Analyze Hamas sentiment', 'test-session');
    console.log('✅ Chat message:', chatResponse.response_type);
    
    // Test analysis execution
    const analysisResponse = await mockAnalysisExecute('Test query', {}, 'test-session');
    console.log('✅ Analysis execute:', analysisResponse.analysis_id);
    
    // Test getting analysis (should show processing)
    const analysisStatus = await mockGetAnalysis(analysisResponse.analysis_id);
    console.log('✅ Analysis status:', analysisStatus.status);
    
    // Test history
    const history = await mockAnalysisHistory();
    console.log('✅ History count:', history.analyses.length);
    
    // Test export
    const exportResponse = await mockExportCreate(analysisResponse.analysis_id, 'pdf', {});
    console.log('✅ Export created:', exportResponse.export_id);
    
    console.log('All mock tests passed! 🎉');
  } catch (error) {
    console.error('❌ Mock test failed:', error);
  }
}

// Run tests if this file is executed directly
if (typeof window === 'undefined') {
  testMocks();
}

export { testMocks };

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { HomePage } from './pages/HomePage';
import { ChatPage } from './pages/ChatPage';
import { InvestigativeJournalistPage } from './pages/InvestigativeJournalistPage';
import { CognitiveCrawlerPage } from './pages/CognitiveCrawlerPage';
import { InfoPage } from './pages/InfoPage';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/investigative-journalist" element={<InvestigativeJournalistPage />} />
        <Route path="/cognitive-crawler" element={<CognitiveCrawlerPage />} />
        <Route path="/info" element={<InfoPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;

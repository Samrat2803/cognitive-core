import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import './App.css';
import Home from './pages/Home';
import Chat from './pages/Chat';
import AnalysisResults from './pages/AnalysisResults';

// Create custom MUI theme that uses CSS variables
const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#1c1e20',
      paper: '#333333'
    },
    primary: {
      main: '#d9f378'
    },
    secondary: {
      main: '#5d535c'
    },
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)'
    }
  },
  typography: {
    fontFamily: 'Roboto Flex, system-ui, -apple-system, sans-serif'
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: 'var(--aistra-darker)',
          color: 'var(--aistra-white)'
        }
      }
    }
  }
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div className="App" style={{ minHeight: '100vh', background: 'var(--aistra-darker)' }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/analysis" element={<AnalysisResults />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
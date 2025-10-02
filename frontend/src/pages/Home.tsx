import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Container,
  Card,
  CardContent,
  Chip,
  Stack
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Public as PublicIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';

const Home: React.FC = () => {
  const navigate = useNavigate();

  const promptChips = [
    "Analyze Hamas sentiment in US, Iran, and Israel",
    "Compare Ukraine war coverage across European countries", 
    "Sentiment analysis of climate change policies in G7 nations",
    "Public opinion on AI regulation in tech-leading countries",
    "Economic sentiment analysis post-COVID recovery"
  ];

  const features = [
    {
      icon: <AnalyticsIcon sx={{ fontSize: 40, color: 'var(--aistra-primary)' }} />,
      title: 'Real-time Analysis',
      description: 'Get instant geopolitical sentiment analysis across multiple countries'
    },
    {
      icon: <TrendingUpIcon sx={{ fontSize: 40, color: 'var(--aistra-primary)' }} />,
      title: 'Trend Detection',
      description: 'Identify emerging patterns and shifts in public opinion'
    },
    {
      icon: <PublicIcon sx={{ fontSize: 40, color: 'var(--aistra-primary)' }} />,
      title: 'Global Coverage',
      description: 'Analyze sentiment across countries and regions worldwide'
    },
    {
      icon: <SpeedIcon sx={{ fontSize: 40, color: 'var(--aistra-primary)' }} />,
      title: 'Fast Results',
      description: 'Streaming analysis with results in under 60 seconds'
    }
  ];

  const handleStartAnalysis = () => {
    navigate('/chat');
  };

  const handlePromptChipClick = (prompt: string) => {
    navigate('/chat', { state: { initialPrompt: prompt } });
  };

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      backgroundColor: 'var(--aistra-darker)',
      color: 'var(--aistra-white)'
    }}>
      <Container maxWidth="lg" sx={{ py: 8 }}>
        {/* Hero Section */}
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <Typography
            variant="h2"
            component="h1"
            sx={{
              fontWeight: 700,
              fontSize: { xs: '2.5rem', md: '3.5rem' },
              color: 'var(--aistra-primary)',
              mb: 2,
              fontFamily: 'Roboto Flex, sans-serif'
            }}
          >
            Cognitive Core
          </Typography>
          
          <Typography
            variant="h5"
            sx={{
              fontWeight: 400,
              fontSize: { xs: '1.2rem', md: '1.5rem' },
              color: 'var(--aistra-white)',
              opacity: 0.9,
              mb: 1,
              maxWidth: '600px',
              mx: 'auto'
            }}
          >
            Political Analyst Workbench
          </Typography>

          <Typography
            variant="body1"
            sx={{
              fontSize: '1.1rem',
              color: 'var(--aistra-white)',
              opacity: 0.7,
              mb: 4,
              maxWidth: '700px',
              mx: 'auto',
              lineHeight: 1.6
            }}
          >
            Analyze geopolitical sentiment across countries with AI-powered insights. 
            Get real-time analysis of public opinion, media coverage, and emerging trends.
          </Typography>

          <Button
            variant="contained"
            size="large"
            onClick={handleStartAnalysis}
            sx={{
              backgroundColor: 'var(--aistra-primary)',
              color: 'var(--aistra-darker)',
              fontWeight: 600,
              fontSize: '1.1rem',
              px: 4,
              py: 1.5,
              borderRadius: 2,
              textTransform: 'none',
              '&:hover': {
                backgroundColor: 'var(--aistra-primary)',
                opacity: 0.9,
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(217, 243, 120, 0.3)'
              },
              transition: 'all 0.3s ease'
            }}
          >
            🚀 Start Analysis
          </Button>
        </Box>

        {/* Quick Start Prompts */}
        <Box sx={{ mb: 8 }}>
          <Typography
            variant="h6"
            sx={{
              textAlign: 'center',
              color: 'var(--aistra-primary)',
              fontWeight: 600,
              mb: 3
            }}
          >
            Quick Start Examples
          </Typography>
          
          <Stack
            direction="row"
            spacing={1}
            sx={{
              flexWrap: 'wrap',
              justifyContent: 'center',
              gap: 1
            }}
          >
            {promptChips.map((prompt, index) => (
              <Chip
                key={index}
                label={prompt}
                onClick={() => handlePromptChipClick(prompt)}
                sx={{
                  backgroundColor: 'var(--aistra-dark)',
                  color: 'var(--aistra-white)',
                  border: '1px solid var(--aistra-secondary)',
                  borderRadius: 2,
                  px: 1,
                  py: 0.5,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    backgroundColor: 'var(--aistra-primary)',
                    color: 'var(--aistra-darker)',
                    borderColor: 'var(--aistra-primary)',
                    transform: 'translateY(-1px)'
                  }
                }}
              />
            ))}
          </Stack>
        </Box>

        {/* Features Grid */}
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { 
            xs: '1fr', 
            sm: 'repeat(2, 1fr)', 
            md: 'repeat(4, 1fr)' 
          }, 
          gap: 4, 
          mb: 6 
        }}>
          {features.map((feature, index) => (
            <Card
              key={index}
              sx={{
                backgroundColor: 'var(--aistra-dark)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 2,
                height: '100%',
                transition: 'all 0.3s ease',
                '&:hover': {
                  borderColor: 'var(--aistra-primary)',
                  transform: 'translateY(-4px)',
                  boxShadow: '0 8px 25px rgba(217, 243, 120, 0.1)'
                }
              }}
            >
              <CardContent sx={{ textAlign: 'center', p: 3 }}>
                <Box sx={{ mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography
                  variant="h6"
                  sx={{
                    color: 'var(--aistra-white)',
                    fontWeight: 600,
                    mb: 1,
                    fontSize: '1.1rem'
                  }}
                >
                  {feature.title}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: 'var(--aistra-white)',
                    opacity: 0.8,
                    lineHeight: 1.5
                  }}
                >
                  {feature.description}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>

        {/* Call to Action */}
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography
            variant="body1"
            sx={{
              color: 'var(--aistra-white)',
              opacity: 0.7,
              mb: 2
            }}
          >
            Ready to dive deeper into geopolitical analysis?
          </Typography>
          <Button
            variant="outlined"
            onClick={handleStartAnalysis}
            sx={{
              borderColor: 'var(--aistra-primary)',
              color: 'var(--aistra-primary)',
              fontWeight: 600,
              px: 3,
              py: 1,
              borderRadius: 2,
              textTransform: 'none',
              '&:hover': {
                borderColor: 'var(--aistra-primary)',
                backgroundColor: 'rgba(217, 243, 120, 0.1)'
              }
            }}
          >
            Get Started →
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default Home;

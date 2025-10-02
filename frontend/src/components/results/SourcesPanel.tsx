import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemText,
  Typography,
  IconButton,
  Box,
  Chip,
  Link,
  Divider
} from '@mui/material';
import { Close as CloseIcon, OpenInNew as OpenInNewIcon } from '@mui/icons-material';
import { Citation } from '../../types';

interface SourcesPanelProps {
  open: boolean;
  onClose: () => void;
  citations: Citation[];
  selectedCitationId?: string;
}

const SourcesPanel: React.FC<SourcesPanelProps> = ({
  open,
  onClose,
  citations,
  selectedCitationId
}) => {
  const getCredibilityColor = (credibility: number) => {
    if (credibility >= 0.8) return '#10b981'; // green
    if (credibility >= 0.6) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  const getCredibilityLabel = (credibility: number) => {
    if (credibility >= 0.8) return 'High';
    if (credibility >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      sx={{
        '& .MuiDrawer-paper': {
          width: { xs: '100%', sm: 400 },
          backgroundColor: 'var(--aistra-dark)',
          color: 'var(--aistra-white)',
          borderLeft: '1px solid rgba(255,255,255,0.1)'
        }
      }}
    >
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ color: 'var(--aistra-primary)', fontWeight: 600 }}>
            Sources ({citations.length})
          </Typography>
          <IconButton 
            onClick={onClose}
            sx={{ color: 'var(--aistra-white)' }}
            aria-label="Close sources panel"
          >
            <CloseIcon />
          </IconButton>
        </Box>

        {citations.length === 0 ? (
          <Typography sx={{ color: 'var(--aistra-white)', opacity: 0.7, textAlign: 'center', mt: 4 }}>
            No sources available
          </Typography>
        ) : (
          <List sx={{ p: 0 }}>
            {citations.map((citation, index) => (
              <React.Fragment key={citation.id}>
                <ListItem
                  sx={{
                    flexDirection: 'column',
                    alignItems: 'flex-start',
                    p: 2,
                    backgroundColor: selectedCitationId === citation.id 
                      ? 'rgba(217, 243, 120, 0.1)' 
                      : 'transparent',
                    borderRadius: 1,
                    mb: 1,
                    border: selectedCitationId === citation.id 
                      ? '1px solid var(--aistra-primary)' 
                      : '1px solid transparent'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, width: '100%' }}>
                    <Chip
                      label={`[${index + 1}]`}
                      size="small"
                      sx={{
                        backgroundColor: 'var(--aistra-primary)',
                        color: 'var(--aistra-darker)',
                        fontWeight: 600,
                        mr: 1
                      }}
                    />
                    <Chip
                      label={getCredibilityLabel(citation.credibility)}
                      size="small"
                      sx={{
                        backgroundColor: getCredibilityColor(citation.credibility),
                        color: 'white',
                        fontSize: '0.75rem'
                      }}
                    />
                  </Box>

                  <ListItemText
                    primary={
                      <Link
                        href={citation.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{
                          color: 'var(--aistra-white)',
                          textDecoration: 'none',
                          fontWeight: 600,
                          fontSize: '0.95rem',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5,
                          '&:hover': {
                            color: 'var(--aistra-primary)',
                            textDecoration: 'underline'
                          }
                        }}
                      >
                        {citation.title}
                        <OpenInNewIcon sx={{ fontSize: 16 }} />
                      </Link>
                    }
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography
                          variant="body2"
                          sx={{
                            color: 'var(--aistra-secondary)',
                            fontSize: '0.85rem',
                            mb: 0.5
                          }}
                        >
                          {citation.domain}
                        </Typography>
                        {citation.published_at && (
                          <Typography
                            variant="caption"
                            sx={{
                              color: 'var(--aistra-white)',
                              opacity: 0.6,
                              fontSize: '0.75rem'
                            }}
                          >
                            Published: {new Date(citation.published_at).toLocaleDateString()}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
                {index < citations.length - 1 && (
                  <Divider sx={{ backgroundColor: 'rgba(255,255,255,0.1)', my: 1 }} />
                )}
              </React.Fragment>
            ))}
          </List>
        )}

        <Box sx={{ mt: 3, p: 2, backgroundColor: 'var(--aistra-darker)', borderRadius: 1 }}>
          <Typography variant="caption" sx={{ color: 'var(--aistra-white)', opacity: 0.7 }}>
            💡 Click citation numbers in the chat to jump to specific sources
          </Typography>
        </Box>
      </Box>
    </Drawer>
  );
};

export default SourcesPanel;

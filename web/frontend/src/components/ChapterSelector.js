import React, { useState, useEffect } from 'react';
import {
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Paper,
  Typography,
  Box,
  Button,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import api from '../services/api';

export default function ChapterSelector({ subject, onSelectChapter, onBack }) {
  const [chapters, setChapters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadChapters();
  }, [subject]);

  const loadChapters = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/learn/chapters?subject=${encodeURIComponent(subject.name)}`);
      if (response.data.success) {
        setChapters(response.data.chapters);
      }
    } catch (err) {
      setError('Failed to load chapters');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={onBack}
          sx={{ mb: 2 }}
        >
          Back to Subjects
        </Button>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>
            {subject.icon} {subject.name}
          </Typography>
          <Chip label={`${chapters.length} chapters`} color="primary" />
        </Box>
        <Typography variant="body1" sx={{ color: 'text.secondary' }}>
          Select a chapter to start learning with summaries, explanations, examples, and quizzes
        </Typography>
      </Box>

      {/* Chapters List */}
      {chapters.length > 0 ? (
        <Paper sx={{ overflow: 'hidden' }}>
          <List sx={{ width: '100%' }}>
            {chapters.map((chapter, index) => (
              <ListItem key={index} disablePadding>
                <ListItemButton
                  onClick={() => onSelectChapter(chapter)}
                  sx={{
                    py: 2,
                    '&:hover': {
                      bgcolor: 'primary.light',
                      color: 'white',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  <ListItemText
                    primary={
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {chapter.name}
                      </Typography>
                    }
                    secondary={
                      <Typography variant="body2" sx={{ color: 'text.secondary', mt: 0.5 }}>
                        {chapter.document_count} sections • Tap to learn
                      </Typography>
                    }
                  />
                  <Chip
                    label={`${chapter.document_count} docs`}
                    size="small"
                    color="primary"
                    variant="outlined"
                    sx={{ ml: 2 }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Paper>
      ) : (
        <Alert severity="info">No chapters found for this subject</Alert>
      )}
    </Box>
  );
}

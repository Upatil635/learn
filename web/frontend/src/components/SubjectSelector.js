import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Typography,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import api from '../services/api';

export default function SubjectSelector({ onSelectSubject }) {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSubjects();
  }, []);

  const loadSubjects = async () => {
    try {
      setLoading(true);
      const response = await api.get('/learn/subjects');
      if (response.data.success) {
        setSubjects(response.data.subjects);
      }
    } catch (err) {
      setError('Failed to load subjects');
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
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          📚 Choose Your Subject
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary' }}>
          Select a subject to begin learning with AI-powered personalized content
        </Typography>
      </Box>

      <Grid container spacing={{ xs: 2, sm: 3 }} sx={{ mb: 4 }}>
        {subjects.map((subject) => (
          <Grid item xs={12} sm={6} md={4} key={subject.name}>
            <Card
              sx={{
                height: '100%',
                transition: 'all 0.3s ease',
                cursor: 'pointer',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: 6,
                  bgcolor: 'primary.light',
                  color: 'white',
                },
                bgcolor: 'background.paper',
              }}
              onClick={() => onSelectSubject(subject)}
            >
              <CardActionArea sx={{ height: '100%' }}>
                <CardContent sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="h2" sx={{ mb: 2 }}>
                    {subject.icon}
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                    {subject.name}
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                    Click to explore chapters
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>

      {subjects.length === 0 && (
        <Alert severity="info">
          No subjects found. Please run setup first: python3 main.py setup
        </Alert>
      )}
    </Box>
  );
}

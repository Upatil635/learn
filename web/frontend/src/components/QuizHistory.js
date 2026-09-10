import React, { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Typography,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import api from '../services/api';

export default function QuizHistory({ onBack }) {
  const [attempts, setAttempts] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.get('/history');
        setAttempts(res.data.attempts || []);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to load history');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const openAttempt = async (id) => {
    try {
      const res = await api.get(`/history/${id}`);
      setSelected(res.data.attempt);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load attempt');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (selected) {
    const quiz = selected.attempt?.quiz || [];
    const answers = selected.attempt?.answers || {};
    return (
      <Box>
        <Button startIcon={<ArrowBackIcon />} onClick={() => setSelected(null)} sx={{ mb: 2 }}>
          Back to history
        </Button>
        <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
          {selected.chapter}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {selected.subject} • Score {selected.score}% • {new Date(selected.created_at).toLocaleString()}
        </Typography>
        {quiz.map((q, qIdx) => {
          const chosen = answers[qIdx] ?? answers[String(qIdx)];
          const isCorrect = chosen === q.correct_answer;
          return (
            <Card key={qIdx} sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                    Q{qIdx + 1}: {q.question}
                  </Typography>
                  {isCorrect ? (
                    <CheckCircleIcon color="success" sx={{ ml: 'auto' }} />
                  ) : (
                    <ErrorIcon color="error" sx={{ ml: 'auto' }} />
                  )}
                </Box>
                {(q.options || []).map((opt, oIdx) => (
                  <Typography
                    key={oIdx}
                    variant="body2"
                    sx={{
                      py: 0.5,
                      fontWeight: oIdx === q.correct_answer || oIdx === chosen ? 600 : 400,
                    }}
                  >
                    {opt}
                    {oIdx === q.correct_answer ? ' ✓' : ''}
                    {oIdx === chosen && oIdx !== q.correct_answer ? ' (your answer)' : ''}
                  </Typography>
                ))}
                {q.explanation && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {q.explanation}
                  </Typography>
                )}
              </CardContent>
            </Card>
          );
        })}
      </Box>
    );
  }

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={onBack} sx={{ mb: 2 }}>
        Back to learning
      </Button>
      <Typography variant="h5" sx={{ fontWeight: 700, mb: 2 }}>
        Quiz history
      </Typography>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {attempts.length === 0 ? (
        <Alert severity="info">No quizzes submitted yet.</Alert>
      ) : (
        attempts.map((item) => (
          <Card
            key={item.id}
            sx={{ mb: 1.5, cursor: 'pointer' }}
            onClick={() => openAttempt(item.id)}
          >
            <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 1.5 }}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {item.chapter}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {item.subject} • {new Date(item.created_at).toLocaleString()}
                </Typography>
              </Box>
              <Chip label={`${item.score}%`} color={item.score >= 70 ? 'success' : 'warning'} />
            </CardContent>
          </Card>
        ))
      )}
    </Box>
  );
}

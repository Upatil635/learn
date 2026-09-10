import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Grid,
  Paper,
  Radio,
  RadioGroup,
  FormControlLabel,
  TextField,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import api from '../services/api';

export default function LearningHub({ subject, chapter, onBack, setError }) {
  const [content, setContent] = useState(null);
  const [loading, setLocalLoading] = useState(true);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [expandedSection, setExpandedSection] = useState('summary');
  const [flipped, setFlipped] = useState({});
  const [askQuestion, setAskQuestion] = useState('');
  const [askAnswer, setAskAnswer] = useState('');
  const [askLoading, setAskLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchHits, setSearchHits] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [askCached, setAskCached] = useState(false);

  useEffect(() => {
    loadContent();
  }, [subject, chapter]);

  const loadContent = async (force = false) => {
    try {
      setLocalLoading(true);
      const response = await api.post('/learn/content', {
        subject: subject.name,
        chapter: chapter.name,
        force,
      });

      if (response.data.success) {
        setContent(response.data);
        setAnswers({});
        setSubmitted(false);
        setExpandedSection('summary');
        setAskAnswer('');
        setAskCached(false);
        setSearchHits([]);
      } else {
        setError(response.data.error || 'Failed to load content');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load learning content');
      console.error(err);
    } finally {
      setLocalLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (!content) {
    return <Alert severity="error">Failed to load content. Please try again.</Alert>;
  }

  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpandedSection(isExpanded ? panel : false);
  };

  const handleAnswerChange = (qIndex, answerIdx) => {
    setAnswers({ ...answers, [qIndex]: answerIdx });
  };

  const handleSubmitQuiz = async () => {
    setSubmitted(true);
    const score = calculateScore();
    try {
      await api.post('/history', {
        subject: subject.name,
        chapter: chapter.name,
        score,
        quiz: content.quiz,
        answers,
      });
    } catch (err) {
      console.error(err);
    }
  };

  const handleAsk = async () => {
    if (!askQuestion.trim()) return;
    try {
      setAskLoading(true);
      const res = await api.post('/learn/ask', {
        subject: subject.name,
        chapter: chapter.name,
        question: askQuestion.trim(),
      });
      setAskAnswer(res.data.answer || '');
      setAskCached(Boolean(res.data.cached));
    } catch (err) {
      setError(err.response?.data?.error || 'Could not answer that question');
    } finally {
      setAskLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      setSearchLoading(true);
      const res = await api.post('/learn/search', {
        subject: subject.name,
        chapter: chapter.name,
        query: searchQuery.trim(),
      });
      setSearchHits(res.data.documents || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Search failed');
    } finally {
      setSearchLoading(false);
    }
  };

  const calculateScore = () => {
    if (!content.quiz || content.quiz.length === 0) return 0;
    let correct = 0;
    content.quiz.forEach((q, idx) => {
      if (answers[idx] === q.correct_answer) correct++;
    });
    return Math.round((correct / content.quiz.length) * 100);
  };

  const toggleFlip = (idx) => {
    setFlipped({ ...flipped, [idx]: !flipped[idx] });
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={onBack}
          sx={{ mb: 2 }}
        >
          Back to Chapters
        </Button>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>
            {subject.icon} {chapter.name}
          </Typography>
          <Chip label={subject.name} color="primary" />
          <Chip
            label={content.cached ? 'Saved — reused' : 'Just generated'}
            color={content.cached ? 'success' : 'default'}
            variant="outlined"
          />
          <Button size="small" variant="outlined" onClick={() => loadContent(true)}>
            Regenerate with AI
          </Button>
        </Box>
      </Box>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
          Ask or search this chapter
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexDirection: { xs: 'column', sm: 'row' }, mb: 1 }}>
          <TextField
            fullWidth
            size="small"
            label="Ask a question"
            value={askQuestion}
            onChange={(e) => setAskQuestion(e.target.value)}
          />
          <Button variant="contained" onClick={handleAsk} disabled={askLoading}>
            {askLoading ? <CircularProgress size={18} color="inherit" /> : 'Ask'}
          </Button>
        </Box>
        {askAnswer && (
          <Box sx={{ mb: 2 }}>
            {askCached && (
              <Chip size="small" label="Saved answer" color="success" sx={{ mb: 1 }} />
            )}
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
              {askAnswer}
            </Typography>
          </Box>
        )}
        <Box sx={{ display: 'flex', gap: 1, flexDirection: { xs: 'column', sm: 'row' } }}>
          <TextField
            fullWidth
            size="small"
            label="Search notes"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Button variant="outlined" onClick={handleSearch} disabled={searchLoading}>
            {searchLoading ? <CircularProgress size={18} /> : 'Search'}
          </Button>
        </Box>
        {searchHits.map((doc, i) => (
          <Box key={i} sx={{ mt: 1.5 }}>
            <Chip size="small" label={`${Math.round((doc.similarity_score || 0) * 100)}% match`} sx={{ mb: 0.5 }} />
            <Typography variant="body2">{doc.content?.slice(0, 320)}...</Typography>
          </Box>
        ))}
      </Paper>

      {/* Main Content Sections */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {/* 1. Summary */}
        <Accordion
          expanded={expandedSection === 'summary'}
          onChange={handleAccordionChange('summary')}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              📝 Summary
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
              {content.summary}
            </Typography>
          </AccordionDetails>
        </Accordion>

        {/* 2. ELI5 */}
        <Accordion
          expanded={expandedSection === 'eli5'}
          onChange={handleAccordionChange('eli5')}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              👧 Explain Like I'm 5 (Simple Version)
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
              {content.eli5}
            </Typography>
          </AccordionDetails>
        </Accordion>

        {/* 3. Mnemonics */}
        <Accordion
          expanded={expandedSection === 'mnemonics'}
          onChange={handleAccordionChange('mnemonics')}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              🧠 Memory Tricks & Mnemonics
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              {content.mnemonics && content.mnemonics.length > 0 ? (
                content.mnemonics.map((m, i) => (
                  <Box key={i} sx={{ mb: 2 }}>
                    <Chip label={`Tip ${i + 1}`} size="small" sx={{ mb: 1 }} />
                    <Typography variant="body2">{m}</Typography>
                  </Box>
                ))
              ) : (
                <Typography variant="body2">No specific mnemonics found. Create your own!</Typography>
              )}
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* 4. Real-life Examples */}
        <Accordion
          expanded={expandedSection === 'examples'}
          onChange={handleAccordionChange('examples')}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              🌟 Real-life Examples
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              {content.examples && content.examples.length > 0 ? (
                content.examples.map((e, i) => (
                  <Box key={i} sx={{ mb: 2 }}>
                    <Chip label={`Example ${i + 1}`} size="small" sx={{ mb: 1 }} />
                    <Typography variant="body2">{e}</Typography>
                  </Box>
                ))
              ) : (
                <Typography variant="body2">See how this concept applies in real life</Typography>
              )}
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* 5. Key Takeaways */}
        <Accordion
          expanded={expandedSection === 'takeaways'}
          onChange={handleAccordionChange('takeaways')}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              ⭐ Key Takeaways
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ width: '100%' }}>
              {content.key_takeaways && content.key_takeaways.length > 0 ? (
                content.key_takeaways.map((k, i) => (
                  <Box key={i} sx={{ display: 'flex', gap: 2, mb: 1.5 }}>
                    <CheckCircleIcon sx={{ color: 'success.main', mt: 0.5, flexShrink: 0 }} />
                    <Typography variant="body2">{k}</Typography>
                  </Box>
                ))
              ) : (
                <Typography variant="body2">Main points to remember</Typography>
              )}
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* 6. Flashcards */}
        <Accordion
          expanded={expandedSection === 'flashcards'}
          onChange={handleAccordionChange('flashcards')}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              🎴 Flashcards
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2} sx={{ width: '100%' }}>
              {content.flashcards && content.flashcards.length > 0 ? (
                content.flashcards.map((card, i) => (
                  <Grid item xs={12} sm={6} key={i}>
                    <Paper
                      sx={{
                        p: 2,
                        minHeight: 150,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        bgcolor: flipped[i] ? 'success.light' : 'info.light',
                        transition: 'all 0.3s ease',
                        '&:hover': { transform: 'scale(1.05)', boxShadow: 3 },
                        textAlign: 'center',
                      }}
                      onClick={() => toggleFlip(i)}
                    >
                      <Box>
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                          {flipped[i] ? 'Answer' : 'Question'} • Tap to flip
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{
                            mt: 1,
                            fontWeight: flipped[i] ? 600 : 500,
                            color: flipped[i] ? 'success.dark' : 'info.dark',
                          }}
                        >
                          {flipped[i] ? card.answer : card.question}
                        </Typography>
                      </Box>
                    </Paper>
                  </Grid>
                ))
              ) : (
                <Typography variant="body2">Flashcards for quick review</Typography>
              )}
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* 7. Quiz */}
        <Accordion
          expanded={expandedSection === 'quiz'}
          onChange={handleAccordionChange('quiz')}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              ✍️ Quiz
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ width: '100%' }}>
              {submitted && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Your Score: {calculateScore()}%
                  </Typography>
                </Alert>
              )}

              {content.quiz && content.quiz.length > 0 ? (
                <Box>
                  {content.quiz.map((q, qIdx) => {
                    const isAnswered = answers[qIdx] !== undefined;
                    const isCorrect = isAnswered && answers[qIdx] === q.correct_answer;
                    const showResult = submitted && isAnswered;

                    return (
                      <Card key={qIdx} sx={{ mb: 2, border: showResult ? (isCorrect ? '2px solid #4caf50' : '2px solid #f44336') : 'none' }}>
                        <CardContent>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                              Q{qIdx + 1}: {q.question}
                            </Typography>
                            {showResult &&
                              (isCorrect ? (
                                <CheckCircleIcon sx={{ color: '#4caf50', ml: 'auto' }} />
                              ) : (
                                <ErrorIcon sx={{ color: '#f44336', ml: 'auto' }} />
                              ))}
                          </Box>

                          <RadioGroup
                            value={answers[qIdx] ?? ''}
                            onChange={(e) => handleAnswerChange(qIdx, parseInt(e.target.value))}
                            disabled={submitted}
                          >
                            {q.options.map((opt, oIdx) => (
                              <FormControlLabel
                                key={oIdx}
                                value={oIdx}
                                control={<Radio />}
                                label={
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    {opt}
                                    {showResult && oIdx === q.correct_answer && (
                                      <Chip label="✓ Correct" size="small" color="success" />
                                    )}
                                    {showResult && oIdx === answers[qIdx] && !isCorrect && (
                                      <Chip label="✗ Your answer" size="small" color="error" />
                                    )}
                                  </Box>
                                }
                              />
                            ))}
                          </RadioGroup>

                          {showResult && (
                            <Box sx={{ mt: 2, p: 1.5, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                              <Typography variant="caption" sx={{ fontWeight: 600 }}>
                                💡 Explanation:
                              </Typography>
                              <Typography variant="body2" sx={{ mt: 1 }}>
                                {q.explanation}
                              </Typography>
                            </Box>
                          )}
                        </CardContent>
                      </Card>
                    );
                  })}

                  {!submitted && (
                    <Button
                      fullWidth
                      variant="contained"
                      color="primary"
                      onClick={handleSubmitQuiz}
                      disabled={Object.keys(answers).length !== content.quiz.length}
                      sx={{ mt: 2, py: 1.5 }}
                    >
                      Submit Quiz
                    </Button>
                  )}
                </Box>
              ) : (
                <Typography variant="body2">Quiz not available</Typography>
              )}
            </Box>
          </AccordionDetails>
        </Accordion>
      </Box>
    </Box>
  );
}

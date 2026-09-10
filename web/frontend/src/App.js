import React, { useMemo, useState } from 'react';
import {
  Container,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Alert,
  IconButton,
  Button,
  Tooltip,
} from '@mui/material';
import { SnackbarProvider } from 'notistack';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import LogoutIcon from '@mui/icons-material/Logout';
import HistoryIcon from '@mui/icons-material/History';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import BrightnessAutoIcon from '@mui/icons-material/BrightnessAuto';
import useMediaQuery from '@mui/material/useMediaQuery';
import SubjectSelector from './components/SubjectSelector';
import ChapterSelector from './components/ChapterSelector';
import LearningHub from './components/LearningHub';
import Login from './components/Login';
import QuizHistory from './components/QuizHistory';
import { AuthProvider, useAuth } from './context/AuthContext';

const steps = [
  { label: 'Select Subject', icon: '📚' },
  { label: 'Choose Chapter', icon: '📖' },
  { label: 'Learn & Practice', icon: '🎓' },
];

function buildTheme(mode) {
  return createTheme({
    palette: {
      mode,
      primary: {
        main: mode === 'dark' ? '#90caf9' : '#1976d2',
      },
      secondary: {
        main: '#dc004e',
      },
      background: {
        default: mode === 'dark' ? '#121212' : '#f5f5f5',
        paper: mode === 'dark' ? '#1e1e1e' : '#ffffff',
      },
    },
    typography: {
      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      h4: { fontWeight: 600 },
      h5: { fontWeight: 600 },
    },
    shape: { borderRadius: 12 },
  });
}

function AppShell() {
  const { user, ready, logout, setTheme } = useAuth();
  const prefersDark = useMediaQuery('(prefers-color-scheme: dark)');
  const [activeStep, setActiveStep] = useState(0);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [error, setError] = useState(null);
  const [view, setView] = useState('learn');

  const resolvedMode =
    (user?.theme || 'system') === 'system' ? (prefersDark ? 'dark' : 'light') : user.theme;
  const theme = useMemo(() => buildTheme(resolvedMode), [resolvedMode]);

  const cycleTheme = () => {
    const order = ['system', 'light', 'dark'];
    const current = user?.theme || 'system';
    const next = order[(order.indexOf(current) + 1) % order.length];
    setTheme(next);
  };

  const themeIcon =
    (user?.theme || 'system') === 'system' ? (
      <BrightnessAutoIcon />
    ) : resolvedMode === 'dark' ? (
      <Brightness4Icon />
    ) : (
      <Brightness7Icon />
    );

  if (!ready) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
          <CircularProgress />
        </Box>
      </ThemeProvider>
    );
  }

  if (!user) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Login />
      </ThemeProvider>
    );
  }

  const handleSubjectSelect = (subject) => {
    setSelectedSubject(subject);
    setSelectedChapter(null);
    setActiveStep(1);
    setError(null);
  };

  const handleChapterSelect = (chapter) => {
    setSelectedChapter(chapter);
    setActiveStep(2);
    setError(null);
  };

  const handleBackToSubjects = () => {
    setSelectedSubject(null);
    setSelectedChapter(null);
    setActiveStep(0);
  };

  const handleBackToChapters = () => {
    setSelectedChapter(null);
    setActiveStep(1);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider maxSnack={3}>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
          <AppBar position="sticky" elevation={2}>
            <Toolbar>
              <MenuBookIcon sx={{ mr: 2, fontSize: 28 }} />
              <Box sx={{ flex: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
                  LearnEasy
                </Typography>
                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                  Hi, {user.username}
                </Typography>
              </Box>
              <Button
                color="inherit"
                startIcon={<HistoryIcon />}
                onClick={() => setView(view === 'history' ? 'learn' : 'history')}
                sx={{ mr: 1, display: { xs: 'none', sm: 'inline-flex' } }}
              >
                History
              </Button>
              <Tooltip title="Quiz history">
                <IconButton
                  color="inherit"
                  onClick={() => setView(view === 'history' ? 'learn' : 'history')}
                  sx={{ display: { xs: 'inline-flex', sm: 'none' } }}
                >
                  <HistoryIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title={`Theme: ${user.theme || 'system'}`}>
                <IconButton color="inherit" onClick={cycleTheme}>
                  {themeIcon}
                </IconButton>
              </Tooltip>
              <Tooltip title="Sign out">
                <IconButton color="inherit" onClick={logout}>
                  <LogoutIcon />
                </IconButton>
              </Tooltip>
            </Toolbar>
          </AppBar>

          {view === 'learn' && (
            <Box sx={{ px: { xs: 2, sm: 3 }, py: 2, bgcolor: 'background.paper', borderBottom: 1, borderColor: 'divider' }}>
              <Stepper activeStep={activeStep} sx={{ display: { xs: 'none', sm: 'flex' } }}>
                {steps.map((step, index) => (
                  <Step key={index} completed={index < activeStep}>
                    <StepLabel>{step.label}</StepLabel>
                  </Step>
                ))}
              </Stepper>
              <Box sx={{ display: { xs: 'flex', sm: 'none' }, justifyContent: 'space-between' }}>
                {steps.map((step, index) => (
                  <Box
                    key={index}
                    sx={{
                      flex: 1,
                      textAlign: 'center',
                      opacity: index <= activeStep ? 1 : 0.5,
                    }}
                  >
                    <Typography variant="h6" sx={{ fontSize: '1.5rem', mb: 0.5 }}>
                      {step.icon}
                    </Typography>
                    <Typography variant="caption" sx={{ fontSize: '0.65rem' }}>
                      {step.label}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          )}

          {error && (
            <Box sx={{ px: 2, py: 1 }}>
              <Alert severity="error" onClose={() => setError(null)}>
                {error}
              </Alert>
            </Box>
          )}

          <Container maxWidth="lg" sx={{ py: { xs: 2, sm: 3 }, flex: 1 }}>
            {view === 'history' ? (
              <QuizHistory onBack={() => setView('learn')} />
            ) : (
              <>
                {activeStep === 0 && (
                  <SubjectSelector onSelectSubject={handleSubjectSelect} />
                )}
                {activeStep === 1 && (
                  <ChapterSelector
                    subject={selectedSubject}
                    onSelectChapter={handleChapterSelect}
                    onBack={handleBackToSubjects}
                  />
                )}
                {activeStep === 2 && (
                  <LearningHub
                    subject={selectedSubject}
                    chapter={selectedChapter}
                    onBack={handleBackToChapters}
                    setError={setError}
                  />
                )}
              </>
            )}
          </Container>
        </Box>
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  );
}

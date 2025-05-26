import React, { useState } from 'react';
import { 
  Container, 
  CssBaseline, 
  Box, 
  Typography, 
  AppBar, 
  Toolbar,
  Paper,
  Stepper,
  Step,
  StepLabel,
  createTheme,
  ThemeProvider
} from '@mui/material';
import JobDescriptionForm from './components/JobDescriptionForm';
import ResumeUpload from './components/ResumeUpload';
import ScreeningResults from './components/ScreeningResults';
import WorkIcon from '@mui/icons-material/Work';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2c3e50',
    },
    secondary: {
      main: '#3498db',
    },
  },
});

const steps = ['Job Description', 'Upload Resumes', 'Screening Results'];

function App() {
  const [activeStep, setActiveStep] = useState(0);
  const [jobDescription, setJobDescription] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [screeningResults, setScreeningResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setJobDescription('');
    setSessionId('');
    setUploadedFiles([]);
    setScreeningResults(null);
    setError(null);
  };

  // Function to render the current step content
  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <JobDescriptionForm 
            jobDescription={jobDescription} 
            setJobDescription={setJobDescription}
            onNext={handleNext}
          />
        );
      case 1:
        return (
          <ResumeUpload 
            jobDescription={jobDescription}
            sessionId={sessionId}
            setSessionId={setSessionId}
            uploadedFiles={uploadedFiles}
            setUploadedFiles={setUploadedFiles}
            onNext={handleNext}
            onBack={handleBack}
            setScreeningResults={setScreeningResults}
            setIsLoading={setIsLoading}
            setError={setError}
          />
        );
      case 2:
        return (
          <ScreeningResults 
            screeningResults={screeningResults}
            isLoading={isLoading}
            error={error}
            onReset={handleReset}
          />
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="absolute" color="primary">
        <Toolbar>
          <WorkIcon sx={{ mr: 2 }} />
          <Typography variant="h6" color="inherit" noWrap>
            Resume Screening Assistant
          </Typography>
        </Toolbar>
      </AppBar>
      <Container component="main" maxWidth="lg" sx={{ mb: 4 }}>
        <Paper variant="outlined" sx={{ my: { xs: 3, md: 6 }, p: { xs: 2, md: 3 }, mt: 8 }}>
          <Typography component="h1" variant="h4" align="center" gutterBottom>
            Resume Screening Tool
          </Typography>
          
          <Stepper activeStep={activeStep} sx={{ pt: 3, pb: 5 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
          
          <Box>
            {getStepContent(activeStep)}
          </Box>
        </Paper>
        <Typography variant="body2" color="text.secondary" align="center">
          {'Copyright © Resume Screening Tool ' + new Date().getFullYear()}
        </Typography>
      </Container>
    </ThemeProvider>
  );
}

export default App;

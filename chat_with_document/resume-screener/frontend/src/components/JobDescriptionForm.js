import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Paper,
  Alert
} from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

const JobDescriptionForm = ({ jobDescription, setJobDescription, onNext }) => {
  const [error, setError] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();
    
    // Validate job description
    if (!jobDescription.trim()) {
      setError('Please enter a job description');
      return;
    }
    
    // Clear any previous errors and proceed to next step
    setError(null);
    onNext();
  };

  return (
    <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
      <Typography variant="h6" gutterBottom>
        Enter Job Description
      </Typography>
      
      <Typography variant="body2" color="text.secondary" paragraph>
        Paste the complete job description text below. The system will analyze the requirements,
        qualifications, and key skills needed for the position.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <TextField
          id="job-description"
          label="Job Description"
          multiline
          fullWidth
          rows={15}
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          placeholder="Paste the complete job description here..."
          variant="outlined"
          sx={{ mb: 2 }}
        />
      </Paper>

      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          type="submit"
          variant="contained"
          endIcon={<ArrowForwardIcon />}
          size="large"
        >
          Continue to Resume Upload
        </Button>
      </Box>
    </Box>
  );
};

export default JobDescriptionForm;

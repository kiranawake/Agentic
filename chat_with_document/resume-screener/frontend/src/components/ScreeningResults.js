import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Paper,
  CircularProgress,
  Alert,
  Divider,
  Card,
  CardContent,
  CardActions,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Stack,
  Grid,
  LinearProgress
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DownloadIcon from '@mui/icons-material/Download';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

const ScreeningResults = ({ screeningResults, isLoading, error, onReset }) => {
  // Helper to get color based on match score
  const getScoreColor = (score) => {
    if (score >= 0.7) return 'success';
    if (score >= 0.4) return 'warning';
    return 'error';
  };

  // Helper to format percentage from decimal
  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(0)}%`;
  };

  // Handle download of report
  const handleDownloadReport = () => {
    if (screeningResults?.report_url) {
      // Open the report URL in a new tab or trigger download
      window.open(screeningResults.report_url, '_blank');
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress size={60} thickness={4} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Processing Resumes...
        </Typography>
        <Typography variant="body2" color="text.secondary">
          This may take a few minutes depending on the number of resumes.
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ mt: 2 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={onReset}
        >
          Start Over
        </Button>
      </Box>
    );
  }

  if (!screeningResults || !screeningResults.results) {
    return (
      <Box sx={{ mt: 2 }}>
        <Alert severity="info" sx={{ mb: 3 }}>
          No screening results available. Please upload resumes and complete the screening process.
        </Alert>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={onReset}
        >
          Start Over
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">
          Screening Results
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={handleDownloadReport}
            sx={{ mr: 2 }}
          >
            Download Report
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={onReset}
          >
            New Screening
          </Button>
        </Box>
      </Box>

      {/* Results Summary */}
      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          {screeningResults.results.length} Resume{screeningResults.results.length !== 1 ? 's' : ''} Analyzed
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Candidates are ranked by their match score with the job description.
        </Typography>
      </Paper>

      {/* Candidate Results */}
      {screeningResults.results.map((result, index) => (
        <Card key={index} variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2}>
              <Grid item xs={12} md={8}>
                <Typography variant="h6" gutterBottom>
                  {result.filename}
                </Typography>
                <Typography variant="body2" paragraph>
                  {result.summary}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center', p: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Match Score
                  </Typography>
                  <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                    <CircularProgress
                      variant="determinate"
                      value={result.match_score * 100}
                      color={getScoreColor(result.match_score)}
                      size={80}
                      thickness={6}
                    />
                    <Box
                      sx={{
                        top: 0,
                        left: 0,
                        bottom: 0,
                        right: 0,
                        position: 'absolute',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <Typography variant="h6" component="div" color="text.secondary">
                        {formatPercentage(result.match_score)}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />
            
            {/* Contact Information */}
            {result.contact_info && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Contact Information
                </Typography>
                <Stack direction="row" spacing={2}>
                  {result.contact_info.email && (
                    <Chip 
                      label={`Email: ${result.contact_info.email}`} 
                      size="small" 
                      variant="outlined" 
                    />
                  )}
                  {result.contact_info.phone && (
                    <Chip 
                      label={`Phone: ${result.contact_info.phone}`} 
                      size="small" 
                      variant="outlined" 
                    />
                  )}
                </Stack>
              </Box>
            )}

            {/* Requirements Analysis */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>Requirements Analysis</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List disablePadding>
                  {result.requirements_analysis.map((req, reqIndex) => (
                    <ListItem key={reqIndex} disablePadding sx={{ py: 1 }}>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {req.match_result.matched ? (
                              <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                            ) : (
                              <CancelIcon color="error" sx={{ mr: 1 }} />
                            )}
                            <Typography variant="body1">
                              {req.requirement}
                            </Typography>
                          </Box>
                        }
                        secondary={req.match_result.explanation}
                      />
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};

export default ScreeningResults;

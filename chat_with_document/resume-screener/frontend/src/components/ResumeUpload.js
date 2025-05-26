import React, { useState, useCallback } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Paper,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Stack
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import axios from 'axios';

const ResumeUpload = ({ 
  jobDescription, 
  sessionId, 
  setSessionId, 
  uploadedFiles, 
  setUploadedFiles, 
  onNext, 
  onBack,
  setScreeningResults,
  setIsLoading,
  setError
}) => {
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  // Handle file drop
  const onDrop = useCallback(acceptedFiles => {
    // Only accept PDF and DOCX files
    const validFiles = acceptedFiles.filter(
      file => file.type === 'application/pdf' || 
             file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    );
    
    if (validFiles.length === 0) {
      setUploadError('Only PDF and DOCX files are accepted.');
      return;
    }
    
    setUploadedFiles(prevFiles => [...prevFiles, ...validFiles]);
    setUploadError(null);
  }, [setUploadedFiles]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    }
  });

  // Remove a file from the list
  const removeFile = (index) => {
    setUploadedFiles(prevFiles => prevFiles.filter((_, i) => i !== index));
  };

  // Upload resumes to the server
  const uploadResumes = async () => {
    if (uploadedFiles.length === 0) {
      setUploadError('Please upload at least one resume file.');
      return;
    }

    setUploading(true);
    setUploadError(null);
    
    try {
      // Create form data with multiple files
      const formData = new FormData();
      uploadedFiles.forEach(file => {
        formData.append('resumes', file);
      });
      
      // Upload the files
      const response = await axios.post('/upload-resumes', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Save the session ID for the next step
      setSessionId(response.data.session_id);
      
      // Proceed to screening
      await screenResumes(response.data.session_id);
    } catch (error) {
      console.error('Error uploading resumes:', error);
      setUploadError(error.response?.data?.detail || 'Failed to upload resumes. Please try again.');
      setUploading(false);
    }
  };

  // Screen the uploaded resumes
  const screenResumes = async (sid) => {
    setIsLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('session_id', sid);
      formData.append('job_description', jobDescription);
      
      const response = await axios.post('/screen-resumes', formData);
      
      setScreeningResults(response.data);
      setIsLoading(false);
      onNext(); // Proceed to results page
    } catch (error) {
      console.error('Error screening resumes:', error);
      setError(error.response?.data?.detail || 'Failed to screen resumes. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ mt: 1 }}>
      <Typography variant="h6" gutterBottom>
        Upload Resumes
      </Typography>
      
      <Typography variant="body2" color="text.secondary" paragraph>
        Upload multiple resume files (PDF or DOCX format). The system will analyze each resume against the job description.
      </Typography>

      {uploadError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {uploadError}
        </Alert>
      )}

      {/* Dropzone area */}
      <Paper 
        variant="outlined" 
        sx={{ 
          p: 3, 
          mb: 3, 
          backgroundColor: isDragActive ? '#f0f7ff' : 'white',
          border: isDragActive ? '2px dashed #3498db' : '1px solid #ddd',
          borderRadius: 2,
          cursor: 'pointer',
          textAlign: 'center'
        }}
        {...getRootProps()}
      >
        <input {...getInputProps()} />
        <UploadFileIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        {isDragActive ? (
          <Typography>Drop the files here...</Typography>
        ) : (
          <Typography>Drag and drop resume files here, or click to select files</Typography>
        )}
        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
          Supported formats: PDF, DOCX
        </Typography>
      </Paper>

      {/* File list */}
      {uploadedFiles.length > 0 && (
        <Paper variant="outlined" sx={{ mb: 3 }}>
          <Typography variant="subtitle1" sx={{ p: 2, pb: 0 }}>
            {uploadedFiles.length} {uploadedFiles.length === 1 ? 'file' : 'files'} selected
          </Typography>
          <List>
            {uploadedFiles.map((file, index) => (
              <React.Fragment key={`${file.name}-${index}`}>
                <ListItem
                  secondaryAction={
                    <Button 
                      onClick={() => removeFile(index)}
                      color="error"
                      size="small"
                    >
                      Remove
                    </Button>
                  }
                >
                  <ListItemIcon>
                    <InsertDriveFileIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary={file.name}
                    secondary={`${(file.size / 1024).toFixed(2)} KB`}
                  />
                </ListItem>
                {index < uploadedFiles.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}

      {/* Navigation buttons */}
      <Stack direction="row" spacing={2} justifyContent="space-between">
        <Button
          onClick={onBack}
          startIcon={<ArrowBackIcon />}
          disabled={uploading}
        >
          Back to Job Description
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={uploadResumes}
          endIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <ArrowForwardIcon />}
          disabled={uploading || uploadedFiles.length === 0}
        >
          {uploading ? 'Processing...' : 'Screen Resumes'}
        </Button>
      </Stack>
    </Box>
  );
};

export default ResumeUpload;

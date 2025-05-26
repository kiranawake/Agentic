# Resume Screening Application

A comprehensive application for screening resumes against job descriptions, allowing hiring managers and recruiters to efficiently evaluate candidate profiles for job openings.

## Features

- **Job Description Analysis:** Extract key requirements and qualifications from job descriptions
- **Multiple Resume Processing:** Support for batch processing of multiple resumes at once
- **Document Parsing:** Extract text from PDF and DOCX resume formats
- **Intelligent Matching:** Use AI to evaluate the match between resumes and job requirements
- **Detailed Reports:** Generate comprehensive screening reports with match scores and analysis
- **Downloadable Results:** Export screening results as PDF for easy sharing
- **Modern UI:** Clean and intuitive user interface with step-by-step workflow

## Project Structure

```
resume-screener/
├── backend/                # Python FastAPI backend
│   ├── document_processor.py  # Resume and JD text extraction
│   ├── screening_engine.py    # Resume matching and analysis
│   ├── report_generator.py    # PDF report generation
│   ├── main.py                # API endpoints
│   └── requirements.txt       # Python dependencies
│
└── frontend/               # React frontend
    ├── public/                # Static files
    └── src/                   # React components and logic
        ├── components/        # UI components
        │   ├── JobDescriptionForm.js   # JD input form
        │   ├── ResumeUpload.js         # Resume upload component
        │   └── ScreeningResults.js     # Results display
        ├── App.js                      # Main application
        └── index.js                    # Entry point
```

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd resume-screener/backend
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a .env file in the backend directory):
   ```
   OPENAI_API_KEY=your_openai_api_key  # Optional, if using OpenAI
   GROQ_API_KEY=your_groq_api_key      # Optional, if using Groq
   ```

5. Start the backend server:
   ```
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd resume-screener/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the frontend application:
   ```
   npm start
   ```

4. The application should now be running at http://localhost:3000

## Usage

1. **Enter Job Description:**
   - Paste the complete job description in the first step
   - The system will automatically extract key requirements

2. **Upload Resumes:**
   - Drag and drop or select resume files (PDF or DOCX)
   - Multiple resumes can be uploaded at once

3. **View Results:**
   - Review match scores and detailed analysis
   - See which requirements each candidate matches
   - Download a comprehensive report

## Technology Stack

### Backend
- FastAPI - High-performance API framework
- LangChain - NLP processing and model integration
- PyPDF2/docx2txt - Document parsing
- HuggingFace models - Text embeddings
- Jinja2/PDFKit - Report generation

### Frontend
- React - UI framework
- Material-UI - Component library
- Axios - API client
- React-Dropzone - File upload functionality

## License

MIT

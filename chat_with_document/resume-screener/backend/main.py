from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
import os
import shutil
import uuid
import json
from datetime import datetime

# Import processor modules
from document_processor import extract_text_from_resume, extract_text_from_jd
from screening_engine import screen_resumes
from report_generator import generate_report

app = FastAPI(title="Resume Screening API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create temp directory for file uploads
UPLOAD_DIR = "temp_uploads"
REPORTS_DIR = "generated_reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Resume Screening API"}

@app.post("/upload-job-description")
async def upload_job_description(job_description: str = Form(...)):
    """
    Upload job description as text
    """
    if not job_description:
        raise HTTPException(status_code=400, detail="Job description cannot be empty")
    
    # Process JD text
    jd_data = extract_text_from_jd(job_description)
    return {"message": "Job description processed successfully", "jd_data": jd_data}

@app.post("/upload-resumes")
async def upload_resumes(resumes: List[UploadFile] = File(...)):
    """
    Upload multiple resume files (PDF/DOCX)
    """
    if not resumes:
        raise HTTPException(status_code=400, detail="No resume files uploaded")
    
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    saved_files = []
    for resume in resumes:
        if not (resume.filename.endswith('.pdf') or resume.filename.endswith('.docx')):
            continue  # Skip invalid file types
        
        file_path = os.path.join(session_dir, resume.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
        saved_files.append({"filename": resume.filename, "path": file_path})
    
    if not saved_files:
        raise HTTPException(status_code=400, detail="No valid resume files uploaded (PDF/DOCX only)")
    
    return {"message": f"{len(saved_files)} resume(s) uploaded successfully", "session_id": session_id, "files": saved_files}

@app.post("/screen-resumes")
async def screen_resumes_endpoint(
    session_id: str = Form(...),
    job_description: str = Form(...)
):
    """
    Screen uploaded resumes against job description
    """
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    
    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get all resume files in the session directory
    resume_files = []
    for filename in os.listdir(session_dir):
        if filename.endswith('.pdf') or filename.endswith('.docx'):
            resume_files.append(os.path.join(session_dir, filename))
    
    if not resume_files:
        raise HTTPException(status_code=400, detail="No resume files found in session")
    
    # Process resumes
    resumes_data = []
    for file_path in resume_files:
        filename = os.path.basename(file_path)
        resume_text = extract_text_from_resume(file_path)
        resumes_data.append({
            "filename": filename,
            "text": resume_text
        })
    
    # Screen resumes against job description
    screening_results = screen_resumes(job_description, resumes_data)
    
    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"screening_report_{timestamp}.pdf"
    report_path = os.path.join(REPORTS_DIR, report_filename)
    
    generate_report(screening_results, job_description, report_path)
    
    return {
        "message": "Screening completed successfully",
        "results": screening_results,
        "report_url": f"/download-report/{report_filename}"
    }

@app.get("/download-report/{filename}")
async def download_report(filename: str):
    """
    Download generated screening report
    """
    report_path = os.path.join(REPORTS_DIR, filename)
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        path=report_path, 
        filename=filename,
        media_type="application/pdf"
    )

@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up temporary files on shutdown
    """
    # In production, you might want a more sophisticated cleanup strategy
    # e.g., cleaning files older than X days
    try:
        if os.path.exists(UPLOAD_DIR):
            shutil.rmtree(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    except Exception as e:
        pass  # Fail silently on shutdown

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

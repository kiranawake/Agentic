import PyPDF2
import docx2txt
import re
import os
from typing import Dict, List, Any

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from a PDF file
    """
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        text = f"Error processing PDF file: {e}"
    
    return text

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text content from a DOCX file
    """
    try:
        text = docx2txt.process(file_path)
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return f"Error processing DOCX file: {e}"

def extract_text_from_resume(file_path: str) -> str:
    """
    Extract text from resume file based on file extension
    """
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        return "Unsupported file format. Please upload PDF or DOCX."

def extract_structured_resume_data(resume_text: str) -> Dict[str, Any]:
    """
    Extract structured data from resume text
    Including sections like education, experience, skills, etc.
    """
    # Basic section identification using regex patterns
    # Note: This is a simplified approach and might need enhancement for production
    
    sections = {
        "contact_info": {},
        "education": [],
        "experience": [],
        "skills": [],
        "certifications": [],
        "full_text": resume_text
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.findall(email_pattern, resume_text)
    if email_matches:
        sections["contact_info"]["email"] = email_matches[0]
    
    # Extract phone number (simplified pattern)
    phone_pattern = r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    phone_matches = re.findall(phone_pattern, resume_text)
    if phone_matches:
        sections["contact_info"]["phone"] = phone_matches[0]
    
    # Extract skills (look for common skill section identifiers)
    skills_section = re.search(r'(?i)skills?(?::[^\n]*)(.*?)(?:\n\s*\n|\n\s*[A-Z])', resume_text, re.DOTALL)
    if skills_section:
        skills_text = skills_section.group(1).strip()
        # Split skills by commas, bullets, or newlines
        skills = re.split(r'[,•\n]', skills_text)
        sections["skills"] = [skill.strip() for skill in skills if skill.strip()]
    
    # Extract education (simplified)
    education_section = re.search(r'(?i)education(?::[^\n]*)(.*?)(?:\n\s*\n|\n\s*[A-Z])', resume_text, re.DOTALL)
    if education_section:
        edu_text = education_section.group(1).strip()
        edu_entries = re.split(r'\n\s*\n', edu_text)
        for entry in edu_entries:
            if entry.strip():
                sections["education"].append(entry.strip())
    
    # Extract experience (simplified)
    experience_section = re.search(r'(?i)(?:experience|employment|work)(?::[^\n]*)(.*?)(?:\n\s*\n|\n\s*[A-Z])', resume_text, re.DOTALL)
    if experience_section:
        exp_text = experience_section.group(1).strip()
        exp_entries = re.split(r'\n\s*\n', exp_text)
        for entry in exp_entries:
            if entry.strip():
                sections["experience"].append(entry.strip())
    
    return sections

def extract_text_from_jd(jd_text: str) -> Dict[str, Any]:
    """
    Process job description text to extract structured data
    """
    # Extract key requirements/skills from job description
    jd_data = {
        "full_text": jd_text,
        "requirements": [],
        "responsibilities": [],
        "qualifications": [],
        "keywords": []
    }
    
    # Extract requirements section
    requirements_section = re.search(r'(?i)(?:requirements|qualifications)(?::[^\n]*)(.*?)(?:\n\s*\n|\n\s*[A-Z]|$)', jd_text, re.DOTALL)
    if requirements_section:
        req_text = requirements_section.group(1).strip()
        requirements = re.findall(r'(?:•|-|\*|\d+\.)\s*(.*?)(?:\n|$)', req_text)
        if requirements:
            jd_data["requirements"] = [req.strip() for req in requirements if req.strip()]
        else:
            # If bullet points aren't found, try splitting by newlines
            requirements = re.split(r'\n', req_text)
            jd_data["requirements"] = [req.strip() for req in requirements if req.strip()]
    
    # Extract responsibilities section
    responsibilities_section = re.search(r'(?i)(?:responsibilities|duties|role)(?::[^\n]*)(.*?)(?:\n\s*\n|\n\s*[A-Z]|$)', jd_text, re.DOTALL)
    if responsibilities_section:
        resp_text = responsibilities_section.group(1).strip()
        responsibilities = re.findall(r'(?:•|-|\*|\d+\.)\s*(.*?)(?:\n|$)', resp_text)
        if responsibilities:
            jd_data["responsibilities"] = [resp.strip() for resp in responsibilities if resp.strip()]
        else:
            # If bullet points aren't found, try splitting by newlines
            responsibilities = re.split(r'\n', resp_text)
            jd_data["responsibilities"] = [resp.strip() for resp in responsibilities if resp.strip()]
    
    # Extract key skills/technologies (look for technical terms, programming languages, etc.)
    skill_patterns = [
        r'\b(?:Java|Python|C\+\+|JavaScript|React|Angular|Vue|Node\.js|SQL|NoSQL|AWS|Azure|GCP|Docker|Kubernetes|REST|API|JSON|HTML|CSS|Git)\b',
        r'\b(?:Bachelor\'s|Master\'s|PhD|degree)\b',
        r'\b\d+\+?\s+years?\s+(?:of\s+)?experience\b'
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, jd_text, re.IGNORECASE)
        if matches:
            jd_data["keywords"].extend([match.strip() for match in matches])
    
    # Remove duplicates
    jd_data["keywords"] = list(set(jd_data["keywords"]))
    
    return jd_data

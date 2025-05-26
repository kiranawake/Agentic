from typing import Dict, List, Any
import re
from langchain_community.llms import HuggingFaceHub
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from document_processor import extract_structured_resume_data

# Initialize embedding model
def get_embeddings_model():
    try:
        # Try instructor embeddings first
        return HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    except Exception as e:
        print(f"Failed to load instructor embeddings: {e}")
        # Fall back to another model if needed
        # You can implement fallback logic here
        raise

# Initialize LLM model
def get_llm():
    # Check if Groq API key is available
    if os.environ.get("GROQ_API_KEY"):
        try:
            return ChatGroq(model='llama3-70b-8192', temperature=0.3)
        except Exception as e:
            print(f"Failed to initialize Groq LLM: {e}")
    
    # Fall back to Hugging Face model
    try:
        return HuggingFaceHub(repo_id="google/flan-t5-large", model_kwargs={"temperature": 0.3})
    except Exception as e:
        print(f"Failed to initialize Hugging Face LLM: {e}")
        raise

def get_embedding(text: str, embeddings_model):
    """Get vector embedding for text"""
    try:
        return embeddings_model.embed_query(text)
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return a zero vector as fallback (not ideal but prevents crashes)
        return [0.0] * 768  # Typical embedding size

def calculate_similarity(vec1, vec2) -> float:
    """Calculate cosine similarity between two vectors"""
    # Reshape for sklearn's cosine_similarity
    vec1_reshaped = np.array(vec1).reshape(1, -1)
    vec2_reshaped = np.array(vec2).reshape(1, -1)
    
    return float(cosine_similarity(vec1_reshaped, vec2_reshaped)[0][0])

def analyze_skill_match(jd_skill: str, resume_skills: List[str], llm) -> Dict[str, Any]:
    """
    Analyze if a specific JD skill/requirement is matched in the resume skills
    Uses LLM for semantic matching rather than just keyword matching
    """
    if not resume_skills:
        return {
            "matched": False,
            "confidence": 0.0,
            "explanation": "No skills listed in resume."
        }
    
    # Prepare prompt for LLM
    prompt = f"""
    Task: Determine if the candidate's skills match the job requirement.
    
    Job Requirement: {jd_skill}
    
    Candidate Skills:
    {', '.join(resume_skills)}
    
    Analyze if the candidate's skills satisfy the job requirement. Consider synonyms and related skills.
    Provide your answer in the following format:
    
    Matched: [Yes/No]
    Confidence: [0-100]
    Explanation: [Your detailed reasoning]
    """
    
    try:
        response = llm.predict(prompt)
        
        # Parse the response
        match_result = {
            "matched": False,
            "confidence": 0.0,
            "explanation": "Could not determine match."
        }
        
        # Extract matched status
        matched_match = re.search(r'Matched:\s*(Yes|No)', response, re.IGNORECASE)
        if matched_match:
            match_result["matched"] = matched_match.group(1).lower() == "yes"
        
        # Extract confidence
        confidence_match = re.search(r'Confidence:\s*(\d+)', response)
        if confidence_match:
            match_result["confidence"] = float(confidence_match.group(1)) / 100.0
        
        # Extract explanation
        explanation_match = re.search(r'Explanation:\s*(.*)', response, re.DOTALL)
        if explanation_match:
            match_result["explanation"] = explanation_match.group(1).strip()
        
        return match_result
    
    except Exception as e:
        print(f"Error analyzing skill match with LLM: {e}")
        # Fallback to simpler matching
        simple_match = any(jd_skill.lower() in skill.lower() for skill in resume_skills)
        return {
            "matched": simple_match,
            "confidence": 0.7 if simple_match else 0.0,
            "explanation": "Based on direct keyword matching."
        }

def screen_resume(job_description: str, resume_data: Dict[str, Any], 
                 embeddings_model, llm) -> Dict[str, Any]:
    """
    Screen a single resume against a job description
    """
    # Extract structured data from resume text if not already done
    if "skills" not in resume_data:
        resume_structured = extract_structured_resume_data(resume_data["text"])
    else:
        resume_structured = resume_data
    
    # Process job description
    from document_processor import extract_text_from_jd
    jd_data = extract_text_from_jd(job_description)
    
    # Get embeddings for overall job description and resume
    jd_embedding = get_embedding(job_description, embeddings_model)
    resume_embedding = get_embedding(resume_data["text"], embeddings_model)
    
    # Calculate overall similarity
    overall_similarity = calculate_similarity(jd_embedding, resume_embedding)
    
    # Analyze requirements match
    requirements_analysis = []
    for req in jd_data["requirements"]:
        requirement_match = analyze_skill_match(req, resume_structured.get("skills", []), llm)
        requirements_analysis.append({
            "requirement": req,
            "match_result": requirement_match
        })
    
    # Calculate match score (simple weighted approach)
    # 50% from overall similarity, 50% from requirements matching
    matched_requirements = sum(1 for req in requirements_analysis if req["match_result"]["matched"])
    total_requirements = len(requirements_analysis) or 1  # Avoid division by zero
    requirements_score = matched_requirements / total_requirements
    
    match_score = (0.5 * overall_similarity) + (0.5 * requirements_score)
    
    # Generate summary using LLM
    summary_prompt = f"""
    Task: Provide a concise summary of how well a candidate's resume matches a job description.
    
    Job Description Summary:
    {job_description[:500]}...
    
    Key Requirements:
    {', '.join(jd_data["requirements"][:5])}
    
    Candidate Resume Summary:
    {resume_data["text"][:500]}...
    
    Overall Match Score: {match_score:.2f} out of 1.0
    
    Provide a 3-5 sentence summary evaluating this candidate's fit for the role. Highlight strengths and weaknesses.
    """
    
    try:
        summary = llm.predict(summary_prompt)
    except Exception as e:
        print(f"Error generating summary: {e}")
        summary = f"Match score: {match_score:.2f}. The candidate's profile has been analyzed against the job requirements."
    
    # Compile final screening result
    screening_result = {
        "filename": resume_data.get("filename", "Unknown"),
        "match_score": float(match_score),
        "overall_similarity": float(overall_similarity),
        "requirements_match_rate": float(requirements_score),
        "requirements_analysis": requirements_analysis,
        "summary": summary,
        "contact_info": resume_structured.get("contact_info", {})
    }
    
    return screening_result

def screen_resumes(job_description: str, resumes_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Screen multiple resumes against a job description
    """
    try:
        # Initialize models
        embeddings_model = get_embeddings_model()
        llm = get_llm()
        
        screening_results = []
        for resume_data in resumes_data:
            result = screen_resume(job_description, resume_data, embeddings_model, llm)
            screening_results.append(result)
        
        # Sort results by match score (descending)
        screening_results.sort(key=lambda x: x["match_score"], reverse=True)
        
        return screening_results
    
    except Exception as e:
        print(f"Error in screening resumes: {e}")
        # Return basic error result
        return [{"error": f"Failed to screen resumes: {str(e)}"}]

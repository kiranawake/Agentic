import jinja2
import pdfkit
import os
import pandas as pd
from typing import Dict, List, Any
import json
from datetime import datetime

# HTML template for the report
REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Resume Screening Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #2980b9;
            margin-top: 20px;
        }
        .summary {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .candidate {
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .candidate-header {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }
        .score {
            font-size: 18px;
            font-weight: bold;
        }
        .score-high {
            color: #27ae60;
        }
        .score-medium {
            color: #f39c12;
        }
        .score-low {
            color: #e74c3c;
        }
        .requirement {
            margin: 10px 0;
        }
        .matched {
            color: #27ae60;
        }
        .not-matched {
            color: #e74c3c;
        }
        .contact-info {
            background-color: #eaf2f8;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }
        .explanation {
            font-style: italic;
            color: #7f8c8d;
            margin-left: 20px;
        }
        .timestamp {
            color: #7f8c8d;
            font-size: 12px;
            text-align: right;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <h1>Resume Screening Report</h1>
    
    <div class="summary">
        <h2>Job Description</h2>
        <p>{{ job_description|truncate(300) }}</p>
    </div>
    
    <h2>Screening Results ({{ results|length }} candidates)</h2>
    
    {% for result in results %}
    <div class="candidate">
        <div class="candidate-header">
            <h3>{{ result.filename }}</h3>
            {% if result.match_score >= 0.7 %}
                <div class="score score-high">Match Score: {{ "%.2f"|format(result.match_score) }}</div>
            {% elif result.match_score >= 0.4 %}
                <div class="score score-medium">Match Score: {{ "%.2f"|format(result.match_score) }}</div>
            {% else %}
                <div class="score score-low">Match Score: {{ "%.2f"|format(result.match_score) }}</div>
            {% endif %}
        </div>
        
        <div class="summary">
            <h4>Summary</h4>
            <p>{{ result.summary }}</p>
        </div>
        
        {% if result.contact_info %}
        <div class="contact-info">
            <h4>Contact Information</h4>
            {% if result.contact_info.email %}
                <p><strong>Email:</strong> {{ result.contact_info.email }}</p>
            {% endif %}
            {% if result.contact_info.phone %}
                <p><strong>Phone:</strong> {{ result.contact_info.phone }}</p>
            {% endif %}
        </div>
        {% endif %}
        
        <h4>Requirements Analysis</h4>
        {% for req_analysis in result.requirements_analysis %}
        <div class="requirement">
            <strong>{{ req_analysis.requirement }}</strong>
            {% if req_analysis.match_result.matched %}
                <span class="matched"> ✓ Matched</span>
            {% else %}
                <span class="not-matched"> ✗ Not Matched</span>
            {% endif %}
            <div class="explanation">{{ req_analysis.match_result.explanation|truncate(150) }}</div>
        </div>
        {% endfor %}
    </div>
    {% endfor %}
    
    <div class="timestamp">
        Report generated on {{ timestamp }}
    </div>
</body>
</html>
"""

def generate_report(screening_results: List[Dict[str, Any]], job_description: str, output_path: str) -> str:
    """
    Generate a PDF report of resume screening results
    """
    try:
        # Set up jinja2 template
        template = jinja2.Template(REPORT_TEMPLATE)
        
        # Prepare the report data
        report_data = {
            "results": screening_results,
            "job_description": job_description,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Render the HTML template
        html_content = template.render(**report_data)
        
        # Save the HTML content to a temporary file
        html_path = f"{output_path}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Convert HTML to PDF using pdfkit
        try:
            # For Windows, you may need to specify the path to wkhtmltopdf
            config = None
            if os.name == "nt":  # Windows
                config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
                pdfkit.from_file(html_path, output_path, configuration=config)
            else:
                pdfkit.from_file(html_path, output_path)
            
            # Clean up the temporary HTML file
            if os.path.exists(html_path):
                os.remove(html_path)
            
            return output_path
        
        except Exception as e:
            print(f"Error converting HTML to PDF: {e}")
            print("Saving as HTML file instead...")
            # If PDF conversion fails, keep the HTML file as fallback
            return html_path
    
    except Exception as e:
        print(f"Error generating report: {e}")
        
        # Fallback to simple JSON report
        try:
            json_path = f"{output_path}.json"
            with open(json_path, "w") as f:
                json.dump(screening_results, f, indent=2)
            return json_path
        except:
            raise Exception(f"Failed to generate report: {str(e)}")

def generate_csv_report(screening_results: List[Dict[str, Any]], output_path: str) -> str:
    """
    Generate a CSV report of resume screening results
    """
    try:
        # Extract relevant data for CSV
        csv_data = []
        for result in screening_results:
            row = {
                "Filename": result.get("filename", "Unknown"),
                "Match Score": result.get("match_score", 0),
                "Overall Similarity": result.get("overall_similarity", 0),
                "Requirements Match Rate": result.get("requirements_match_rate", 0),
                "Email": result.get("contact_info", {}).get("email", ""),
                "Phone": result.get("contact_info", {}).get("phone", ""),
                "Summary": result.get("summary", "").replace("\n", " ")
            }
            csv_data.append(row)
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(csv_data)
        csv_path = f"{output_path}.csv"
        df.to_csv(csv_path, index=False)
        
        return csv_path
    
    except Exception as e:
        print(f"Error generating CSV report: {e}")
        raise Exception(f"Failed to generate CSV report: {str(e)}")

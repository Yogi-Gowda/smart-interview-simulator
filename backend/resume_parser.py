# Resume Parser Module
# Extracts skills, technologies, projects from PDF/DOCX resumes

import os
import re
from pathlib import Path
from typing import Dict, List, Optional

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

try:
    import spacy
except ImportError:
    spacy = None

# Load spaCy model if available
if spacy:
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        nlp = None
else:
    nlp = None


class ResumeParser:
    """Parse resumes and extract relevant information"""
    
    # Common tech skills and keywords
    TECH_KEYWORDS = {
        "programming_languages": [
            "python", "java", "javascript", "c++", "c#", "ruby", "go", "rust",
            "typescript", "php", "swift", "kotlin", "scala", "r"
        ],
        "web_technologies": [
            "html", "css", "react", "angular", "vue", "node.js", "express",
            "django", "flask", "spring", "asp.net", "rest api", "graphql"
        ],
        "databases": [
            "mysql", "postgresql", "mongodb", "oracle", "sqlite", "redis",
            "elasticsearch", "cassandra", "firebase"
        ],
        "tools": [
            "git", "docker", "kubernetes", "jenkins", "aws", "azure", "gcp",
            "linux", "windows", "jira", "confluence"
        ],
        "data_science": [
            "machine learning", "deep learning", "tensorflow", "pytorch",
            "pandas", "numpy", "scikit-learn", "data analysis", "visualization",
            "tableau", "power bi", "nlp", "computer vision"
        ],
        "testing": [
            "selenium", "junit", "pytest", "unittest", "cypress", "postman",
            "jmeter", "load testing", "unit testing", "integration testing"
        ],
        "methodologies": [
            "agile", "scrum", "waterfall", "devops", "ci/cd", "tdd", "bdd"
        ]
    }
    
    def __init__(self):
        self.extracted_data = {}
    
    def parse_resume(self, file_path: str, filename: str) -> Dict:
        """Main method to parse resume based on file type"""
        ext = Path(filename).suffix.lower()
        
        if ext == ".pdf":
            return self._parse_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return self._parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def _parse_pdf(self, file_path: str) -> Dict:
        """Extract text from PDF"""
        if not PyPDF2:
            raise ImportError("PyPDF2 is required for PDF parsing. Install with: pip install PyPDF2")
        
        text = ""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Failed to read PDF: {str(e)}")
        
        return self._extract_info(text)
    
    def _parse_docx(self, file_path: str) -> Dict:
        """Extract text from DOCX"""
        if not docx:
            raise ImportError("python-docx is required for DOCX parsing. Install with: pip install python-docx")
        
        text = ""
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            raise Exception(f"Failed to read DOCX: {str(e)}")
        
        return self._extract_info(text)
    
    def _extract_info(self, text: str) -> Dict:
        """Extract structured information from resume text"""
        text = text.lower()
        
        # Extract skills
        skills = self._extract_skills(text)
        
        # Extract technologies
        technologies = self._extract_technologies(text)
        
        # Extract projects (look for project descriptions)
        projects = self._extract_projects(text)
        
        # Extract experience level
        experience = self._extract_experience(text)
        
        # Extract education
        education = self._extract_education(text)
        
        return {
            "skills": skills,
            "technologies": technologies,
            "projects": projects,
            "experience_years": experience,
            "education": education,
            "raw_text_length": len(text)
        }
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from text"""
        found_skills = []
        
        for category, keywords in self.TECH_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    if keyword not in found_skills:
                        found_skills.append(keyword)
        
        return found_skills
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract technology names"""
        technologies = []
        
        # Common technology patterns
        tech_patterns = [
            r'\b(Python|Java|JavaScript|C\+\+|C#|Ruby|Go|Rust)\b',
            r'\b(React|Angular|Vue|Node|Django|Flask)\b',
            r'\b(MySQL|PostgreSQL|MongoDB|Redis)\b',
            r'\b(AWS|Azure|GCP|Docker|Kubernetes)\b',
            r'\b(TensorFlow|PyTorch|Pandas|NumPy)\b',
            r'\b(Git|Jenkins|Jira)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            technologies.extend(matches)
        
        return list(set(technologies))
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """Extract project information"""
        projects = []
        
        # Look for project keywords
        project_keywords = ["project", "developed", "built", "created", "implemented"]
        
        # Split into sentences and look for project-like content
        sentences = text.split(".")
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in project_keywords):
                if len(sentence) > 50 and len(sentence) < 500:
                    projects.append({
                        "description": sentence.strip(),
                        "technologies": self._extract_technologies(sentence)
                    })
        
        return projects[:5]  # Limit to 5 projects
    
    def _extract_experience(self, text: str) -> int:
        """Extract years of experience"""
        # Look for patterns like "X years", "X+ years"
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'experience\s*of\s*(\d+)\+?\s*years',
            r'(\d+)\s*-\s*\d+\s*years'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Default to 0 (fresher)
        return 0
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education details"""
        education = []
        
        # Degree patterns
        degree_patterns = {
            "btech": r"b\.?tech|bachelor.*technology",
            "mca": r"m\.?ca|master.*computer",
            "bsc": r"b\.?sc|bachelor.*science",
            "msc": r"m\.?sc|master.*science",
            "phd": r"ph\.?d|doctor.*philosophy"
        }
        
        for degree, pattern in degree_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                education.append(degree.upper())
        
        return education if education else ["Not specified"]
    
    def get_skill_categories(self) -> Dict[str, List[str]]:
        """Return categorized skills for question generation"""
        return self.TECH_KEYWORDS


# Standalone function for testing
def parse_resume_file(file_path: str) -> Dict:
    """Quick function to parse a resume file"""
    parser = ResumeParser()
    filename = os.path.basename(file_path)
    return parser.parse_resume(file_path, filename)


if __name__ == "__main__":
    # Test the parser
    parser = ResumeParser()
    print("Resume Parser Module")
    print("Available skill categories:", list(parser.TECH_KEYWORDS.keys()))
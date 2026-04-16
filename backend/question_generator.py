# Question Generator Module
# Generates interview questions based on job role, difficulty, and resume

import json
import random
from typing import Dict, List, Optional
from pathlib import Path


class QuestionGenerator:
    """Generate interview questions based on various parameters"""
    
    def __init__(self, dataset_path: str = None):
        """Initialize with optional dataset path"""
        if dataset_path is None:
            # Default dataset path
            dataset_path = Path(__file__).parent.parent / "dataset" / "questions.json"
        
        self.dataset = self._load_dataset(dataset_path)
        self.generated_questions = []
    
    def _load_dataset(self, path: Path) -> Dict:
        """Load question dataset from JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default questions if file not found
            return self._get_default_questions()
    
    def _get_default_questions(self) -> Dict:
        """Return default question dataset"""
        return {
            "software_developer": {
                "easy": [
                    {"text": "What is Object-Oriented Programming?", "category": "oop", "expected_keywords": ["class", "object", "inheritance", "encapsulation"], "time_limit": 60},
                    {"text": "What is an API?", "category": "web", "expected_keywords": ["interface", "request", "response"], "time_limit": 60},
                    {"text": "What is a variable?", "category": "programming", "expected_keywords": ["storage", "value", "data type"], "time_limit": 45},
                    {"text": "Explain what a database is.", "category": "database", "expected_keywords": ["storage", "data", "table"], "time_limit": 60},
                    {"text": "What is version control?", "category": "tools", "expected_keywords": ["git", "commit", "branch"], "time_limit": 60}
                ],
                "medium": [
                    {"text": "Explain the difference between REST and SOAP APIs.", "category": "web", "expected_keywords": ["rest", "soap", "xml", "json", "http"], "time_limit": 120},
                    {"text": "What is SQL injection and how can you prevent it?", "category": "security", "expected_keywords": ["injection", "parameterized", "validation"], "time_limit": 120},
                    {"text": "Explain the concept of recursion with an example.", "category": "programming", "expected_keywords": ["function", "base case", "stack"], "time_limit": 120},
                    {"text": "What is the difference between GET and POST methods?", "category": "web", "expected_keywords": ["request", "data", "security"], "time_limit": 90},
                    {"text": "Explain ACID properties in databases.", "category": "database", "expected_keywords": ["atomicity", "consistency", "isolation", "durability"], "time_limit": 120}
                ],
                "hard": [
                    {"text": "Explain microservices architecture and its advantages over monolithic architecture.", "category": "architecture", "expected_keywords": ["microservices", "deployment", "scalability", "loose coupling"], "time_limit": 180},
                    {"text": "What is the CAP theorem and how does it apply to distributed systems?", "category": "distributed_systems", "expected_keywords": ["consistency", "availability", "partition tolerance"], "time_limit": 180},
                    {"text": "Explain the concept of dependency injection and its benefits.", "category": "design_patterns", "expected_keywords": ["inversion of control", "loose coupling", "testability"], "time_limit": 150},
                    {"text": "What are design patterns? Explain Singleton and Factory patterns.", "category": "design_patterns", "expected_keywords": ["singleton", "factory", "creational", "object creation"], "time_limit": 150},
                    {"text": "Explain the working of a hash table and handle collisions.", "category": "data_structures", "expected_keywords": ["hash function", "collision", "chaining", "open addressing"], "time_limit": 180}
                ]
            },
            "data_analyst": {
                "easy": [
                    {"text": "What is data analysis?", "category": "basics", "expected_keywords": ["data", "insights", "patterns"], "time_limit": 60},
                    {"text": "What is a spreadsheet?", "category": "tools", "expected_keywords": ["rows", "columns", "cells"], "time_limit": 45},
                    {"text": "Explain the difference between data and information.", "category": "basics", "expected_keywords": ["data", "information", "processed"], "time_limit": 60},
                    {"text": "What is a chart or graph?", "category": "visualization", "expected_keywords": ["visual", "data", "representation"], "time_limit": 45},
                    {"text": "What is data cleaning?", "category": "preprocessing", "expected_keywords": ["missing", "duplicate", "errors"], "time_limit": 60}
                ],
                "medium": [
                    {"text": "Explain the difference between correlation and causation.", "category": "statistics", "expected_keywords": ["correlation", "causation", "relationship"], "time_limit": 120},
                    {"text": "What is SQL and why is it important for data analysis?", "category": "database", "expected_keywords": ["query", "database", "select"], "time_limit": 120},
                    {"text": "Explain the concept of data normalization.", "category": "preprocessing", "expected_keywords": ["scale", "range", "standardization"], "time_limit": 120},
                    {"text": "What are the measures of central tendency?", "category": "statistics", "expected_keywords": ["mean", "median", "mode"], "time_limit": 90},
                    {"text": "Explain what a pivot table is used for.", "category": "tools", "expected_keywords": ["summarize", "aggregate", "filter"], "time_limit": 90}
                ],
                "hard": [
                    {"text": "Explain the concept of hypothesis testing and p-value.", "category": "statistics", "expected_keywords": ["hypothesis", "p-value", "significance", "null hypothesis"], "time_limit": 180},
                    {"text": "What is the difference between supervised and unsupervised learning?", "category": "machine_learning", "expected_keywords": ["labeled", "unlabeled", "training", "prediction"], "time_limit": 180},
                    {"text": "Explain the bias-variance tradeoff in machine learning.", "category": "machine_learning", "expected_keywords": ["bias", "variance", "overfitting", "underfitting"], "time_limit": 180},
                    {"text": "What is time series analysis and when is it used?", "category": "analysis", "expected_keywords": ["temporal", "trend", "seasonality", "forecast"], "time_limit": 150},
                    {"text": "Explain the concept of feature engineering in machine learning.", "category": "machine_learning", "expected_keywords": ["features", "transformation", "selection", "engineering"], "time_limit": 150}
                ]
            },
            "software_testing": {
                "easy": [
                    {"text": "What is software testing?", "category": "basics", "expected_keywords": ["quality", "defects", "verification"], "time_limit": 60},
                    {"text": "What is a test case?", "category": "basics", "expected_keywords": ["steps", "expected", "result"], "time_limit": 45},
                    {"text": "What is the difference between manual and automated testing?", "category": "basics", "expected_keywords": ["manual", "automated", "tools"], "time_limit": 60},
                    {"text": "What is a bug?", "category": "basics", "expected_keywords": ["defect", "error", "issue"], "time_limit": 45},
                    {"text": "Explain what is meant by test execution.", "category": "process", "expected_keywords": ["run", "execute", "results"], "time_limit": 60}
                ],
                "medium": [
                    {"text": "Explain the different levels of testing.", "category": "levels", "expected_keywords": ["unit", "integration", "system", "acceptance"], "time_limit": 120},
                    {"text": "What is the difference between functional and non-functional testing?", "category": "types", "expected_keywords": ["functional", "performance", "security"], "time_limit": 120},
                    {"text": "What is regression testing and when is it performed?", "category": "types", "expected_keywords": ["regression", "changes", "existing"], "time_limit": 120},
                    {"text": "Explain the concept of test-driven development (TDD).", "category": "methodology", "expected_keywords": ["test first", "red green refactor", "development"], "time_limit": 120},
                    {"text": "What is a test plan and what does it contain?", "category": "documentation", "expected_keywords": ["scope", "strategy", "schedule", "resources"], "time_limit": 90}
                ],
                "hard": [
                    {"text": "Explain the different types of test automation frameworks.", "category": "automation", "expected_keywords": ["framework", "modular", "data-driven", "keyword-driven"], "time_limit": 180},
                    {"text": "What is API testing and how do you perform it?", "category": "testing", "expected_keywords": ["api", "request", "response", "validation"], "time_limit": 180},
                    {"text": "Explain the concept of continuous integration and continuous deployment.", "category": "devops", "expected_keywords": ["ci", "cd", "automation", "pipeline"], "time_limit": 180},
                    {"text": "What is performance testing and what are its types?", "category": "performance", "expected_keywords": ["load", "stress", "volume", "scalability"], "time_limit": 150},
                    {"text": "Explain the bug life cycle in software testing.", "category": "process", "expected_keywords": ["new", "assigned", "fixed", "verified", "closed"], "time_limit": 150}
                ]
            },
            "mca_fresher": {
                "easy": [
                    {"text": "What is a programming language?", "category": "basics", "expected_keywords": ["instructions", "code", "syntax"], "time_limit": 60},
                    {"text": "Explain what is a variable in programming.", "category": "programming", "expected_keywords": ["storage", "value", "memory"], "time_limit": 45},
                    {"text": "What is an algorithm?", "category": "basics", "expected_keywords": ["steps", "problem", "solution"], "time_limit": 60},
                    {"text": "What is data structure?", "category": "data_structures", "expected_keywords": ["organization", "storage", "efficiency"], "time_limit": 60},
                    {"text": "Explain what is a function.", "category": "programming", "expected_keywords": ["block", "reusable", "call"], "time_limit": 45}
                ],
                "medium": [
                    {"text": "Explain the difference between array and linked list.", "category": "data_structures", "expected_keywords": ["array", "linked list", "pointer", "contiguous"], "time_limit": 120},
                    {"text": "What is time complexity and space complexity?", "category": "algorithms", "expected_keywords": ["time", "space", "big O", "efficiency"], "time_limit": 120},
                    {"text": "Explain the concept of sorting algorithms.", "category": "algorithms", "expected_keywords": ["sort", "order", "bubble", "quick"], "time_limit": 120},
                    {"text": "What is DBMS?", "category": "database", "expected_keywords": ["database", "management", "storage"], "time_limit": 90},
                    {"text": "Explain the difference between SQL and NoSQL databases.", "category": "database", "expected_keywords": ["sql", "nosql", "relational", "non-relational"], "time_limit": 120}
                ],
                "hard": [
                    {"text": "Explain the working of binary search algorithm.", "category": "algorithms", "expected_keywords": ["binary", "search", "divide", "conquer"], "time_limit": 180},
                    {"text": "What is recursion? Explain with an example.", "category": "programming", "expected_keywords": ["recursion", "base case", "stack"], "time_limit": 150},
                    {"text": "Explain the concept of stack and queue with real-life examples.", "category": "data_structures", "expected_keywords": ["stack", "queue", "lifo", "fifo"], "time_limit": 150},
                    {"text": "What is normalization in databases? Explain 1NF, 2NF, 3NF.", "category": "database", "expected_keywords": ["normalization", "1nf", "2nf", "3nf", "tables"], "time_limit": 180},
                    {"text": "Explain the concept of object-oriented programming principles.", "category": "oop", "expected_keywords": ["encapsulation", "inheritance", "polymorphism", "abstraction"], "time_limit": 180}
                ]
            }
        }
    
    def generate_question(self, job_role: str, difficulty: str, 
                         resume_data: Optional[Dict] = None,
                         previous_questions: List[Dict] = None) -> Dict:
        """Generate a question based on job role, difficulty, and resume"""
        
        # Get questions for the role and difficulty
        role_questions = self.dataset.get(job_role, {}).get(difficulty, [])
        
        if not role_questions:
            # Fallback to default
            role_questions = self.dataset.get("software_developer", {}).get("easy", [])
        
        # Filter out previously asked questions
        if previous_questions:
            previous_texts = [q.get("question", q.get("text", "")) for q in previous_questions]
            role_questions = [q for q in role_questions 
                            if q.get("text", q.get("question", "")) not in previous_texts]
        
        # If resume data is available, prioritize resume-based questions
        if resume_data and resume_data.get("skills"):
            resume_based = self._generate_resume_based_question(
                job_role, difficulty, resume_data
            )
            if resume_based and random.random() > 0.3:  # 70% chance of resume-based question
                self.generated_questions.append(resume_based)
                return resume_based
        
        # Select a random question
        if role_questions:
            question = random.choice(role_questions)
            self.generated_questions.append(question)
            return question
        
        # Fallback
        return {
            "text": "Tell me about yourself.",
            "category": "general",
            "expected_keywords": ["background", "skills", "experience"],
            "time_limit": 120
        }
    
    def _generate_resume_based_question(self, job_role: str, difficulty: str,
                                       resume_data: Dict) -> Optional[Dict]:
        """Generate questions based on resume skills"""
        
        skills = resume_data.get("skills", [])
        technologies = resume_data.get("technologies", [])
        
        if not skills and not technologies:
            return None
        
        # Resume-based question templates
        resume_questions = {
            "python": [
                "Explain Python list comprehension with an example.",
                "What are Python decorators and how do they work?",
                "Explain the difference between Python lists and tuples.",
                "What is Python's GIL (Global Interpreter Lock)?",
                "How does Python handle memory management?"
            ],
            "java": [
                "Explain the difference between abstract class and interface in Java.",
                "What is the difference between == and .equals() in Java?",
                "Explain the Java Collections framework.",
                "What is polymorphism in Java?",
                "Explain the concept of multithreading in Java."
            ],
            "javascript": [
                "Explain the difference between let, const, and var in JavaScript.",
                "What is closure in JavaScript?",
                "Explain the event loop in JavaScript.",
                "What is the difference between synchronous and asynchronous code?",
                "How does prototype inheritance work in JavaScript?"
            ],
            "machine learning": [
                "What is overfitting and how can you prevent it?",
                "Explain the difference between supervised and unsupervised learning.",
                "What is gradient descent?",
                "Explain the bias-variance tradeoff.",
                "What are the different evaluation metrics for classification?"
            ],
            "data analysis": [
                "How do you handle missing values in a dataset?",
                "Explain the concept of data normalization.",
                "What is the difference between correlation and causation?",
                "How would you detect outliers in a dataset?",
                "Explain the steps in data preprocessing."
            ],
            "sql": [
                "Explain the difference between INNER JOIN and LEFT JOIN.",
                "What is a subquery and how is it used?",
                "Explain the concept of database normalization.",
                "What is the difference between WHERE and HAVING clause?",
                "How would you optimize a slow SQL query?"
            ],
            "react": [
                "Explain the component lifecycle in React.",
                "What is the difference between state and props in React?",
                "What are React hooks and how do they work?",
                "Explain the concept of virtual DOM in React.",
                "How do you handle form validation in React?"
            ],
            "docker": [
                "What is Docker and how does it work?",
                "Explain the difference between Docker image and container.",
                "What is a Dockerfile?",
                "How do you manage data in Docker?",
                "Explain Docker networking."
            ]
        }
        
        # Find matching questions based on skills/technologies
        for skill in skills + technologies:
            skill_lower = skill.lower()
            for key, questions in resume_questions.items():
                if key in skill_lower:
                    return {
                        "text": random.choice(questions),
                        "category": "resume_based",
                        "expected_keywords": self._get_keywords_for_skill(key),
                        "time_limit": 120 if difficulty == "easy" else 180,
                        "skill_based_on": skill
                    }
        
        return None
    
    def _get_keywords_for_skill(self, skill: str) -> List[str]:
        """Get expected keywords for a skill"""
        keywords_map = {
            "python": ["list comprehension", "decorator", "tuple", "GIL", "memory"],
            "java": ["abstract", "interface", "equals", "collections", "thread"],
            "javascript": ["let", "const", "var", "closure", "event loop", "async"],
            "machine learning": ["overfitting", "supervised", "unsupervised", "gradient descent", "bias"],
            "data analysis": ["missing values", "normalization", "correlation", "outliers", "preprocessing"],
            "sql": ["join", "subquery", "normalization", "where", "having", "query optimization"],
            "react": ["lifecycle", "state", "props", "hooks", "virtual dom"],
            "docker": ["container", "image", "dockerfile", "volume", "network"]
        }
        return keywords_map.get(skill, [])
    
    def generate_follow_up(self, original_question: str, original_answer: str,
                          analysis: Dict, job_role: str) -> Dict:
        """Generate a follow-up question based on the user's answer"""
        
        # Analyze the original answer
        technical_terms = analysis.get("technical_terms", [])
        word_count = analysis.get("word_count", 0)
        
        # Follow-up question templates based on common patterns
        follow_ups = []
        
        if word_count < 30:
            follow_ups.append("Can you elaborate more on that?")
            follow_ups.append("Could you provide more details about that?")
        
        if "python" in original_answer.lower() or "python" in technical_terms:
            follow_ups.append("What libraries or frameworks have you used in Python?")
            follow_ups.append("Can you give an example of a Python project you've worked on?")
        
        if "java" in original_answer.lower() or "java" in technical_terms:
            follow_ups.append("What Java frameworks are you familiar with?")
            follow_ups.append("Explain a Java application you've developed.")
        
        if "machine learning" in original_answer.lower() or "ml" in original_answer.lower():
            follow_ups.append("What machine learning algorithms have you worked with?")
            follow_ups.append("How do you evaluate the performance of your models?")
        
        if "database" in original_answer.lower() or "sql" in original_answer.lower():
            follow_ups.append("What types of queries have you written?")
            follow_ups.append("How do you optimize database performance?")
        
        if "project" in original_answer.lower():
            follow_ups.append("What was your role in that project?")
            follow_ups.append("What challenges did you face during the project?")
        
        # Default follow-ups
        if not follow_ups:
            follow_ups = [
                "Can you explain that in more detail?",
                "What specific example can you give?",
                "How did you apply this in practice?"
            ]
        
        selected_follow_up = random.choice(follow_ups)
        
        return {
            "text": selected_follow_up,
            "reason": "Based on your previous answer, I'd like to explore this topic further.",
            "category": "follow-up"
        }
    
    def get_question_count(self, job_role: str, difficulty: str) -> int:
        """Get the number of available questions for a role and difficulty"""
        return len(self.dataset.get(job_role, {}).get(difficulty, []))


# Standalone function for testing
def generate_test_question(role: str = "software_developer", difficulty: str = "easy") -> Dict:
    """Quick function to generate a test question"""
    generator = QuestionGenerator()
    return generator.generate_question(role, difficulty)


if __name__ == "__main__":
    # Test the question generator
    generator = QuestionGenerator()
    q = generator.generate_question("software_developer", "medium")
    print("Generated Question:", q)
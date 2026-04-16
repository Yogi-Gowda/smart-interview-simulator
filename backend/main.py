# Smart Interview Simulator - Backend
# FastAPI Application

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
import random
from pathlib import Path

# Import custom modules
from resume_parser import ResumeParser
from nlp_analyzer import NLPAnalyzer
from question_generator import QuestionGenerator
from feedback_engine import FeedbackEngine
from database import DatabaseManager

# Initialize FastAPI
app = FastAPI(
    title="Smart Interview Simulator API",
    description="AI-powered interview practice system with NLP analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = DatabaseManager()
resume_parser = ResumeParser()
nlp_analyzer = NLPAnalyzer()
question_generator = QuestionGenerator()
feedback_engine = FeedbackEngine()

# Data models
class InterviewSession(BaseModel):
    user_id: str
    job_role: str
    difficulty: str

class AnswerSubmission(BaseModel):
    session_id: str
    question_id: str
    answer_text: str
    answer_type: str  # "text" or "voice"

class FollowUpRequest(BaseModel):
    session_id: str
    original_question: str
    original_answer: str

# Store active sessions
sessions = {}

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "message": "Smart Interview Simulator API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ==================== INTERVIEW SETUP ====================

@app.post("/api/interview/start")
async def start_interview(session: InterviewSession):
    """Start a new interview session"""
    session_id = f"session_{datetime.now().timestamp()}"
    
    sessions[session_id] = {
        "session_id": session_id,
        "user_id": session.user_id,
        "job_role": session.job_role,
        "difficulty": session.difficulty,
        "start_time": datetime.now().isoformat(),
        "questions": [],
        "answers": [],
        "resume_data": None,
        "current_question_index": 0,
        "scores": []
    }
    
    return {
        "session_id": session_id,
        "message": "Interview session started",
        "job_role": session.job_role,
        "difficulty": session.difficulty
    }

@app.post("/api/resume/upload")
async def upload_resume(session_id: str, file: UploadFile = File(...)):
    """Upload and parse resume"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Save uploaded file
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / f"{session_id}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Parse resume
    try:
        resume_data = resume_parser.parse_resume(str(file_path), file.filename)
        sessions[session_id]["resume_data"] = resume_data
        
        # Save to database
        db.save_resume(session_id, resume_data)
        
        return {
            "success": True,
            "resume_data": resume_data,
            "message": "Resume parsed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")

# ==================== QUESTION GENERATION ====================

@app.get("/api/question/{session_id}")
async def get_next_question(session_id: str):
    """Get next interview question"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Generate question based on resume data if available
    question = question_generator.generate_question(
        job_role=session["job_role"],
        difficulty=session["difficulty"],
        resume_data=session.get("resume_data"),
        previous_questions=session["questions"]
    )
    
    question_id = f"q_{len(session['questions']) + 1}"
    question_data = {
        "question_id": question_id,
        "question": question["text"],
        "category": question["category"],
        "skills": question.get("skills", []),
        "expected_keywords": question.get("expected_keywords", []),
        "time_limit": question.get("time_limit", 120)
    }
    
    session["questions"].append(question_data)
    session["current_question_index"] += 1
    
    return question_data

@app.post("/api/question/follow-up")
async def get_follow_up_question(request: FollowUpRequest):
    """Generate follow-up question based on user's answer"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    
    # Analyze the original answer
    analysis = nlp_analyzer.analyze_answer(request.original_answer)
    
    # Generate follow-up based on analysis
    follow_up = question_generator.generate_follow_up(
        original_question=request.original_question,
        original_answer=request.original_answer,
        analysis=analysis,
        job_role=session["job_role"]
    )
    
    return {
        "follow_up_question": follow_up["text"],
        "reason": follow_up.get("reason", ""),
        "category": follow_up.get("category", "follow-up")
    }

# ==================== ANSWER ANALYSIS ====================

@app.post("/api/answer/submit")
async def submit_answer(submission: AnswerSubmission):
    """Submit and analyze user's answer"""
    if submission.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[submission.session_id]
    
    # Find the current question
    current_q = session["questions"][-1] if session["questions"] else None
    if not current_q:
        raise HTTPException(status_code=400, detail="No active question")
    
    # Analyze the answer
    analysis = nlp_analyzer.analyze_answer(submission.answer_text)
    
    # Calculate scores
    scores = feedback_engine.calculate_scores(
        answer=submission.answer_text,
        analysis=analysis,
        expected_keywords=current_q.get("expected_keywords", []),
        question_category=current_q.get("category", "")
    )
    
    # Generate feedback
    feedback = feedback_engine.generate_feedback(
        answer=submission.answer_text,
        analysis=analysis,
        scores=scores,
        question=current_q["question"]
    )
    
    # Store answer
    answer_data = {
        "question_id": submission.question_id,
        "question": current_q["question"],
        "answer": submission.answer_text,
        "answer_type": submission.answer_type,
        "analysis": analysis,
        "scores": scores,
        "feedback": feedback,
        "timestamp": datetime.now().isoformat()
    }
    
    session["answers"].append(answer_data)
    session["scores"].append(scores)
    
    # Save to database
    db.save_interview_history(
        session_id=submission.session_id,
        user_id=session["user_id"],
        answer_data=answer_data
    )
    
    return {
        "success": True,
        "analysis": analysis,
        "scores": scores,
        "feedback": feedback,
        "suggestions": feedback.get("improvements", [])
    }

# ==================== SESSION MANAGEMENT ====================

@app.get("/api/session/{session_id}")
async def get_session_status(session_id: str):
    """Get current session status"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "job_role": session["job_role"],
        "difficulty": session["difficulty"],
        "questions_answered": len(session["answers"]),
        "current_question_index": session["current_question_index"],
        "average_score": sum(s["total_score"] for s in session["scores"]) / len(session["scores"]) if session["scores"] else 0
    }

@app.post("/api/interview/end")
async def end_interview(session_id: str):
    """End interview session and generate final report"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Calculate final statistics
    total_questions = len(session["answers"])
    if total_questions == 0:
        raise HTTPException(status_code=400, detail="No answers recorded")
    
    avg_score = sum(s["total_score"] for s in session["scores"]) / total_questions
    
    # Identify weak areas
    weak_areas = feedback_engine.identify_weak_areas(session["answers"])
    
    # Generate final report
    report = {
        "session_id": session_id,
        "job_role": session["job_role"],
        "difficulty": session["difficulty"],
        "total_questions": total_questions,
        "average_score": round(avg_score, 2),
        "scores_breakdown": {
            "content": round(sum(s["content_score"] for s in session["scores"]) / total_questions, 2),
            "grammar": round(sum(s["grammar_score"] for s in session["scores"]) / total_questions, 2),
            "technical": round(sum(s["technical_score"] for s in session["scores"]) / total_questions, 2),
            "confidence": round(sum(s["confidence_score"] for s in session["scores"]) / total_questions, 2)
        },
        "weak_areas": weak_areas,
        "strengths": feedback_engine.identify_strengths(session["answers"]),
        "overall_feedback": feedback_engine.generate_final_feedback(avg_score, weak_areas),
        "improvement_suggestions": feedback_engine.generate_improvement_plan(weak_areas),
        "completed_at": datetime.now().isoformat()
    }
    
    # Save final report
    db.save_final_report(session_id, report)
    
    # Clean up session
    del sessions[session_id]
    
    return report

# ==================== HISTORY & DASHBOARD ====================

@app.get("/api/history/{user_id}")
async def get_interview_history(user_id: str):
    """Get user's interview history"""
    history = db.get_user_history(user_id)
    return {
        "history": history,
        "total_interviews": len(history)
    }

@app.get("/api/dashboard/{user_id}")
async def get_user_dashboard(user_id: str):
    """Get user performance dashboard"""
    dashboard = db.get_dashboard_data(user_id)
    return dashboard

@app.get("/api/analytics/{session_id}")
async def get_session_analytics(session_id: str):
    """Get detailed analytics for a session"""
    if session_id not in sessions:
        # Try to get from database
        analytics = db.get_session_analytics(session_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Session not found")
        return analytics
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "answers": session["answers"],
        "scores": session["scores"],
        "question_categories": [a["analysis"]["category"] for a in session["answers"]],
        "performance_trend": [s["total_score"] for s in session["scores"]]
    }

# ==================== JOB ROLES & QUESTIONS ====================

@app.get("/api/roles")
async def get_job_roles():
    """Get available job roles"""
    return {
        "roles": [
            {"id": "software_developer", "name": "Software Developer"},
            {"id": "data_analyst", "name": "Data Analyst"},
            {"id": "software_testing", "name": "Software Testing"},
            {"id": "mca_fresher", "name": "MCA Fresher"}
        ],
        "difficulties": ["easy", "medium", "hard"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
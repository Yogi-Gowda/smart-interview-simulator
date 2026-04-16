# Database Manager Module
# Handles MongoDB database operations

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

try:
    from pymongo import MongoClient
    from bson import ObjectId
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


class DatabaseManager:
    """Manage database operations for the interview simulator"""
    
    def __init__(self, connection_string: str = None, database_name: str = "interview_simulator"):
        """Initialize database connection"""
        self.database_name = database_name
        self.client = None
        self.db = None
        
        if PYMONGO_AVAILABLE:
            try:
                if connection_string:
                    self.client = MongoClient(connection_string)
                else:
                    self.client = MongoClient("mongodb://localhost:27017/")
                self.db = self.client[database_name]
                self._ensure_indexes()
            except Exception as e:
                print(f"MongoDB connection failed: {e}. Using file-based storage.")
                self.client = None
                self.db = None
        else:
            print("PyMongo not available. Using file-based storage.")
        
        # Fallback to file-based storage
        self.data_dir = Path(__file__).parent.parent / "database"
        self.data_dir.mkdir(exist_ok=True)
    
    def _ensure_indexes(self):
        """Create database indexes"""
        if self.db:
            try:
                self.db.users.create_index("user_id", unique=True)
                self.db.interviews.create_index("session_id", unique=True)
                self.db.interviews.create_index("user_id")
                self.db.resumes.create_index("session_id")
            except Exception as e:
                print(f"Index creation warning: {e}")
    
    # ==================== USER OPERATIONS ====================
    
    def save_user(self, user_data: Dict) -> str:
        """Save or update user data"""
        user_id = user_data.get("user_id")
        
        if self.db:
            self.db.users.update_one(
                {"user_id": user_id},
                {"$set": {**user_data, "updated_at": datetime.now().isoformat()}},
                upsert=True
            )
            return user_id
        else:
            # File-based fallback
            return self._save_to_file("users", user_id, user_data)
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        if self.db:
            return self.db.users.find_one({"user_id": user_id})
        else:
            return self._read_from_file("users", user_id)
    
    # ==================== RESUME OPERATIONS ====================
    
    def save_resume(self, session_id: str, resume_data: Dict) -> str:
        """Save parsed resume data"""
        if self.db:
            self.db.resumes.update_one(
                {"session_id": session_id},
                {"$set": {**resume_data, "saved_at": datetime.now().isoformat()}},
                upsert=True
            )
            return session_id
        else:
            return self._save_to_file("resumes", session_id, resume_data)
    
    def get_resume(self, session_id: str) -> Optional[Dict]:
        """Get resume by session ID"""
        if self.db:
            return self.db.resumes.find_one({"session_id": session_id})
        else:
            return self._read_from_file("resumes", session_id)
    
    # ==================== INTERVIEW HISTORY ====================
    
    def save_interview_history(self, session_id: str, user_id: str, answer_data: Dict):
        """Save individual answer to interview history"""
        if self.db:
            self.db.interviews.update_one(
                {"session_id": session_id},
                {
                    "$push": {"answers": answer_data},
                    "$set": {"user_id": user_id, "last_updated": datetime.now().isoformat()}
                },
                upsert=True
            )
        else:
            self._append_to_file("interviews", session_id, answer_data, user_id)
    
    def save_final_report(self, session_id: str, report: Dict):
        """Save final interview report"""
        if self.db:
            self.db.interviews.update_one(
                {"session_id": session_id},
                {"$set": {**report, "completed": True}},
                upsert=True
            )
        else:
            self._save_to_file("reports", session_id, report)
    
    def get_user_history(self, user_id: str) -> List[Dict]:
        """Get all interview history for a user"""
        if self.db:
            cursor = self.db.interviews.find(
                {"user_id": user_id}
            ).sort("last_updated", -1)
            return list(cursor)
        else:
            return self._read_all_from_file("interviews", user_id)
    
    def get_session_analytics(self, session_id: str) -> Optional[Dict]:
        """Get analytics for a specific session"""
        if self.db:
            return self.db.interviews.find_one({"session_id": session_id})
        else:
            return self._read_from_file("reports", session_id)
    
    # ==================== DASHBOARD DATA ====================
    
    def get_dashboard_data(self, user_id: str) -> Dict:
        """Get dashboard data for user"""
        history = self.get_user_history(user_id)
        
        if not history:
            return {
                "total_interviews": 0,
                "average_score": 0,
                "total_questions": 0,
                "weak_areas": [],
                "strengths": [],
                "recent_interviews": [],
                "performance_trend": []
            }
        
        # Calculate statistics
        total_interviews = len(history)
        total_questions = sum(len(i.get("answers", [])) for i in history)
        
        all_scores = []
        category_scores = {}
        
        for interview in history:
            if "scores_breakdown" in interview:
                all_scores.append(interview.get("average_score", 0))
            
            for answer in interview.get("answers", []):
                if "scores" in answer:
                    all_scores.append(answer["scores"].get("total_score", 0))
                
                category = answer.get("analysis", {}).get("category", "unknown")
                if category not in category_scores:
                    category_scores[category] = []
                if "scores" in answer:
                    category_scores[category].append(
                        answer["scores"].get("technical_score", 0)
                    )
        
        average_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # Identify weak areas
        weak_areas = []
        for category, scores in category_scores.items():
            avg = sum(scores) / len(scores)
            if avg < 60:
                weak_areas.append({"category": category, "score": round(avg, 2)})
        
        # Identify strengths
        strengths = []
        for category, scores in category_scores.items():
            avg = sum(scores) / len(scores)
            if avg >= 70:
                strengths.append({"category": category, "score": round(avg, 2)})
        
        # Recent interviews
        recent = []
        for i in history[:5]:
            recent.append({
                "session_id": i.get("session_id"),
                "job_role": i.get("job_role"),
                "average_score": i.get("average_score", 0),
                "date": i.get("last_updated", i.get("completed_at", ""))
            })
        
        # Performance trend
        performance_trend = []
        for i in history:
            performance_trend.append({
                "date": i.get("last_updated", i.get("completed_at", "")),
                "score": i.get("average_score", 0)
            })
        
        return {
            "total_interviews": total_interviews,
            "average_score": round(average_score, 2),
            "total_questions": total_questions,
            "weak_areas": weak_areas,
            "strengths": strengths,
            "recent_interviews": recent,
            "performance_trend": performance_trend
        }
    
    # ==================== FILE-BASED FALLBACK ====================
    
    def _save_to_file(self, collection: str, id: str, data: Dict) -> str:
        """Save data to JSON file"""
        file_path = self.data_dir / f"{collection}.json"
        
        # Load existing data
        try:
            with open(file_path, 'r') as f:
                all_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_data = {}
        
        # Update data
        all_data[id] = data
        
        # Save back
        with open(file_path, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        return id
    
    def _read_from_file(self, collection: str, id: str) -> Optional[Dict]:
        """Read data from JSON file"""
        file_path = self.data_dir / f"{collection}.json"
        
        try:
            with open(file_path, 'r') as f:
                all_data = json.load(f)
            return all_data.get(id)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _append_to_file(self, collection: str, session_id: str, answer: Dict, user_id: str):
        """Append answer to interview record"""
        file_path = self.data_dir / f"{collection}.json"
        
        try:
            with open(file_path, 'r') as f:
                all_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_data = {}
        
        if session_id not in all_data:
            all_data[session_id] = {"session_id": session_id, "user_id": user_id, "answers": []}
        
        all_data[session_id]["answers"].append(answer)
        all_data[session_id]["last_updated"] = datetime.now().isoformat()
        
        with open(file_path, 'w') as f:
            json.dump(all_data, f, indent=2)
    
    def _read_all_from_file(self, collection: str, user_id: str) -> List[Dict]:
        """Read all records for a user"""
        file_path = self.data_dir / f"{collection}.json"
        
        try:
            with open(file_path, 'r') as f:
                all_data = json.load(f)
            return [v for v in all_data.values() if v.get("user_id") == user_id]
        except (FileNotFoundError, json.JSONDecodeError):
            return []


# Standalone function for testing
def test_database():
    """Test database operations"""
    db = DatabaseManager()
    print("Database Manager initialized")
    print("Data directory:", db.data_dir)


if __name__ == "__main__":
    test_database()
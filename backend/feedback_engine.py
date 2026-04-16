# Feedback Engine Module
# Generates feedback and scores for user answers

import random
from typing import Dict, List, Optional
from collections import Counter


class FeedbackEngine:
    """Generate feedback and calculate scores for answers"""
    
    def __init__(self):
        self.feedback_history = []
    
    def calculate_scores(self, answer: str, analysis: Dict,
                        expected_keywords: List[str], 
                        question_category: str) -> Dict:
        """Calculate various scores for the answer"""
        
        # Content Score (based on length and completeness)
        content_score = self._calculate_content_score(answer, analysis)
        
        # Grammar Score
        grammar_score = analysis.get("grammar_quality", 70)
        
        # Technical Score (based on keyword matching)
        technical_score = self._calculate_technical_score(
            answer, expected_keywords, question_category
        )
        
        # Confidence Score (based on answer structure)
        confidence_score = self._calculate_confidence_score(answer, analysis)
        
        # Calculate total score (weighted average)
        total_score = round(
            (content_score * 0.25) +
            (grammar_score * 0.15) +
            (technical_score * 0.40) +
            (confidence_score * 0.20)
        )
        
        scores = {
            "content_score": content_score,
            "grammar_score": grammar_score,
            "technical_score": technical_score,
            "confidence_score": confidence_score,
            "total_score": total_score,
            "grade": self._get_grade(total_score)
        }
        
        self.feedback_history.append(scores)
        return scores
    
    def _calculate_content_score(self, answer: str, analysis: Dict) -> int:
        """Calculate content score based on answer quality"""
        score = 50  # Base score
        
        word_count = analysis.get("word_count", 0)
        sentence_count = analysis.get("sentence_count", 0)
        completeness = analysis.get("completeness", 0)
        
        # Word count scoring
        if word_count >= 50:
            score += 20
        elif word_count >= 30:
            score += 10
        elif word_count >= 15:
            score += 5
        
        # Sentence structure scoring
        if sentence_count >= 3:
            score += 10
        if sentence_count >= 5:
            score += 5
        
        # Completeness scoring
        score += int(completeness * 0.2)
        
        return min(100, score)
    
    def _calculate_technical_score(self, answer: str, expected_keywords: List[str],
                                   category: str) -> int:
        """Calculate technical accuracy score"""
        if not expected_keywords:
            return 70  # Default score if no keywords specified
        
        answer_lower = answer.lower()
        found_count = 0
        
        for keyword in expected_keywords:
            if keyword.lower() in answer_lower:
                found_count += 1
        
        # Calculate percentage
        match_percentage = (found_count / len(expected_keywords)) * 100
        
        # Base score + match percentage
        score = 30 + int(match_percentage * 0.6)
        
        return min(100, score)
    
    def _calculate_confidence_score(self, answer: str, analysis: Dict) -> int:
        """Calculate confidence score based on answer structure"""
        score = 60  # Base score
        
        # Check for hedging words (reduces confidence)
        hedging_words = ["maybe", "perhaps", "I think", "I guess", "not sure", "possibly"]
        answer_lower = answer.lower()
        
        hedging_count = sum(1 for word in hedging_words if word in answer_lower)
        score -= hedging_count * 5
        
        # Check for definitive language (increases confidence)
        definitive_words = ["definitely", "certainly", "absolutely", "clearly", "specifically"]
        definitive_count = sum(1 for word in definitive_words if word in answer_lower)
        score += definitive_count * 5
        
        # Check for examples (increases confidence)
        if "for example" in answer_lower or "for instance" in answer_lower:
            score += 10
        
        # Check for structured answers
        if analysis.get("sentence_count", 0) >= 3:
            score += 10
        
        return max(0, min(100, score))
    
    def _get_grade(self, score: int) -> str:
        """Convert score to grade"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C"
        elif score >= 40:
            return "D"
        else:
            return "F"
    
    def generate_feedback(self, answer: str, analysis: Dict,
                         scores: Dict, question: str) -> Dict:
        """Generate detailed feedback for the answer"""
        
        feedback = {
            "overall": "",
            "strengths": [],
            "weaknesses": [],
            "improvements": [],
            "technical_accuracy": "",
            "grammar_suggestions": "",
            "next_steps": ""
        }
        
        # Overall feedback
        total_score = scores.get("total_score", 0)
        if total_score >= 80:
            feedback["overall"] = "Excellent answer! You demonstrated strong understanding of the topic."
        elif total_score >= 60:
            feedback["overall"] = "Good answer! You have a decent understanding but there's room for improvement."
        elif total_score >= 40:
            feedback["overall"] = "Average answer. Consider expanding your knowledge on this topic."
        else:
            feedback["overall"] = "Your answer needs improvement. Review the fundamentals of this topic."
        
        # Strengths
        if scores.get("content_score", 0) >= 70:
            feedback["strengths"].append("Good content coverage with adequate length")
        if scores.get("grammar_score", 0) >= 80:
            feedback["strengths"].append("Excellent grammar and sentence structure")
        if scores.get("technical_score", 0) >= 70:
            feedback["strengths"].append("Good use of technical terminology")
        if scores.get("confidence_score", 0) >= 70:
            feedback["strengths"].append("Confident and clear communication")
        
        # Weaknesses
        if scores.get("content_score", 0) < 50:
            feedback["weaknesses"].append("Answer is too short. Aim for more detailed explanations.")
        if scores.get("grammar_score", 0) < 60:
            feedback["weaknesses"].append("Grammar needs improvement. Proofread your answers.")
        if scores.get("technical_score", 0) < 50:
            feedback["weaknesses"].append("Missing key technical concepts. Review the fundamentals.")
        if scores.get("confidence_score", 0) < 50:
            feedback["weaknesses"].append("Answer lacks confidence. Be more definitive in your responses.")
        
        # Improvements
        if not feedback["strengths"]:
            feedback["improvements"].append("Try to provide more detailed explanations")
        if scores.get("technical_score", 0) < 70:
            feedback["improvements"].append("Study the key concepts related to this topic")
        if analysis.get("sentence_count", 0) < 3:
            feedback["improvements"].append("Structure your answer with multiple sentences")
        
        # Technical accuracy feedback
        tech_score = scores.get("technical_score", 0)
        if tech_score >= 80:
            feedback["technical_accuracy"] = "Excellent technical understanding. You covered the key concepts well."
        elif tech_score >= 60:
            feedback["technical_accuracy"] = "Good technical knowledge but missing some important points."
        else:
            feedback["technical_accuracy"] = "Technical accuracy needs improvement. Review the core concepts."
        
        # Grammar suggestions
        grammar_score = scores.get("grammar_score", 0)
        if grammar_score < 70:
            feedback["grammar_suggestions"] = "Work on grammar: check sentence structure, punctuation, and word usage."
        else:
            feedback["grammar_suggestions"] = "Grammar is good. Keep maintaining clear language."
        
        # Next steps
        if total_score >= 70:
            feedback["next_steps"] = "Move on to the next question. You're doing well!"
        else:
            feedback["next_steps"] = "Review the feedback and try to improve in the next answer."
        
        return feedback
    
    def identify_weak_areas(self, answers: List[Dict]) -> List[Dict]:
        """Identify weak areas based on answer history"""
        
        category_scores = {}
        
        for answer in answers:
            category = answer.get("analysis", {}).get("category", "unknown")
            score = answer.get("scores", {}).get("technical_score", 0)
            
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(score)
        
        weak_areas = []
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 60:
                weak_areas.append({
                    "category": category,
                    "average_score": round(avg_score, 2),
                    "question_count": len(scores),
                    "recommendation": self._get_weakness_recommendation(category)
                })
        
        return sorted(weak_areas, key=lambda x: x["average_score"])
    
    def _get_weakness_recommendation(self, category: str) -> str:
        """Get recommendation for weak category"""
        recommendations = {
            "programming": "Practice coding fundamentals and data structures",
            "web": "Study web development concepts and frameworks",
            "database": "Learn SQL and database design principles",
            "oop": "Review object-oriented programming principles",
            "data_science": "Study machine learning fundamentals and statistics",
            "software_testing": "Learn testing methodologies and tools",
            "general": "Practice more interview questions"
        }
        return recommendations.get(category, "Review this topic in depth")
    
    def identify_strengths(self, answers: List[Dict]) -> List[Dict]:
        """Identify strong areas based on answer history"""
        
        category_scores = {}
        
        for answer in answers:
            category = answer.get("analysis", {}).get("category", "unknown")
            score = answer.get("scores", {}).get("technical_score", 0)
            
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(score)
        
        strengths = []
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score >= 70:
                strengths.append({
                    "category": category,
                    "average_score": round(avg_score, 2),
                    "question_count": len(scores)
                })
        
        return sorted(strengths, key=lambda x: x["average_score"], reverse=True)
    
    def generate_final_feedback(self, average_score: float, weak_areas: List[Dict]) -> str:
        """Generate final overall feedback"""
        
        if average_score >= 80:
            return (
                "Outstanding performance! You demonstrated strong technical knowledge "
                "and communication skills. Keep up the good work and continue "
                "building on your strengths."
            )
        elif average_score >= 70:
            return (
                "Good job! You have a solid understanding of the topics covered. "
                "Focus on improving your weak areas to achieve even better results."
            )
        elif average_score >= 60:
            return (
                "Decent performance. You have basic understanding but need to "
                "strengthen your technical knowledge. Review the weak areas identified."
            )
        else:
            return (
                "Keep practicing! This is a learning process. Focus on the fundamentals "
                "and gradually build your knowledge. Don't get discouraged - "
                "consistent practice will lead to improvement."
            )
    
    def generate_improvement_plan(self, weak_areas: List[Dict]) -> List[Dict]:
        """Generate a personalized improvement plan"""
        
        plan = []
        
        for area in weak_areas:
            category = area.get("category", "general")
            plan.append({
                "area": category,
                "action": self._get_improvement_action(category),
                "resources": self._get_learning_resources(category),
                "priority": "high" if area.get("average_score", 100) < 50 else "medium"
            })
        
        return plan
    
    def _get_improvement_action(self, category: str) -> str:
        """Get specific action for improvement"""
        actions = {
            "programming": "Practice coding problems daily, focus on data structures and algorithms",
            "web": "Build small web projects to understand HTTP, APIs, and frameworks",
            "database": "Practice SQL queries and learn database design patterns",
            "oop": "Study design patterns and practice object-oriented design",
            "data_science": "Complete ML courses and work on real datasets",
            "software_testing": "Learn testing frameworks and write test cases",
            "general": "Practice more interview questions and review fundamentals"
        }
        return actions.get(category, "Review and practice this topic")
    
    def _get_learning_resources(self, category: str) -> List[str]:
        """Get recommended learning resources"""
        resources = {
            "programming": ["LeetCode", "HackerRank", "GeeksforGeeks"],
            "web": ["MDN Web Docs", "React Documentation", "REST API Tutorial"],
            "database": ["SQL Tutorial", "Database Normalization Guide"],
            "oop": ["OOP Design Patterns", "SOLID Principles"],
            "data_science": ["Kaggle", "Coursera ML", "Scikit-learn Documentation"],
            "software_testing": ["Selenium Documentation", "Testing Best Practices"],
            "general": ["Interview Prep Books", "Online Coding Practice"]
        }
        return resources.get(category, ["Online tutorials", "Practice exercises"])


# Standalone function for testing
def calculate_sample_scores() -> Dict:
    """Quick function to test score calculation"""
    engine = FeedbackEngine()
    answer = "Object-oriented programming is a programming paradigm that uses objects and classes. It includes inheritance, polymorphism, and encapsulation."
    analysis = {
        "word_count": 20,
        "sentence_count": 2,
        "grammar_quality": 85,
        "technical_terms": ["object", "class", "inheritance", "polymorphism", "encapsulation"]
    }
    expected_keywords = ["class", "object", "inheritance", "encapsulation", "polymorphism"]
    
    scores = engine.calculate_scores(answer, analysis, expected_keywords, "oop")
    return scores


if __name__ == "__main__":
    # Test the feedback engine
    scores = calculate_sample_scores()
    print("Sample Scores:", scores)
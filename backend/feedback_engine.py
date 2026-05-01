# Feedback Engine Module
# Generates feedback and scores for user answers

import random
from typing import Dict, List, Optional
from collections import Counter


class FeedbackEngine:
    """Generate feedback and calculate scores for answers"""

    # ── Score weights ────────────────────────────────────────
    # technical_score drives quality the most — it measures
    # whether the candidate actually knows the answer.
    WEIGHT_TECHNICAL  = 0.50
    WEIGHT_CONTENT    = 0.25
    WEIGHT_CONFIDENCE = 0.15
    WEIGHT_GRAMMAR    = 0.10

    def __init__(self):
        self.feedback_history = []

    # ─────────────────────────────────────────────────────────
    # MAIN SCORING ENTRY POINT
    # ─────────────────────────────────────────────────────────
    def calculate_scores(
        self,
        answer: str,
        analysis: Dict,
        expected_keywords: List[str],
        question_category: str,
    ) -> Dict:
        """Calculate all sub-scores and a weighted total score."""

        # ── Low-effort / "I don't know" short-circuit ────────
        if analysis.get("low_effort"):
            reason = analysis.get("low_effort_reason", "")
            content_score    = 5
            grammar_score    = analysis.get("grammar_quality", 50)
            technical_score  = 0
            confidence_score = 5

            total_score = round(
                (technical_score  * self.WEIGHT_TECHNICAL)  +
                (content_score    * self.WEIGHT_CONTENT)    +
                (confidence_score * self.WEIGHT_CONFIDENCE) +
                (grammar_score    * self.WEIGHT_GRAMMAR)
            )

            scores = {
                "content_score":    content_score,
                "grammar_score":    grammar_score,
                "technical_score":  technical_score,
                "confidence_score": confidence_score,
                "total_score":      total_score,
                "grade":            self._get_grade(total_score),
                "low_effort":       True,
                "low_effort_reason": reason,
                "found_keywords":   [],
                "missing_keywords": expected_keywords,
            }
            self.feedback_history.append(scores)
            return scores

        # ── Normal scoring ────────────────────────────────────
        kw_result        = self._keyword_analysis(answer, expected_keywords)
        technical_score  = self._calculate_technical_score(answer, analysis, kw_result)
        content_score    = self._calculate_content_score(answer, analysis, technical_score)
        grammar_score    = analysis.get("grammar_quality", 70)
        confidence_score = self._calculate_confidence_score(answer, analysis)

        total_score = round(
            (technical_score  * self.WEIGHT_TECHNICAL)  +
            (content_score    * self.WEIGHT_CONTENT)    +
            (confidence_score * self.WEIGHT_CONFIDENCE) +
            (grammar_score    * self.WEIGHT_GRAMMAR)
        )

        scores = {
            "content_score":    content_score,
            "grammar_score":    grammar_score,
            "technical_score":  technical_score,
            "confidence_score": confidence_score,
            "total_score":      total_score,
            "grade":            self._get_grade(total_score),
            "found_keywords":   kw_result["found"],
            "missing_keywords": kw_result["missing"],
        }
        self.feedback_history.append(scores)
        return scores

    # ─────────────────────────────────────────────────────────
    # KEYWORD ANALYSIS (shared between scoring & feedback)
    # ─────────────────────────────────────────────────────────
    def _keyword_analysis(self, answer: str, expected_keywords: List[str]) -> Dict:
        """
        Check expected keywords against the answer.
        Uses exact match + partial/root match for robustness.
        Returns {"found": [...], "missing": [...], "match_pct": float}
        """
        answer_lower = answer.lower()
        found   = []
        missing = []

        for kw in expected_keywords:
            kw_lower = kw.lower()
            if kw_lower in answer_lower:
                found.append(kw)
            else:
                # Partial root match — e.g. "encapsulation" in "encapsulate"
                root = kw_lower.split()[0]
                if len(root) > 4 and root in answer_lower:
                    found.append(kw)
                else:
                    missing.append(kw)

        match_pct = (len(found) / len(expected_keywords) * 100) if expected_keywords else 0
        return {"found": found, "missing": missing, "match_pct": match_pct}

    # ─────────────────────────────────────────────────────────
    # TECHNICAL SCORE  (0 – 100, no inflated base)
    # ─────────────────────────────────────────────────────────
    def _calculate_technical_score(
        self, answer: str, analysis: Dict, kw_result: Dict
    ) -> int:
        """
        Score purely on keyword coverage.
        No base score — an answer with 0 matching keywords scores ≤15.
        """
        match_pct = kw_result["match_pct"]
        quality   = analysis.get("quality_prediction", "average")

        if not kw_result["found"] and not kw_result["missing"]:
            # No expected keywords defined → use quality prediction
            base = {"good": 72, "average": 50, "poor": 20}.get(quality, 50)
            return base

        # Pure keyword-match driven (0 – 100)
        score = int(match_pct)

        # Soft quality adjustment (±10 max)
        if quality == "good"    and score >= 40:  score = min(100, score + 10)
        if quality == "average" and score >= 60:  score = min(100, score + 5)
        if quality == "poor":                      score = max(0,   score - 10)

        return min(100, max(0, score))

    # ─────────────────────────────────────────────────────────
    # CONTENT SCORE  (0 – 100)
    # ─────────────────────────────────────────────────────────
    def _calculate_content_score(
        self, answer: str, analysis: Dict, technical_score: int
    ) -> int:
        """
        Score based on depth, length, and ML quality prediction.
        Anchored to technical_score so a wrong answer can't score high here.
        """
        quality      = analysis.get("quality_prediction", "average")
        word_count   = analysis.get("word_count", 0)
        sent_count   = analysis.get("sentence_count", 0)

        # Quality-anchored base (poor answers can't score high content)
        quality_base = {"good": 60, "average": 40, "poor": 15}.get(quality, 40)
        score = quality_base

        # Word count bonus
        if quality != "poor":
            if word_count >= 80:  score += 25
            elif word_count >= 50: score += 18
            elif word_count >= 30: score += 10
            elif word_count >= 15: score += 5
        else:
            if word_count >= 40:  score += 5   # minimal bonus even for poor answers

        # Multi-sentence structure bonus
        if sent_count >= 5 and quality != "poor":  score += 10
        elif sent_count >= 3:                       score += 5

        # Cap content score relative to technical accuracy:
        # A completely wrong answer can't score well on content
        if technical_score < 20:
            score = min(score, 35)
        elif technical_score < 40:
            score = min(score, 55)

        return min(100, max(0, score))

    # ─────────────────────────────────────────────────────────
    # CONFIDENCE SCORE  (0 – 100)
    # ─────────────────────────────────────────────────────────
    def _calculate_confidence_score(self, answer: str, analysis: Dict) -> int:
        """
        Measure confident, structured delivery.
        Base is 40 (not 60) so wrong answers don't inflate the total.
        """
        score = 40   # realistic base

        answer_lower = answer.lower()

        # Penalise hedging / uncertainty words
        hedging = ["maybe", "perhaps", "i think", "i guess",
                   "not sure", "possibly", "i believe", "kind of"]
        hedging_count = sum(1 for w in hedging if w in answer_lower)
        score -= hedging_count * 5

        # Reward confident, definitive language
        definitive = ["definitely", "certainly", "absolutely",
                      "clearly", "specifically", "in summary", "in conclusion"]
        definitive_count = sum(1 for w in definitive if w in answer_lower)
        score += definitive_count * 5

        # Reward concrete examples
        if "for example" in answer_lower or "for instance" in answer_lower:
            score += 15

        # Reward structured multi-sentence answers
        if analysis.get("sentence_count", 0) >= 5:  score += 15
        elif analysis.get("sentence_count", 0) >= 3: score += 8

        return max(0, min(100, score))

    # ─────────────────────────────────────────────────────────
    # GRADE MAPPING
    # ─────────────────────────────────────────────────────────
    def _get_grade(self, score: int) -> str:
        if score >= 90:  return "A+"
        elif score >= 80: return "A"
        elif score >= 70: return "B+"
        elif score >= 60: return "B"
        elif score >= 50: return "C"
        elif score >= 40: return "D"
        else:             return "F"

    # ─────────────────────────────────────────────────────────
    # FEEDBACK GENERATION
    # ─────────────────────────────────────────────────────────
    def generate_feedback(
        self,
        answer: str,
        analysis: Dict,
        scores: Dict,
        question: str,
        expected_keywords: List[str] = None,
    ) -> Dict:
        """Generate detailed, specific feedback for the answer."""

        feedback = {
            "overall":          "",
            "strengths":        [],
            "weaknesses":       [],
            "improvements":     [],
            "technical_accuracy": "",
            "grammar_suggestions": "",
            "next_steps":       "",
            "missing_concepts": [],
            "found_concepts":   [],
        }

        total_score     = scores.get("total_score", 0)
        technical_score = scores.get("technical_score", 0)
        content_score   = scores.get("content_score", 0)
        grammar_score   = scores.get("grammar_score", 0)
        confidence_score = scores.get("confidence_score", 0)
        found_kws       = scores.get("found_keywords",   [])
        missing_kws     = scores.get("missing_keywords", [])
        quality         = analysis.get("quality_prediction", "average")

        feedback["found_concepts"]   = found_kws
        feedback["missing_concepts"] = missing_kws

        # ── Low-effort short-circuit ─────────────────────────
        if scores.get("low_effort"):
            feedback["overall"] = (
                "It looks like you didn't attempt the answer. "
                "Even a partial attempt or outlining your approach shows effort."
            )
            feedback["weaknesses"].append("No answer or 'I don't know' response detected.")
            feedback["improvements"].append(
                "Try to outline your approach even if unsure. "
                "Structure: define the concept → give an example → explain why it matters."
            )
            if expected_keywords:
                feedback["improvements"].append(
                    f"Key concepts to study for this question: "
                    f"{', '.join(expected_keywords[:6])}."
                )
            feedback["next_steps"] = "Review this topic and try to answer again."
            return feedback

        # ── Overall message ───────────────────────────────────
        if total_score >= 85:
            feedback["overall"] = (
                "Excellent answer! You demonstrated a strong understanding of the topic "
                "and covered the key concepts clearly."
            )
        elif total_score >= 70:
            feedback["overall"] = (
                "Good answer! You have a solid understanding but missed a few key points."
            )
        elif total_score >= 55:
            feedback["overall"] = (
                "Partial answer. You touched on some ideas but the core concepts "
                "were not fully covered."
            )
        elif total_score >= 35:
            feedback["overall"] = (
                "Your answer needs significant improvement. "
                "The key technical concepts for this question were missing."
            )
        else:
            feedback["overall"] = (
                "Incorrect or off-topic answer. "
                "Review the fundamentals of this topic before your next attempt."
            )

        # ── Strengths ────────────────────────────────────────
        if found_kws:
            feedback["strengths"].append(
                f"You correctly mentioned: {', '.join(found_kws[:5])}."
            )
        if content_score >= 70:
            feedback["strengths"].append("Good depth — your answer was detailed and structured.")
        if grammar_score >= 80:
            feedback["strengths"].append("Clear language and good grammar throughout.")
        if confidence_score >= 70:
            feedback["strengths"].append("Confident and well-structured delivery.")
        if analysis.get("sentence_count", 0) >= 4:
            feedback["strengths"].append("Good multi-sentence explanation style.")

        # ── Weaknesses ───────────────────────────────────────
        if missing_kws:
            feedback["weaknesses"].append(
                f"Missing key concepts: {', '.join(missing_kws[:6])}."
            )
        if technical_score < 40:
            feedback["weaknesses"].append(
                "The answer did not demonstrate sufficient technical knowledge for this question."
            )
        if content_score < 40:
            feedback["weaknesses"].append(
                "Answer is too brief or lacks depth. Aim for at least 40–60 words."
            )
        if grammar_score < 60:
            feedback["weaknesses"].append("Grammar and sentence structure need improvement.")
        if confidence_score < 40:
            feedback["weaknesses"].append(
                "Answer sounds uncertain. Reduce hedging words like 'maybe', 'I think'."
            )
        if quality == "poor":
            feedback["weaknesses"].append(
                "The overall response quality was low. Work on providing complete answers."
            )

        # ── Specific improvement suggestions ─────────────────
        if missing_kws:
            missing_display = ", ".join(missing_kws[:6])
            feedback["improvements"].append(
                f"Study and include these key concepts in your answer: {missing_display}."
            )
        if technical_score < 50:
            feedback["improvements"].append(
                "Review the fundamentals of this topic. "
                "Focus on understanding the definition, purpose, and a concrete example."
            )
        if analysis.get("word_count", 0) < 30:
            feedback["improvements"].append(
                "Expand your answer: define the concept, give an example, "
                "and explain when/why it is used."
            )
        if analysis.get("sentence_count", 0) < 3:
            feedback["improvements"].append(
                "Structure your answer with at least 3 sentences: "
                "definition → example → real-world use."
            )
        if confidence_score < 50:
            feedback["improvements"].append(
                "Use direct, confident language. Replace 'I think' / 'maybe' "
                "with definitive statements."
            )
        if not feedback["improvements"]:
            feedback["improvements"].append(
                "Good job! Keep practising to maintain this level of accuracy."
            )

        # ── Technical accuracy summary ────────────────────────
        if technical_score >= 80:
            feedback["technical_accuracy"] = (
                f"Excellent technical accuracy. You covered "
                f"{len(found_kws)}/{len(found_kws) + len(missing_kws)} key concepts."
            )
        elif technical_score >= 60:
            feedback["technical_accuracy"] = (
                f"Moderate technical accuracy. "
                f"You covered {len(found_kws)} of {len(found_kws)+len(missing_kws)} key concepts."
            )
        elif technical_score >= 30:
            feedback["technical_accuracy"] = (
                f"Weak technical accuracy. Only {len(found_kws)} keyword(s) found. "
                f"Missing: {', '.join(missing_kws[:4])}."
            )
        else:
            feedback["technical_accuracy"] = (
                "Very low technical accuracy. "
                f"None or very few of the expected concepts were mentioned. "
                f"Expected: {', '.join((found_kws + missing_kws)[:6])}."
            )

        # ── Grammar suggestions ───────────────────────────────
        if grammar_score < 70:
            feedback["grammar_suggestions"] = (
                "Work on grammar: check punctuation, avoid run-on sentences, "
                "and capitalise the first word of each sentence."
            )
        else:
            feedback["grammar_suggestions"] = "Grammar is good — keep it up."

        # ── Next steps ────────────────────────────────────────
        if total_score >= 75:
            feedback["next_steps"] = "Move on to the next question. You're doing well!"
        elif total_score >= 50:
            feedback["next_steps"] = (
                "Brush up on the missing concepts and try a similar question again."
            )
        else:
            feedback["next_steps"] = (
                f"Review this topic thoroughly. "
                + (f"Focus on: {', '.join(missing_kws[:4])}." if missing_kws else
                   "Focus on the core definition and use-cases.")
            )

        return feedback

    # ─────────────────────────────────────────────────────────
    # WEAK / STRONG AREA ANALYSIS
    # ─────────────────────────────────────────────────────────
    def identify_weak_areas(self, answers: List[Dict]) -> List[Dict]:
        """Identify weak topic areas from answer history."""
        category_scores = {}
        category_missing = {}

        for answer in answers:
            category = answer.get("analysis", {}).get("category", "unknown")
            score    = answer.get("scores",   {}).get("technical_score", 0)
            missing  = answer.get("scores",   {}).get("missing_keywords", [])

            if category not in category_scores:
                category_scores[category]  = []
                category_missing[category] = []
            category_scores[category].append(score)
            category_missing[category].extend(missing)

        weak_areas = []
        for category, s_list in category_scores.items():
            avg_score = sum(s_list) / len(s_list)
            if avg_score < 60:
                # Most frequently missing keywords for this category
                freq   = Counter(category_missing[category])
                top_kw = [kw for kw, _ in freq.most_common(4)]
                weak_areas.append({
                    "category":        category,
                    "average_score":   round(avg_score, 2),
                    "question_count":  len(s_list),
                    "missing_concepts": top_kw,
                    "recommendation":  self._get_weakness_recommendation(category),
                })

        return sorted(weak_areas, key=lambda x: x["average_score"])

    def _get_weakness_recommendation(self, category: str) -> str:
        recommendations = {
            "programming":       "Practice coding fundamentals: variables, loops, functions, recursion.",
            "web_development":   "Study HTTP, REST APIs, HTML/CSS/JS, and frontend frameworks.",
            "web":               "Study HTTP, REST APIs, HTML/CSS/JS, and frontend frameworks.",
            "database":          "Practice SQL queries, JOINs, normalization, and ACID properties.",
            "data_science":      "Study ML algorithms, evaluation metrics, and model validation.",
            "software_testing":  "Learn testing levels, TDD, automation tools like Selenium/pytest.",
            "oop":               "Review OOP principles: encapsulation, inheritance, polymorphism, abstraction.",
            "algorithms":        "Practice Big-O analysis, sorting, searching, and data structures.",
            "operating_system":  "Study processes, threads, memory management, and scheduling.",
            "general":           "Practice forming clear, complete answers even when uncertain.",
        }
        return recommendations.get(category, "Review this topic in depth with examples.")

    def identify_strengths(self, answers: List[Dict]) -> List[Dict]:
        """Identify strong topic areas from answer history."""
        category_scores = {}

        for answer in answers:
            category = answer.get("analysis", {}).get("category", "unknown")
            score    = answer.get("scores",   {}).get("technical_score", 0)

            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(score)

        strengths = []
        for category, s_list in category_scores.items():
            avg_score = sum(s_list) / len(s_list)
            if avg_score >= 65:
                strengths.append({
                    "category":      category,
                    "average_score": round(avg_score, 2),
                    "question_count": len(s_list),
                })

        return sorted(strengths, key=lambda x: x["average_score"], reverse=True)

    # ─────────────────────────────────────────────────────────
    # FINAL REPORT HELPERS
    # ─────────────────────────────────────────────────────────
    def generate_final_feedback(self, average_score: float, weak_areas: List[Dict]) -> str:
        if average_score >= 80:
            return (
                "Outstanding performance! You demonstrated strong technical knowledge "
                "and communication skills. Keep building on your strengths."
            )
        elif average_score >= 70:
            return (
                "Good job! You have a solid understanding of the topics. "
                "Focus on improving your weak areas to achieve even better results."
            )
        elif average_score >= 55:
            return (
                "Decent performance. You have basic understanding but need to "
                "strengthen your technical answers. Review the weak areas identified."
            )
        elif average_score >= 40:
            return (
                "Below average. Many key concepts were missing from your answers. "
                "Focus on understanding definitions, examples, and use-cases for each topic."
            )
        else:
            return (
                "Keep practising! Focus on the fundamentals: learn core definitions, "
                "memorise key terms, and practice explaining with examples. "
                "Consistent practice will lead to improvement."
            )

    def generate_improvement_plan(self, weak_areas: List[Dict]) -> List[Dict]:
        """Generate a personalised improvement plan from weak areas."""
        plan = []
        for area in weak_areas:
            category = area.get("category", "general")
            missing  = area.get("missing_concepts", [])
            plan.append({
                "area":           category,
                "action":         self._get_improvement_action(category),
                "focus_concepts": missing,
                "resources":      self._get_learning_resources(category),
                "priority":       "high" if area.get("average_score", 100) < 40 else "medium",
            })
        return plan

    def _get_improvement_action(self, category: str) -> str:
        actions = {
            "programming":       "Practice coding problems daily; focus on data structures and algorithms.",
            "web_development":   "Build small web projects to understand HTTP, APIs, and frameworks.",
            "web":               "Build small web projects to understand HTTP, APIs, and frameworks.",
            "database":          "Practice SQL queries and learn database design patterns.",
            "oop":               "Study design patterns and practice object-oriented design exercises.",
            "data_science":      "Complete ML tutorials and work on real datasets via Kaggle.",
            "software_testing":  "Learn testing frameworks and write test cases for a personal project.",
            "algorithms":        "Solve algorithm challenges on LeetCode / HackerRank daily.",
            "operating_system":  "Read OS textbook chapters on memory, processes, and scheduling.",
            "general":           "Practice more interview questions and review fundamentals.",
        }
        return actions.get(category, "Review and practice this topic with examples.")

    def _get_learning_resources(self, category: str) -> List[str]:
        resources = {
            "programming":       ["LeetCode", "HackerRank", "GeeksforGeeks"],
            "web_development":   ["MDN Web Docs", "React Documentation", "REST API Tutorial"],
            "web":               ["MDN Web Docs", "React Documentation", "REST API Tutorial"],
            "database":          ["SQLZoo", "Database Normalization Guide", "Use The Index, Luke"],
            "oop":               ["Refactoring Guru (Design Patterns)", "SOLID Principles Guide"],
            "data_science":      ["Kaggle Learn", "Coursera ML by Andrew Ng", "Scikit-learn Docs"],
            "software_testing":  ["Selenium Documentation", "pytest Docs", "ISTQB Study Guide"],
            "algorithms":        ["LeetCode", "VisuAlgo", "CLRS (Introduction to Algorithms)"],
            "operating_system":  ["OS by Tanenbaum", "GeeksforGeeks OS Articles"],
            "general":           ["Interview Prep Books", "Pramp (Mock Interviews)"],
        }
        return resources.get(category, ["Online tutorials", "Practice exercises"])


# ─────────────────────────────────────────────────────────────
# Standalone test
# ─────────────────────────────────────────────────────────────
def _demo():
    engine = FeedbackEngine()

    cases = [
        {
            "label": "CORRECT answer",
            "answer": (
                "Object-oriented programming organises code into classes and objects. "
                "It uses inheritance to share behaviour between parent and child classes, "
                "encapsulation to hide internal state, polymorphism to allow different types "
                "to be treated uniformly, and abstraction to expose only essential details."
            ),
            "expected": ["class", "object", "inheritance", "encapsulation", "abstraction"],
            "category": "oop",
        },
        {
            "label": "PARTIALLY CORRECT",
            "answer": "OOP is about using classes and objects. Inheritance lets one class use another's methods.",
            "expected": ["class", "object", "inheritance", "encapsulation", "abstraction"],
            "category": "oop",
        },
        {
            "label": "WRONG / off-topic answer",
            "answer": (
                "OOP is a way to optimise database queries using indexes and normalization. "
                "It involves writing SQL joins to retrieve data from multiple tables efficiently."
            ),
            "expected": ["class", "object", "inheritance", "encapsulation", "abstraction"],
            "category": "oop",
        },
        {
            "label": "BLANK / I don't know",
            "answer": "I don't know.",
            "expected": ["class", "object", "inheritance", "encapsulation", "abstraction"],
            "category": "oop",
        },
    ]

    from nlp_analyzer import NLPAnalyzer
    analyzer = NLPAnalyzer()

    print("=" * 60)
    print("  Feedback Engine — Score Accuracy Demo")
    print("=" * 60)
    for c in cases:
        analysis = analyzer.analyze_answer(c["answer"])
        scores   = engine.calculate_scores(
            answer=c["answer"],
            analysis=analysis,
            expected_keywords=c["expected"],
            question_category=c["category"],
        )
        fb = engine.generate_feedback(
            answer=c["answer"],
            analysis=analysis,
            scores=scores,
            question="What is OOP?",
            expected_keywords=c["expected"],
        )
        print(f"\n[{c['label']}]")
        print(f"  Total Score   : {scores['total_score']}  ({scores['grade']})")
        print(f"  Technical     : {scores['technical_score']}")
        print(f"  Content       : {scores['content_score']}")
        print(f"  Confidence    : {scores['confidence_score']}")
        print(f"  Grammar       : {scores['grammar_score']}")
        print(f"  Quality (ML)  : {analysis.get('quality_prediction','N/A')}")
        print(f"  Found KWs     : {scores['found_keywords']}")
        print(f"  Missing KWs   : {scores['missing_keywords']}")
        print(f"  Overall FB    : {fb['overall']}")
        print(f"  Improvements  : {fb['improvements']}")


if __name__ == "__main__":
    _demo()
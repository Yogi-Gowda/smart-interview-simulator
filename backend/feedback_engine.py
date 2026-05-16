# Feedback Engine Module
# Generates strict answer verdicts, scores, and reports.

import math
import re
from collections import Counter
from typing import Dict, List, Set


class FeedbackEngine:
    """Generate feedback and calculate answer correctness."""

    # Technical accuracy should dominate the final score. Grammar and confidence
    # can improve presentation, but they must not make a wrong answer look correct.
    WEIGHT_TECHNICAL = 0.65
    WEIGHT_CONTENT = 0.20
    WEIGHT_CONFIDENCE = 0.05
    WEIGHT_GRAMMAR = 0.10

    CORRECT_MATCH_RATIO = 0.70
    MIN_WORDS_FOR_CORRECT = 8
    WRONG_SCORE_CAP = 49

    STOP_WORDS = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "has", "have", "in", "into", "is", "it", "its", "of", "on", "or",
        "that", "the", "their", "this", "to", "was", "were", "with", "we",
        "you", "your", "i", "they", "them", "can", "will", "would", "should",
    }

    CATEGORY_GROUPS = {
        "web": {"web_development", "security", "architecture", "devops"},
        "web_development": {"web", "security", "architecture", "devops"},
        "oop": {"programming", "design_patterns"},
        "programming": {"oop", "algorithms", "data_structures", "operating_system"},
        "database": {"data_science", "data_analysis", "preprocessing"},
        "machine_learning": {"data_science", "analysis", "statistics"},
        "data_science": {"machine_learning", "analysis", "statistics"},
        "basics": {"general", "programming", "database", "software_testing"},
        "types": {"software_testing", "testing"},
        "testing": {"software_testing", "types"},
    }

    CONCEPT_ALIASES = {
        "abstraction": ["abstract", "hide implementation", "essential details"],
        "acceptance": ["uat", "user acceptance"],
        "api": ["application programming interface"],
        "array": ["indexed collection", "fixed collection"],
        "async": ["asynchronous", "non blocking", "non-blocking"],
        "authentication": ["login", "identity verification", "verify identity"],
        "authorization": ["permission", "access control", "allowed access"],
        "availability": ["available", "uptime"],
        "base case": ["stopping condition", "termination condition"],
        "big o": ["big-o", "time complexity notation", "asymptotic"],
        "black box": ["black-box"],
        "class": ["classes", "blueprint", "template"],
        "client": ["frontend", "browser"],
        "collection": ["group", "set"],
        "communication": ["communicate", "exchange data", "talk to each other"],
        "consistency": ["consistent"],
        "container": ["containers", "docker container"],
        "data type": ["datatype", "type of data"],
        "database": ["db", "data store", "datastore"],
        "deadlock": ["circular wait"],
        "defect": ["bug", "issue"],
        "deployment": ["deploy", "release"],
        "durability": ["durable", "persisted", "persistence"],
        "encapsulation": ["encapsulate", "data hiding", "hide internal state", "private data"],
        "equivalence": ["equivalent"],
        "factory": ["factory pattern"],
        "foreign key": ["foreign-key", "referential key", "relationship key"],
        "function": ["method", "procedure", "routine"],
        "hash function": ["hashing function"],
        "html": ["hypertext markup language"],
        "http": ["hypertext transfer protocol"],
        "inheritance": ["inherit", "inherits", "extends", "parent class", "child class", "subclass"],
        "integration": ["integrated"],
        "interface": ["contract"],
        "isolation": ["isolated"],
        "json": ["javascript object notation"],
        "lifo": ["last in first out"],
        "loose coupling": ["loosely coupled", "decoupled"],
        "manual": ["human executed", "manual testing"],
        "memory": ["ram"],
        "message queue": ["queue", "broker"],
        "microservices": ["microservice", "small independent services"],
        "model": ["data model"],
        "normalization": ["normalisation", "normalize", "normalise"],
        "object": ["objects", "instance", "instances"],
        "open addressing": ["linear probing", "quadratic probing"],
        "parameter": ["argument"],
        "parameterized": ["prepared statement", "parameterised", "bind parameter"],
        "partition tolerance": ["network partition", "partition tolerant"],
        "pca": ["principal component analysis"],
        "polymorphism": ["many forms", "method overriding", "override behavior"],
        "primary key": ["primary-key", "unique identifier", "unique id"],
        "red green refactor": ["red-green-refactor", "red green refactoring"],
        "request": ["api call", "http call"],
        "response": ["reply", "result"],
        "rest": ["representational state transfer", "restful"],
        "sanitization": ["sanitisation", "sanitize", "clean input", "escape input"],
        "schema": ["structure"],
        "security": ["secure"],
        "server": ["backend"],
        "singleton": ["singleton pattern", "single instance"],
        "soap": ["simple object access protocol"],
        "storage": ["store", "stores", "stored", "save", "keeps"],
        "supervised": ["labelled", "labeled data"],
        "synchronization": ["synchronisation", "sync", "locking"],
        "test case": ["testcase"],
        "test first": ["write tests first"],
        "thread": ["threads", "lightweight process"],
        "validation": ["validate", "checking correctness"],
        "variable": ["named storage", "identifier"],
        "virtual dom": ["vdom"],
        "white box": ["white-box"],
    }

    ACRONYM_FULL_FORMS = {
        "acid": ["atomicity consistency isolation durability"],
        "api": ["application programming interface"],
        "cap": ["consistency availability partition tolerance"],
        "cd": ["continuous deployment", "continuous delivery"],
        "ci": ["continuous integration"],
        "cors": ["cross origin resource sharing"],
        "css": ["cascading style sheets"],
        "dbms": ["database management system"],
        "dom": ["document object model"],
        "fifo": ["first in first out"],
        "html": ["hypertext markup language"],
        "http": ["hypertext transfer protocol"],
        "json": ["javascript object notation"],
        "lifo": ["last in first out"],
        "mvc": ["model view controller"],
        "oop": ["object oriented programming", "object orientated programming"],
        "os": ["operating system"],
        "pca": ["principal component analysis"],
        "rest": ["representational state transfer"],
        "soap": ["simple object access protocol"],
        "sql": ["structured query language"],
        "tdd": ["test driven development", "test first development"],
        "xml": ["extensible markup language"],
    }

    def __init__(self):
        self.feedback_history = []

    def calculate_scores(
        self,
        answer: str,
        analysis: Dict,
        expected_keywords: List[str],
        question_category: str,
        question: str = "",
    ) -> Dict:
        """Calculate sub-scores and a strict correct/wrong verdict."""

        expected_keywords = self._dedupe_keywords(expected_keywords or [])
        kw_result = self._keyword_analysis(answer or "", expected_keywords)
        full_form_info = self._full_form_analysis(answer or "", question or "")

        if analysis.get("low_effort") and not full_form_info["matched"]:
            low_effort_message = (
                "The answer is too short or incomplete for this question."
                if kw_result["found"]
                else "No meaningful answer was provided."
            )
            scores = {
                "content_score": 0,
                "grammar_score": analysis.get("grammar_quality", 0),
                "technical_score": 0,
                "confidence_score": 0,
                "total_score": 0,
                "grade": "F",
                "low_effort": True,
                "low_effort_reason": analysis.get("low_effort_reason", "low_effort"),
                "found_keywords": kw_result["found"],
                "missing_keywords": kw_result["missing"],
                "matched_keyword_count": len(kw_result["found"]),
                "expected_keyword_count": len(expected_keywords),
                "required_keyword_count": self._required_keyword_count(len(expected_keywords)),
                "match_percentage": kw_result["match_pct"],
                "concept_evidence": kw_result["evidence"],
                "contradictions": [],
                "full_form_match": False,
                "full_form_matches": [],
                "is_correct": False,
                "verdict": "wrong",
                "answer_status": "Wrong",
                "decision_reasons": [low_effort_message],
                "verdict_reason": low_effort_message,
            }
            self.feedback_history.append(scores)
            return scores

        technical_score = self._calculate_technical_score(answer, analysis, kw_result)
        if full_form_info["matched"]:
            technical_score = max(technical_score, 85)

        content_score = self._calculate_content_score(answer, analysis, technical_score)
        if full_form_info["matched"]:
            content_score = max(content_score, 45)

        grammar_score = int(max(0, min(100, analysis.get("grammar_quality", 70))))
        confidence_score = self._calculate_confidence_score(answer, analysis)
        if full_form_info["matched"]:
            confidence_score = max(confidence_score, 45)

        verdict_info = self._decide_verdict(
            answer=answer,
            analysis=analysis,
            kw_result=kw_result,
            technical_score=technical_score,
            expected_keywords=expected_keywords,
            question_category=question_category,
            full_form_info=full_form_info,
        )

        total_score = round(
            (technical_score * self.WEIGHT_TECHNICAL)
            + (content_score * self.WEIGHT_CONTENT)
            + (confidence_score * self.WEIGHT_CONFIDENCE)
            + (grammar_score * self.WEIGHT_GRAMMAR)
        )

        if not verdict_info["is_correct"]:
            total_score = min(total_score, self.WRONG_SCORE_CAP)

        scores = {
            "content_score": content_score,
            "grammar_score": grammar_score,
            "technical_score": technical_score,
            "confidence_score": confidence_score,
            "total_score": total_score,
            "grade": self._get_grade(total_score),
            "low_effort": False,
            "found_keywords": kw_result["found"],
            "missing_keywords": kw_result["missing"],
            "matched_keyword_count": len(kw_result["found"]),
            "expected_keyword_count": len(expected_keywords),
            "required_keyword_count": self._required_keyword_count(len(expected_keywords)),
            "match_percentage": kw_result["match_pct"],
            "concept_evidence": kw_result["evidence"],
            "contradictions": verdict_info["contradictions"],
            "full_form_match": full_form_info["matched"],
            "full_form_matches": full_form_info["matches"],
            "is_correct": verdict_info["is_correct"],
            "verdict": "correct" if verdict_info["is_correct"] else "wrong",
            "answer_status": "Correct" if verdict_info["is_correct"] else "Wrong",
            "decision_reasons": verdict_info["reasons"],
            "verdict_reason": " ".join(verdict_info["reasons"]),
        }
        self.feedback_history.append(scores)
        return scores

    def _keyword_analysis(self, answer: str, expected_keywords: List[str]) -> Dict:
        """
        Match expected concepts against the answer.

        Matching uses exact phrases, common aliases, word boundaries, simple stems,
        and singular/plural variants. This avoids the old substring-only behavior
        that could count unrelated words as correct.
        """
        normalized_answer = self._normalize_text(answer)
        answer_tokens = self._tokenize(normalized_answer)
        answer_stems = {self._stem(token) for token in answer_tokens}

        found = []
        missing = []
        evidence = {}

        for keyword in expected_keywords:
            matched_by = self._matched_variant(keyword, normalized_answer, answer_stems)
            if matched_by:
                found.append(keyword)
                evidence[keyword] = matched_by
            else:
                missing.append(keyword)

        match_pct = round((len(found) / len(expected_keywords) * 100), 2) if expected_keywords else 0
        return {
            "found": found,
            "missing": missing,
            "match_pct": match_pct,
            "evidence": evidence,
        }

    def _calculate_technical_score(self, answer: str, analysis: Dict, kw_result: Dict) -> int:
        expected_count = len(kw_result["found"]) + len(kw_result["missing"])
        quality = analysis.get("quality_prediction", "average")

        if expected_count == 0:
            return {"good": 72, "average": 50, "poor": 20}.get(quality, 50)

        score = int(round(kw_result["match_pct"]))

        # A complete, substantial answer can earn a small presentation bonus, but
        # missing concepts still control the result.
        if score >= 70 and analysis.get("word_count", 0) >= self.MIN_WORDS_FOR_CORRECT:
            score += 5
        if quality == "poor":
            score -= 10

        return max(0, min(100, score))

    def _calculate_content_score(self, answer: str, analysis: Dict, technical_score: int) -> int:
        quality = analysis.get("quality_prediction", "average")
        word_count = analysis.get("word_count", 0)
        sentence_count = analysis.get("sentence_count", 0)

        quality_base = {"good": 55, "average": 35, "poor": 10}.get(quality, 35)
        score = quality_base

        if word_count >= 80:
            score += 25
        elif word_count >= 50:
            score += 18
        elif word_count >= 30:
            score += 10
        elif word_count >= 15:
            score += 5

        if sentence_count >= 4:
            score += 10
        elif sentence_count >= 2:
            score += 5

        if technical_score < 40:
            score = min(score, 35)
        elif technical_score < 70:
            score = min(score, 60)

        return max(0, min(100, score))

    def _calculate_confidence_score(self, answer: str, analysis: Dict) -> int:
        score = 40
        answer_lower = self._normalize_text(answer)

        hedging = [
            "maybe", "perhaps", "i think", "i guess", "not sure",
            "possibly", "i believe", "kind of", "sort of",
        ]
        definitive = [
            "definitely", "certainly", "clearly", "specifically",
            "in summary", "in conclusion",
        ]

        score -= sum(1 for word in hedging if word in answer_lower) * 6
        score += sum(1 for word in definitive if word in answer_lower) * 4

        if "for example" in answer_lower or "for instance" in answer_lower:
            score += 15

        if analysis.get("sentence_count", 0) >= 4:
            score += 15
        elif analysis.get("sentence_count", 0) >= 2:
            score += 8

        return max(0, min(100, score))

    def _decide_verdict(
        self,
        answer: str,
        analysis: Dict,
        kw_result: Dict,
        technical_score: int,
        expected_keywords: List[str],
        question_category: str,
        full_form_info: Dict,
    ) -> Dict:
        reasons = []
        expected_count = len(expected_keywords)
        matched_count = len(kw_result["found"])
        required_count = self._required_keyword_count(expected_count)
        contradictions = self._find_contradictions(answer, expected_keywords)
        has_substance = self._answer_has_substance(answer, analysis)
        full_form_matched = full_form_info.get("matched", False)

        if full_form_matched:
            full_forms = ", ".join(
                f"{item['acronym'].upper()}: {item['full_form']}"
                for item in full_form_info.get("matches", [])
            )
            reasons.append(f"Recognized correct full form: {full_forms}.")

        if expected_count:
            if matched_count < required_count:
                if not full_form_matched:
                    reasons.append(
                        f"Matched {matched_count}/{expected_count} required concepts; "
                        f"at least {required_count} are needed."
                    )
            else:
                reasons.append(
                    f"Matched {matched_count}/{expected_count} required concepts."
                )
        elif technical_score < 70:
            reasons.append("The answer did not show enough technical detail.")

        if not has_substance and not full_form_matched:
            reasons.append("The answer is too short to prove understanding.")

        if contradictions:
            reasons.append(
                "Possible contradiction detected around: "
                + ", ".join(contradictions[:3])
                + "."
            )

        answer_category = analysis.get("category", "general")
        category_matches = self._category_matches(question_category, answer_category)
        if not category_matches and matched_count < required_count and not full_form_matched:
            reasons.append(
                f"The answer appears off-topic for {question_category or 'this'} question."
            )

        if full_form_matched:
            is_correct = not contradictions
        else:
            is_correct = (
                matched_count >= required_count
                and technical_score >= 70
                and has_substance
                and not contradictions
            ) if expected_count else (
                technical_score >= 70 and has_substance and not contradictions
            )

        if is_correct and not reasons:
            reasons.append("Answer meets the required technical concepts.")

        if not is_correct and not reasons:
            reasons.append("Answer does not meet the required correctness threshold.")

        return {
            "is_correct": is_correct,
            "reasons": reasons,
            "contradictions": contradictions,
        }

    def generate_feedback(
        self,
        answer: str,
        analysis: Dict,
        scores: Dict,
        question: str,
        expected_keywords: List[str] = None,
    ) -> Dict:
        """Generate detailed, direct feedback for the answer."""
        expected_keywords = self._dedupe_keywords(expected_keywords or [])
        is_correct = scores.get("is_correct", False)
        found_kws = scores.get("found_keywords", [])
        missing_kws = scores.get("missing_keywords", [])
        technical_score = scores.get("technical_score", 0)
        content_score = scores.get("content_score", 0)
        grammar_score = scores.get("grammar_score", 0)
        confidence_score = scores.get("confidence_score", 0)
        full_form_match = scores.get("full_form_match", False)
        full_form_matches = scores.get("full_form_matches", [])

        feedback = {
            "overall": "",
            "verdict": "correct" if is_correct else "wrong",
            "answer_status": "Correct" if is_correct else "Wrong",
            "is_correct": is_correct,
            "strengths": [],
            "weaknesses": [],
            "improvements": [],
            "technical_accuracy": "",
            "grammar_suggestions": "",
            "next_steps": "",
            "missing_concepts": missing_kws,
            "found_concepts": found_kws,
            "accuracy_report": {
                "question": question,
                "required_concepts": expected_keywords,
                "matched_concepts": found_kws,
                "missing_concepts": missing_kws,
                "matched_count": scores.get("matched_keyword_count", 0),
                "required_to_pass": scores.get("required_keyword_count", 0),
                "expected_count": scores.get("expected_keyword_count", 0),
                "match_percentage": scores.get("match_percentage", 0),
                "decision_reasons": scores.get("decision_reasons", []),
                "concept_evidence": scores.get("concept_evidence", {}),
                "full_form_matches": full_form_matches,
            },
        }

        if scores.get("low_effort"):
            feedback["overall"] = "Wrong. " + scores.get(
                "verdict_reason",
                "The answer is too short or incomplete for this question.",
            )
            if found_kws:
                feedback["weaknesses"].append(
                    "Only a small part of the expected topic was mentioned: "
                    + ", ".join(found_kws[:4])
                    + "."
                )
            else:
                feedback["weaknesses"].append("No answer or an explicit unknown response was detected.")
            feedback["improvements"].append(
                "Attempt the answer by giving a definition, one example, and why the concept matters."
            )
            if expected_keywords:
                feedback["improvements"].append(
                    "Study these required concepts: " + ", ".join(expected_keywords[:6]) + "."
                )
            feedback["technical_accuracy"] = (
                "Verdict: Wrong. The answer is too short for this question."
                if found_kws
                else "Verdict: Wrong. The answer did not attempt the topic."
            )
            feedback["grammar_suggestions"] = "Grammar cannot be meaningfully evaluated without an answer."
            feedback["next_steps"] = "Review the topic and retry this question."
            return feedback

        if is_correct and full_form_match:
            full_forms = ", ".join(
                f"{item['acronym'].upper()} = {item['full_form']}"
                for item in full_form_matches
            )
            feedback["overall"] = (
                f"Correct. The full form was recognized ({full_forms}). "
                "The answer is correct, but it is brief."
            )
        elif is_correct:
            feedback["overall"] = (
                "Correct. Your answer covered enough required concepts to be marked correct."
            )
        else:
            reason = scores.get("verdict_reason") or "The answer missed required concepts."
            feedback["overall"] = f"Wrong. {reason}"

        if found_kws:
            feedback["strengths"].append("Relevant concepts mentioned: " + ", ".join(found_kws[:6]) + ".")
        if full_form_match:
            feedback["strengths"].append(
                "Correct full form: "
                + ", ".join(
                    f"{item['acronym'].upper()} = {item['full_form']}"
                    for item in full_form_matches
                )
                + "."
            )
        if is_correct and content_score >= 70:
            feedback["strengths"].append("The answer has good depth and structure.")
        if grammar_score >= 80:
            feedback["strengths"].append("Language and grammar are clear.")
        if confidence_score >= 65:
            feedback["strengths"].append("Delivery is direct and confident.")

        if missing_kws and full_form_match:
            feedback["weaknesses"].append(
                "The answer gives the full form but does not explain the concept in detail."
            )
        elif missing_kws:
            feedback["weaknesses"].append("Missing required concepts: " + ", ".join(missing_kws[:6]) + ".")
        if technical_score < 70:
            feedback["weaknesses"].append("Technical coverage is below the correctness threshold.")
        if content_score < 40:
            feedback["weaknesses"].append("Answer is too brief or lacks explanation.")
        if grammar_score < 60:
            feedback["weaknesses"].append("Grammar and sentence structure need improvement.")
        if confidence_score < 40:
            feedback["weaknesses"].append("Answer sounds uncertain or underdeveloped.")

        if missing_kws and full_form_match:
            feedback["improvements"].append(
                "Make the answer stronger by explaining: " + ", ".join(missing_kws[:6]) + "."
            )
        elif missing_kws:
            feedback["improvements"].append(
                "Add these concepts to make the answer correct: " + ", ".join(missing_kws[:6]) + "."
            )
        if analysis.get("word_count", 0) < 30:
            feedback["improvements"].append(
                "Expand the response with a definition, example, and practical use."
            )
        if analysis.get("sentence_count", 0) < 2:
            feedback["improvements"].append(
                "Use at least two clear sentences so the evaluator can verify your reasoning."
            )
        if confidence_score < 50:
            feedback["improvements"].append(
                "Use direct statements and avoid phrases like 'maybe' or 'I think'."
            )
        if not feedback["improvements"]:
            feedback["improvements"].append("Keep this structure: definition, key concepts, and example.")

        if full_form_match:
            feedback["technical_accuracy"] = (
                f"Verdict: {feedback['answer_status']}. Correct full form recognized; "
                "add a short explanation to improve completeness."
            )
        else:
            feedback["technical_accuracy"] = (
                f"Verdict: {feedback['answer_status']}. "
                f"Matched {scores.get('matched_keyword_count', 0)}/"
                f"{scores.get('expected_keyword_count', 0)} expected concepts "
                f"({scores.get('match_percentage', 0)}%)."
            )

        if grammar_score < 70:
            feedback["grammar_suggestions"] = (
                "Check punctuation, avoid run-on sentences, and capitalize sentence starts."
            )
        else:
            feedback["grammar_suggestions"] = "Grammar is clear."

        feedback["next_steps"] = (
            "Move to the next question." if is_correct
            else "Review the missing concepts and retry a similar question."
        )

        return feedback

    def identify_weak_areas(self, answers: List[Dict]) -> List[Dict]:
        """Identify weak topic areas from answer history."""
        category_scores = {}
        category_missing = {}
        category_wrong = {}

        for answer in answers:
            category = answer.get("question_category") or answer.get("analysis", {}).get("category", "unknown")
            score = answer.get("scores", {}).get("technical_score", 0)
            missing = answer.get("scores", {}).get("missing_keywords", [])
            is_correct = answer.get("scores", {}).get("is_correct", False)

            category_scores.setdefault(category, []).append(score)
            category_missing.setdefault(category, []).extend(missing)
            category_wrong[category] = category_wrong.get(category, 0) + (0 if is_correct else 1)

        weak_areas = []
        for category, score_list in category_scores.items():
            avg_score = sum(score_list) / len(score_list)
            wrong_count = category_wrong.get(category, 0)
            if avg_score < 70 or wrong_count:
                freq = Counter(category_missing.get(category, []))
                top_keywords = [keyword for keyword, _ in freq.most_common(4)]
                weak_areas.append({
                    "category": category,
                    "average_score": round(avg_score, 2),
                    "question_count": len(score_list),
                    "wrong_count": wrong_count,
                    "missing_concepts": top_keywords,
                    "recommendation": self._get_weakness_recommendation(category),
                })

        return sorted(weak_areas, key=lambda item: (item["average_score"], -item["wrong_count"]))

    def identify_strengths(self, answers: List[Dict]) -> List[Dict]:
        """Identify strong topic areas from answer history."""
        category_scores = {}
        category_correct = {}

        for answer in answers:
            category = answer.get("question_category") or answer.get("analysis", {}).get("category", "unknown")
            score = answer.get("scores", {}).get("technical_score", 0)
            is_correct = answer.get("scores", {}).get("is_correct", False)

            category_scores.setdefault(category, []).append(score)
            category_correct[category] = category_correct.get(category, 0) + (1 if is_correct else 0)

        strengths = []
        for category, score_list in category_scores.items():
            avg_score = sum(score_list) / len(score_list)
            correct_count = category_correct.get(category, 0)
            if avg_score >= 75 and correct_count == len(score_list):
                strengths.append({
                    "category": category,
                    "average_score": round(avg_score, 2),
                    "question_count": len(score_list),
                    "correct_count": correct_count,
                })

        return sorted(strengths, key=lambda item: item["average_score"], reverse=True)

    def generate_final_feedback(
        self,
        average_score: float,
        weak_areas: List[Dict],
        accuracy_percentage: float = None,
    ) -> str:
        if accuracy_percentage is not None:
            if accuracy_percentage >= 80:
                return (
                    f"You answered {accuracy_percentage}% correctly. Strong performance; "
                    "keep refining explanations with examples."
                )
            if accuracy_percentage >= 50:
                return (
                    f"You answered {accuracy_percentage}% correctly. Several answers were related "
                    "but missed required concepts, so review the weak areas carefully."
                )
            return (
                f"You answered {accuracy_percentage}% correctly. Focus on fundamentals first: "
                "definitions, required keywords, and one concrete example for each topic."
            )

        if average_score >= 80:
            return "Outstanding performance. You demonstrated strong technical knowledge."
        if average_score >= 70:
            return "Good performance. Focus on weak areas to improve further."
        if average_score >= 55:
            return "Decent performance, but your technical answers need more complete coverage."
        if average_score >= 40:
            return "Below average. Many key concepts were missing from your answers."
        return "Keep practising. Start with core definitions and simple examples."

    def generate_improvement_plan(self, weak_areas: List[Dict]) -> List[Dict]:
        """Generate a personalised improvement plan from weak areas."""
        plan = []
        for area in weak_areas:
            category = area.get("category", "general")
            missing = area.get("missing_concepts", [])
            plan.append({
                "area": category,
                "action": self._get_improvement_action(category),
                "focus_concepts": missing,
                "resources": self._get_learning_resources(category),
                "priority": "high" if area.get("wrong_count", 0) or area.get("average_score", 100) < 50 else "medium",
            })
        return plan

    def _full_form_analysis(self, answer: str, question: str) -> Dict:
        """Recognize short acronym/full-form answers before low-effort scoring."""
        normalized_answer = self._normalize_text(answer)
        normalized_question = self._normalize_text(question)
        answer_tokens = set(self._tokenize(normalized_answer))
        question_tokens = set(self._tokenize(normalized_question))

        candidates = []
        for acronym, full_forms in self.ACRONYM_FULL_FORMS.items():
            question_has_acronym = self._acronym_in_tokens(acronym, question_tokens)
            question_has_full_form = any(
                self._full_form_phrase_matches(full_form, normalized_question)
                for full_form in full_forms
            )

            if not question_has_acronym and not question_has_full_form:
                continue
            if not self._question_allows_full_form_answer(normalized_question, acronym):
                continue

            answer_has_acronym = self._acronym_in_tokens(acronym, answer_tokens)
            matched_full_form = next(
                (
                    full_form
                    for full_form in full_forms
                    if self._full_form_phrase_matches(full_form, normalized_answer)
                ),
                "",
            )

            if question_has_acronym and matched_full_form:
                candidates.append({
                    "acronym": acronym,
                    "full_form": matched_full_form,
                    "match_type": "answer_full_form",
                })
            elif question_has_full_form and answer_has_acronym:
                candidates.append({
                    "acronym": acronym,
                    "full_form": full_forms[0],
                    "match_type": "answer_acronym",
                })

        required_acronyms = {
            acronym
            for acronym in self.ACRONYM_FULL_FORMS
            if (
                self._acronym_in_tokens(acronym, question_tokens)
                or any(
                    self._full_form_phrase_matches(full_form, normalized_question)
                    for full_form in self.ACRONYM_FULL_FORMS[acronym]
                )
            )
            and self._question_allows_full_form_answer(normalized_question, acronym)
        }
        matched_acronyms = {item["acronym"] for item in candidates}

        # If a question explicitly asks about multiple acronyms, e.g. REST and SOAP
        # or CI/CD, require the answer to expand all of them before accepting the
        # short full-form route.
        matched = bool(candidates) and required_acronyms.issubset(matched_acronyms)

        return {
            "matched": matched,
            "matches": candidates if matched else [],
            "required_acronyms": sorted(required_acronyms),
        }

    def _question_allows_full_form_answer(self, normalized_question: str, acronym: str) -> bool:
        """Return True when a full-form-only response is a fair minimum answer."""
        blocked_phrases = {
            "api": ["api testing", "rest and soap"],
            "sql": ["sql injection", "sql and nosql", "nosql"],
        }
        if any(phrase in normalized_question for phrase in blocked_phrases.get(acronym, [])):
            return False

        if "stands for" in normalized_question or "full form" in normalized_question:
            return True

        if re.search(rf"\bwhat\s+(?:is|are)\s+(?:a\s+|an\s+|the\s+)?{re.escape(acronym)}s?\b", normalized_question):
            return True

        if re.search(rf"\bexplain\b.*\b{re.escape(acronym)}s?\b", normalized_question):
            return True

        concept_cues = [
            "architecture", "pattern", "properties", "theorem", "concept",
            "principles", "dimensionality", "development", "integration",
            "deployment",
        ]
        if self._acronym_in_tokens(acronym, set(self._tokenize(normalized_question))):
            return any(cue in normalized_question for cue in concept_cues)

        full_form_in_question = any(
            self._full_form_phrase_matches(full_form, normalized_question)
            for full_form in self.ACRONYM_FULL_FORMS.get(acronym, [])
        )
        if full_form_in_question:
            return bool(re.search(r"\b(?:what|explain|define|concept)\b", normalized_question))

        return False

    def _acronym_in_tokens(self, acronym: str, tokens: Set[str]) -> bool:
        acronym = acronym.lower()
        return acronym in tokens or f"{acronym}s" in tokens

    def _full_form_phrase_matches(self, full_form: str, normalized_text: str) -> bool:
        expected = [
            self._stem(token)
            for token in self._tokenize(full_form)
            if token not in self.STOP_WORDS
        ]
        actual = [
            self._stem(token)
            for token in self._tokenize(normalized_text)
            if token not in self.STOP_WORDS
        ]
        return bool(expected) and all(token in actual for token in expected)

    def _required_keyword_count(self, expected_count: int) -> int:
        if expected_count <= 0:
            return 0
        if expected_count == 1:
            return 1
        return max(2, math.ceil(expected_count * self.CORRECT_MATCH_RATIO))

    def _dedupe_keywords(self, keywords: List[str]) -> List[str]:
        seen = set()
        result = []
        for keyword in keywords:
            cleaned = str(keyword).strip()
            lowered = cleaned.lower()
            if cleaned and lowered not in seen:
                seen.add(lowered)
                result.append(cleaned)
        return result

    def _matched_variant(self, keyword: str, normalized_answer: str, answer_stems: Set[str]) -> str:
        for variant in self._keyword_variants(keyword):
            if self._variant_matches(variant, normalized_answer, answer_stems):
                return variant
        return ""

    def _keyword_variants(self, keyword: str) -> List[str]:
        base = self._normalize_text(keyword)
        variants = {base}

        if base in self.CONCEPT_ALIASES:
            variants.update(self._normalize_text(alias) for alias in self.CONCEPT_ALIASES[base])

        words = self._tokenize(base)
        if len(words) == 1:
            word = words[0]
            variants.add(self._stem(word))
            if word.endswith("s") and not word.endswith("ss"):
                variants.add(word[:-1])
            else:
                variants.add(word + "s")

        return [variant for variant in variants if variant]

    def _variant_matches(self, variant: str, normalized_answer: str, answer_stems: Set[str]) -> bool:
        words = self._tokenize(variant)
        if not words:
            return False

        if len(words) == 1:
            return self._stem(words[0]) in answer_stems

        phrase_pattern = r"\b" + r"\s+".join(re.escape(word) for word in words) + r"\b"
        if re.search(phrase_pattern, normalized_answer):
            return True

        # Accept loose matching for compact technical phrases, e.g. "primary key"
        # even when the answer says "key that uniquely identifies a primary record".
        return all(self._stem(word) in answer_stems for word in words)

    def _find_contradictions(self, answer: str, expected_keywords: List[str]) -> List[str]:
        normalized_answer = self._normalize_text(answer)
        contradictions = []

        for keyword in expected_keywords:
            base = self._normalize_text(keyword)
            if not base:
                continue
            words = self._tokenize(base)
            phrase = r"\s+".join(re.escape(word) for word in words)
            patterns = [
                rf"\b(?:not|never|no)\s+(?:a\s+|an\s+|the\s+)?{phrase}\b",
                rf"\b{phrase}\s+(?:is|are|means)\s+not\b",
            ]
            if any(re.search(pattern, normalized_answer) for pattern in patterns):
                contradictions.append(keyword)

        return contradictions

    def _answer_has_substance(self, answer: str, analysis: Dict) -> bool:
        if analysis.get("word_count", 0) < self.MIN_WORDS_FOR_CORRECT:
            return False

        tokens = self._tokenize(answer)
        meaningful_tokens = [
            token for token in tokens
            if token not in self.STOP_WORDS and len(token) > 2
        ]
        return len(meaningful_tokens) >= 4

    def _category_matches(self, question_category: str, answer_category: str) -> bool:
        question_category = (question_category or "").lower()
        answer_category = (answer_category or "").lower()

        if not question_category or question_category in {"general", "basics"}:
            return True
        if not answer_category or answer_category in {"general", "unknown"}:
            return True
        if question_category == answer_category:
            return True
        return answer_category in self.CATEGORY_GROUPS.get(question_category, set())

    def _normalize_text(self, text: str) -> str:
        text = (text or "").lower()
        text = text.replace("'", " ")
        text = re.sub(r"[^a-z0-9+#\s-]", " ", text)
        text = text.replace("-", " ")
        return re.sub(r"\s+", " ", text).strip()

    def _tokenize(self, text: str) -> List[str]:
        normalized = self._normalize_text(text)
        return re.findall(r"[a-z0-9+#]+", normalized)

    def _stem(self, word: str) -> str:
        word = word.lower()
        if len(word) <= 4:
            return word

        suffixes = [
            "izations", "isation", "ization", "ations", "ation",
            "ments", "ment", "ingly", "edly", "ing", "ied", "ed", "es", "s",
        ]
        for suffix in suffixes:
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                if suffix == "s" and word.endswith("ss"):
                    continue
                if suffix == "ied":
                    return word[:-3] + "y"
                return word[:-len(suffix)]
        return word

    def _get_grade(self, score: int) -> str:
        if score >= 90:
            return "A+"
        if score >= 80:
            return "A"
        if score >= 70:
            return "B+"
        if score >= 60:
            return "B"
        if score >= 50:
            return "C"
        if score >= 40:
            return "D"
        return "F"

    def _get_weakness_recommendation(self, category: str) -> str:
        recommendations = {
            "programming": "Practice coding fundamentals: variables, loops, functions, recursion.",
            "web_development": "Study HTTP, REST APIs, HTML/CSS/JS, and frontend frameworks.",
            "web": "Study HTTP, REST APIs, HTML/CSS/JS, and frontend frameworks.",
            "database": "Practice SQL queries, JOINs, normalization, and ACID properties.",
            "data_science": "Study ML algorithms, evaluation metrics, and model validation.",
            "machine_learning": "Study ML algorithms, evaluation metrics, and model validation.",
            "software_testing": "Learn testing levels, TDD, and automation tools like Selenium or pytest.",
            "oop": "Review OOP principles: encapsulation, inheritance, polymorphism, abstraction.",
            "algorithms": "Practice Big-O analysis, sorting, searching, and data structures.",
            "data_structures": "Review arrays, linked lists, stacks, queues, trees, and hash tables.",
            "operating_system": "Study processes, threads, memory management, and scheduling.",
            "security": "Study validation, authorization, authentication, and secure coding patterns.",
            "general": "Practice forming clear, complete answers even when uncertain.",
        }
        return recommendations.get(category, "Review this topic in depth with examples.")

    def _get_improvement_action(self, category: str) -> str:
        actions = {
            "programming": "Practice coding problems and explain each solution aloud.",
            "web_development": "Build small web projects to understand HTTP, APIs, and frameworks.",
            "web": "Build small web projects to understand HTTP, APIs, and frameworks.",
            "database": "Practice SQL queries and learn database design patterns.",
            "oop": "Study design patterns and practice object-oriented design exercises.",
            "data_science": "Complete ML tutorials and work on small real datasets.",
            "machine_learning": "Review ML concepts with examples and evaluation metrics.",
            "software_testing": "Write test cases for a small project and map them to testing levels.",
            "algorithms": "Solve algorithm challenges and write down time and space complexity.",
            "data_structures": "Implement core data structures and explain their tradeoffs.",
            "operating_system": "Review memory, processes, threads, and scheduling with diagrams.",
            "security": "Practice secure input handling and common vulnerability prevention.",
            "general": "Practice more interview questions and review fundamentals.",
        }
        return actions.get(category, "Review and practice this topic with examples.")

    def _get_learning_resources(self, category: str) -> List[str]:
        resources = {
            "programming": ["LeetCode", "HackerRank", "GeeksforGeeks"],
            "web_development": ["MDN Web Docs", "React Documentation", "REST API Tutorial"],
            "web": ["MDN Web Docs", "React Documentation", "REST API Tutorial"],
            "database": ["SQLZoo", "Database Normalization Guide", "Use The Index, Luke"],
            "oop": ["Refactoring Guru", "SOLID Principles Guide"],
            "data_science": ["Kaggle Learn", "Scikit-learn Docs", "Google ML Crash Course"],
            "machine_learning": ["Kaggle Learn", "Scikit-learn Docs", "Google ML Crash Course"],
            "software_testing": ["Selenium Documentation", "pytest Docs", "ISTQB Study Guide"],
            "algorithms": ["LeetCode", "VisuAlgo", "CLRS"],
            "data_structures": ["VisuAlgo", "GeeksforGeeks", "LeetCode Explore"],
            "operating_system": ["Operating Systems: Three Easy Pieces", "GeeksforGeeks OS"],
            "security": ["OWASP Top 10", "PortSwigger Web Security Academy"],
            "general": ["Interview practice notes", "Mock interviews"],
        }
        return resources.get(category, ["Online tutorials", "Practice exercises"])


def _demo():
    engine = FeedbackEngine()

    cases = [
        {
            "label": "CORRECT answer",
            "answer": (
                "Object-oriented programming organizes code into classes and objects. "
                "It uses inheritance, encapsulation, polymorphism, and abstraction."
            ),
            "expected": ["class", "object", "inheritance", "encapsulation", "abstraction"],
            "category": "oop",
        },
        {
            "label": "WRONG partial answer",
            "answer": "OOP is about using classes and objects.",
            "expected": ["class", "object", "inheritance", "encapsulation", "abstraction"],
            "category": "oop",
        },
        {
            "label": "WRONG off-topic answer",
            "answer": "It is mainly SQL joins, indexes, and query optimization in databases.",
            "expected": ["class", "object", "inheritance", "encapsulation", "abstraction"],
            "category": "oop",
        },
    ]

    from nlp_analyzer import NLPAnalyzer

    analyzer = NLPAnalyzer()
    for case in cases:
        analysis = analyzer.analyze_answer(case["answer"])
        scores = engine.calculate_scores(
            answer=case["answer"],
            analysis=analysis,
            expected_keywords=case["expected"],
            question_category=case["category"],
        )
        feedback = engine.generate_feedback(
            answer=case["answer"],
            analysis=analysis,
            scores=scores,
            question="What is OOP?",
            expected_keywords=case["expected"],
        )
        print(f"{case['label']}: {scores['answer_status']} ({scores['total_score']})")
        print(feedback["overall"])


if __name__ == "__main__":
    _demo()

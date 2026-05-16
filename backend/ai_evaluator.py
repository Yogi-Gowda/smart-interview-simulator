# AI Evaluator Module
# Optional semantic answer evaluation using an OpenAI-compatible chat API.

import json
import os
import re
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


class AIEvaluator:
    """Evaluate interview answers with an external AI model API.

    The evaluator is optional. If no real API key is configured, callers should
    keep using the local rule-based feedback engine.
    """

    DUMMY_KEYS = {
        "",
        "dummy-api-key",
        "dummy_api_key",
        "gemini_api_key",
        "replace_with_actual_api_key",
        "replace_with_actual_gemini_api_key",
        "replace-me",
        "your_api_key_here",
        "sk-your-key-here",
    }

    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent
        if load_dotenv:
            load_dotenv(project_root / ".env")
            load_dotenv(Path(__file__).resolve().parent / ".env")

        self.enabled = os.getenv("AI_EVALUATOR_ENABLED", "true").lower() in {
            "1", "true", "yes", "on"
        }
        self.provider = os.getenv("AI_PROVIDER", "gemini")
        self.api_key = (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("AI_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or ""
        )
        self.api_url = os.getenv(
            "AI_API_URL",
            "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        )
        self.model = os.getenv("AI_MODEL", "gemini-3-flash-preview")
        self.timeout_seconds = int(os.getenv("AI_TIMEOUT_SECONDS", "20"))
        self.key_name = os.getenv("GEMINI_KEY_NAME", "")
        self.project_name = os.getenv("GEMINI_PROJECT_NAME", "")
        self.project_number = os.getenv("GEMINI_PROJECT_NUMBER", "")
        self.last_error = ""

    def is_configured(self) -> bool:
        key = self.api_key.strip()
        return bool(self.enabled and key and key.lower() not in self.DUMMY_KEYS)

    def status(self) -> Dict:
        return {
            "enabled": self.enabled,
            "configured": self.is_configured(),
            "provider": self.provider,
            "model": self.model,
            "api_url": self.api_url,
            "key_name_set": bool(self.key_name.strip()),
            "project_name_set": bool(self.project_name.strip()),
            "project_number_set": bool(self.project_number.strip()),
            "endpoint_type": self._endpoint_type(),
            "last_error": self.last_error,
        }

    def evaluate_answer(
        self,
        *,
        question: str,
        answer: str,
        expected_keywords: List[str],
        category: str,
        difficulty: str,
        job_role: str,
        local_analysis: Dict,
    ) -> Optional[Dict]:
        """Return normalized AI scores/feedback, or None when unavailable."""
        if not self.is_configured():
            self.last_error = "AI evaluator is not configured with a real API key."
            return None

        if not answer or not answer.strip():
            self.last_error = "Skipped AI evaluation for empty answer."
            return None

        prompt_payload = {
            "question": question,
            "answer": answer,
            "expected_keywords": expected_keywords,
            "category": category,
            "difficulty": difficulty,
            "job_role": job_role,
            "project_context": {
                "key_name": self.key_name,
                "project_name": self.project_name,
                "project_number": self.project_number,
            },
            "local_analysis": {
                "word_count": local_analysis.get("word_count", 0),
                "sentence_count": local_analysis.get("sentence_count", 0),
                "quality_prediction": local_analysis.get("quality_prediction", ""),
                "technical_terms": local_analysis.get("technical_terms", []),
            },
        }

        try:
            raw_text = self._post_evaluation_request(prompt_payload)
            parsed = self._parse_model_json(raw_text)
            normalized = self._normalize_result(parsed, question, expected_keywords)
            self.last_error = ""
            return normalized
        except Exception as exc:
            self.last_error = str(exc)
            return None

    def _post_evaluation_request(self, prompt_payload: Dict) -> str:
        if self._endpoint_type() == "gemini_native":
            return self._post_gemini_native_json(prompt_payload)
        return self._post_openai_compatible_json(prompt_payload)

    def _endpoint_type(self) -> str:
        url = self.api_url.lower()
        if "generatecontent" in url and "openai" not in url:
            return "gemini_native"
        return "openai_compatible"

    def _post_openai_compatible_json(self, prompt_payload: Dict) -> str:
        request_body = {
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": self._system_prompt(),
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt_payload, ensure_ascii=True),
                },
            ],
        }
        response_json = self._post_json(request_body, auth_mode="bearer")
        try:
            return response_json["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("AI API response did not contain message content.") from exc

    def _post_gemini_native_json(self, prompt_payload: Dict) -> str:
        request_body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": (
                                self._system_prompt()
                                + "\n\nEvaluate this answer and return JSON only:\n"
                                + json.dumps(prompt_payload, ensure_ascii=True)
                            )
                        }
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
            },
        }

        response_json = self._post_json(request_body, auth_mode="gemini_key")
        try:
            parts = response_json["candidates"][0]["content"]["parts"]
            return "".join(str(part.get("text", "")) for part in parts)
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Gemini response did not contain generated text.") from exc

    def _post_json(self, payload: Dict, auth_mode: str) -> Dict:
        data = json.dumps(payload).encode("utf-8")
        api_url = self._effective_api_url()
        headers = {"Content-Type": "application/json"}

        if auth_mode == "gemini_key":
            headers["x-goog-api-key"] = self.api_key
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = urllib.request.Request(
            api_url,
            data=data,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                response_data = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"AI API HTTP {exc.code}: {detail[:500]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"AI API connection failed: {exc.reason}") from exc

        return json.loads(response_data)

    def _effective_api_url(self) -> str:
        """Keep Gemini native URL model aligned with AI_MODEL from .env."""
        if self._endpoint_type() != "gemini_native":
            return self.api_url

        return re.sub(
            r"/models/[^/:]+:generateContent",
            f"/models/{urllib.parse.quote(self.model)}:generateContent",
            self.api_url,
        )

    def _parse_model_json(self, raw_text: str) -> Dict:
        text = (raw_text or "").strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
            text = re.sub(r"```$", "", text).strip()

        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise RuntimeError("AI evaluator did not return JSON.")

        return json.loads(text[start:end + 1])

    def _normalize_result(
        self,
        result: Dict,
        question: str,
        expected_keywords: List[str],
    ) -> Dict:
        score = self._clamp_int(result.get("score", 0), 0, 100)
        is_correct = result.get("is_correct")
        if not isinstance(is_correct, bool):
            is_correct = score >= 60

        verdict = "Correct" if is_correct else "Wrong"
        matched = self._string_list(result.get("matched_concepts", []))
        missing = self._string_list(result.get("missing_concepts", []))
        strengths = self._string_list(result.get("strengths", []))
        weaknesses = self._string_list(result.get("weaknesses", []))
        improvements = self._string_list(
            result.get("improvement_suggestions", result.get("improvements", []))
        )
        decision_reasons = self._string_list(result.get("decision_reasons", []))

        feedback_text = str(result.get("feedback", "")).strip()
        if not feedback_text:
            feedback_text = (
                "Correct answer." if is_correct
                else "Wrong answer. Review the missing concepts."
            )
        if not feedback_text.lower().startswith(("correct", "wrong")):
            feedback_text = f"{verdict}. {feedback_text}"

        technical_accuracy = str(
            result.get(
                "technical_accuracy",
                f"AI verdict: {verdict}. Score: {score}/100.",
            )
        ).strip()

        if is_correct and score < 60:
            score = 60
        if not is_correct and score > 59:
            score = 59

        scores = {
            "content_score": self._clamp_int(result.get("content_score", score), 0, 100),
            "grammar_score": self._clamp_int(result.get("grammar_score", 75), 0, 100),
            "technical_score": self._clamp_int(result.get("technical_score", score), 0, 100),
            "confidence_score": self._clamp_int(result.get("confidence_score", 70), 0, 100),
            "total_score": score,
            "grade": self._get_grade(score),
            "low_effort": False,
            "found_keywords": matched,
            "missing_keywords": missing,
            "matched_keyword_count": len(matched),
            "expected_keyword_count": len(expected_keywords or []),
            "required_keyword_count": 0,
            "match_percentage": round((len(matched) / len(expected_keywords) * 100), 2) if expected_keywords else 0,
            "concept_evidence": result.get("concept_evidence", {}),
            "contradictions": self._string_list(result.get("contradictions", [])),
            "full_form_match": bool(result.get("full_form_match", False)),
            "full_form_matches": result.get("full_form_matches", []),
            "is_correct": is_correct,
            "verdict": verdict.lower(),
            "answer_status": verdict,
            "decision_reasons": decision_reasons or [feedback_text],
            "verdict_reason": " ".join(decision_reasons) if decision_reasons else feedback_text,
            "evaluation_source": "ai",
            "ai_model": self.model,
        }

        feedback = {
            "overall": feedback_text,
            "verdict": verdict.lower(),
            "answer_status": verdict,
            "is_correct": is_correct,
            "strengths": strengths or (matched[:3] if matched else []),
            "weaknesses": weaknesses,
            "improvements": improvements,
            "technical_accuracy": technical_accuracy,
            "grammar_suggestions": str(result.get("grammar_suggestions", "")).strip()
            or "Grammar was not the main focus of this evaluation.",
            "next_steps": str(result.get("next_steps", "")).strip()
            or ("Move to the next question." if is_correct else "Review and retry this topic."),
            "missing_concepts": missing,
            "found_concepts": matched,
            "accuracy_report": {
                "question": question,
                "required_concepts": expected_keywords or [],
                "matched_concepts": matched,
                "missing_concepts": missing,
                "matched_count": len(matched),
                "required_to_pass": 0,
                "expected_count": len(expected_keywords or []),
                "match_percentage": scores["match_percentage"],
                "decision_reasons": scores["decision_reasons"],
                "concept_evidence": scores["concept_evidence"],
                "evaluation_source": "ai",
                "ai_model": self.model,
            },
        }

        return {
            "scores": scores,
            "feedback": feedback,
            "raw_result": result,
        }

    def _system_prompt(self) -> str:
        return (
            "You are a strict but fair technical interview answer evaluator. "
            "Evaluate semantic correctness, not exact keyword matching. "
            "Accept correct synonyms, acronyms, full forms, and equivalent explanations. "
            "For questions like 'What is an API?' or 'Explain MVC', a correct full form "
            "alone can be marked correct but brief. For process/deep questions like "
            "'How do you perform API testing?' or 'How do you prevent SQL injection?', "
            "a full form alone is not enough. "
            "Mark answers with technical contradictions as wrong even if keywords appear. "
            "Return only valid JSON with these keys: "
            "is_correct (boolean), score (0-100 integer), matched_concepts (array), "
            "missing_concepts (array), feedback (string), strengths (array), "
            "weaknesses (array), improvement_suggestions (array), technical_accuracy "
            "(string), grammar_suggestions (string), next_steps (string), "
            "decision_reasons (array), contradictions (array), full_form_match (boolean)."
        )

    def _string_list(self, value) -> List[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    def _clamp_int(self, value, low: int, high: int) -> int:
        try:
            number = int(round(float(value)))
        except (TypeError, ValueError):
            number = low
        return max(low, min(high, number))

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

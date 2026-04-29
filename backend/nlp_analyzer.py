# NLP Analyzer Module
# Analyzes user answers using NLP techniques

import os
import re
from typing import Dict, List, Optional
from collections import Counter

try:
    import joblib
except ImportError:
    joblib = None

try:
    import spacy
except ImportError:
    spacy = None

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
except ImportError:
    nltk = None

# Load spaCy model
if spacy:
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        nlp = None
else:
    nlp = None

# Initialize NLTK components
if nltk:
    try:
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
    except:
        stop_words = set()
        lemmatizer = None
else:
    stop_words = set()
    lemmatizer = None


class NLPAnalyzer:
    """Analyze user answers using NLP techniques"""
    
    # Technical keywords for different categories
    TECHNICAL_KEYWORDS = {
        "programming": [
            "variable", "function", "class", "object", "method", "loop",
            "condition", "array", "list", "dictionary", "string", "integer",
            "boolean", "inheritance", "polymorphism", "encapsulation",
            "abstraction", "interface", "abstract", "constructor", "destructor"
        ],
        "web_development": [
            "html", "css", "javascript", "react", "angular", "vue",
            "node", "express", "api", "rest", "json", "xml", "http",
            "request", "response", "server", "client", "browser", "domain"
        ],
        "database": [
            "sql", "mysql", "postgresql", "mongodb", "query", "table",
            "database", "schema", "index", "primary key", "foreign key",
            "join", "select", "insert", "update", "delete", "normalize"
        ],
        "data_science": [
            "machine learning", "deep learning", "model", "algorithm",
            "training", "testing", "accuracy", "precision", "recall",
            "f1 score", "confusion matrix", "overfitting", "underfitting",
            "feature", "label", "dataset", "neural network", "tensorflow"
        ],
        "software_testing": [
            "test", "testing", "unit", "integration", "system", "acceptance",
            "bug", "defect", "test case", "test plan", "automation",
            "selenium", "junit", "pytest", "manual testing", "regression"
        ],
        "oop": [
            "class", "object", "inheritance", "polymorphism", "encapsulation",
            "abstraction", "constructor", "method", "property", "static",
            "abstract", "interface", "override", "overload"
        ]
    }
    
    def __init__(self):
        self.analysis_history = []
        
        # Attempt to load ML topic classifier
        self.topic_classifier = None
        if joblib:
            try:
                model_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), 
                    "models", 
                    "topic_classifier.joblib"
                )
                if os.path.exists(model_path):
                    self.topic_classifier = joblib.load(model_path)
            except Exception as e:
                print(f"Warning: Failed to load topic classifier: {e}")
    
    def analyze_answer(self, answer: str) -> Dict:
        """Main method to analyze a user's answer"""
        if not answer or not answer.strip():
            return self._empty_analysis()
        
        answer = answer.strip()
        
        # Perform various analyses
        analysis = {
            "word_count": self._count_words(answer),
            "sentence_count": self._count_sentences(answer),
            "avg_word_length": self._avg_word_length(answer),
            "technical_terms": self._extract_technical_terms(answer),
            "key_phrases": self._extract_key_phrases(answer),
            "clarity_score": self._calculate_clarity(answer),
            "completeness": self._assess_completeness(answer),
            "category": self._categorize_answer(answer),
            "sentiment": self._analyze_sentiment(answer),
            "grammar_quality": self._assess_grammar(answer)
        }
        # Detect explicit "I don't know" / very short / low-effort responses
        low_effort, reason = self._detect_low_effort(answer)
        analysis["low_effort"] = low_effort
        analysis["low_effort_reason"] = reason
        
        self.analysis_history.append(analysis)
        return analysis
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis for empty answers"""
        return {
            "word_count": 0,
            "sentence_count": 0,
            "avg_word_length": 0,
            "technical_terms": [],
            "key_phrases": [],
            "clarity_score": 0,
            "completeness": 0,
            "category": "unknown",
            "sentiment": "neutral",
            "grammar_quality": 0
        }
    
    def _count_words(self, text: str) -> int:
        """Count words in text"""
        if nltk:
            try:
                return len(word_tokenize(text))
            except:
                pass
        return len(text.split())
    
    def _count_sentences(self, text: str) -> int:
        """Count sentences in text"""
        if nltk:
            try:
                return len(sent_tokenize(text))
            except:
                pass
        # Fallback: split on sentence-ending punctuation and ignore empty segments
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        return len(sentences)
    
    def _avg_word_length(self, text: str) -> float:
        """Calculate average word length"""
        words = text.split()
        if not words:
            return 0
        return sum(len(word) for word in words) / len(words)
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms from answer"""
        text_lower = text.lower()
        found_terms = []
        
        for category, terms in self.TECHNICAL_KEYWORDS.items():
            for term in terms:
                if term.lower() in text_lower:
                    found_terms.append(term)
        
        return list(set(found_terms))
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases using NLP"""
        phrases = []
        
        if nlp:
            doc = nlp(text)
            # Extract noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 3:
                    phrases.append(chunk.text.lower())
        else:
            # Fallback: extract common bigram phrases (words only)
            words = re.findall(r"\b\w+\b", text.lower())
            for i in range(len(words) - 1):
                phrases.append(f"{words[i]} {words[i+1]}")
        
        return phrases[:10]  # Limit to 10 phrases
    
    def _calculate_clarity(self, text: str) -> int:
        """Calculate clarity score (0-100)"""
        score = 100
        
        # Penalize for very short answers
        word_count = self._count_words(text)
        if word_count < 10:
            score -= 30
        elif word_count < 20:
            score -= 15
        
        # Penalize for very long sentences
        sentences = self._count_sentences(text)
        if sentences > 0:
            avg_words_per_sentence = word_count / sentences
            if avg_words_per_sentence > 30:
                score -= 20
        
        # Penalize for excessive repetition
        words = text.lower().split()
        if len(words) > 5:
            word_freq = Counter(words)
            max_freq = max(word_freq.values())
            if max_freq / len(words) > 0.3:
                score -= 15
        
        return max(0, min(100, score))
    
    def _assess_completeness(self, text: str) -> int:
        """Assess answer completeness (0-100)"""
        score = 50  # Base score
        
        word_count = self._count_words(text)
        
        # Good answers should have at least 30 words
        if word_count >= 30:
            score += 20
        if word_count >= 50:
            score += 15
        if word_count >= 100:
            score += 10
        
        # Check for technical terms
        technical_terms = self._extract_technical_terms(text)
        score += min(20, len(technical_terms) * 5)
        
        # Check for structure (multiple sentences)
        if self._count_sentences(text) >= 3:
            score += 10
        
        return max(0, min(100, score))
    
    def _categorize_answer(self, text: str) -> str:
        """Categorize the answer topic"""
        
        # Use ML model if available
        if self.topic_classifier:
            try:
                prediction = self.topic_classifier.predict([text])[0]
                return prediction
            except Exception as e:
                print(f"ML categorization failed: {e}. Falling back to rule-based.")
        
        # Fallback rule-based approach
        text_lower = text.lower()
        
        # Check for category keywords
        for category, keywords in self.TECHNICAL_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches >= 2:
                return category
        
        return "general"
    
    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis"""
        positive_words = ["good", "great", "excellent", "better", "understand", "know"]
        negative_words = ["bad", "poor", "difficult", "confused", "don't know", "not sure"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"
    
    def _assess_grammar(self, text: str) -> int:
        """Basic grammar assessment (0-100)"""
        score = 80  # Base score
        
        # Check for common grammar issues
        issues = 0
        
        # Check for double spaces
        if "  " in text:
            issues += 1
        
        # Check for missing capitalization at start
        if text and not text[0].isupper():
            issues += 1
        
        # Check for proper punctuation
        if not any(p in text for p in [".", "!", "?"]):
            issues += 5
            score -= 10
        
        # Check for very long words (possible typos)
        words = text.split()
        long_words = sum(1 for word in words if len(word) > 20)
        if long_words > 2:
            issues += long_words
        
        score -= issues * 5
        return max(0, min(100, score))

    def _detect_low_effort(self, text: str) -> (bool, str):
        """Detect low-effort or explicit unknown responses.

        Returns (is_low_effort, reason)
        """
        if not text:
            return True, "empty"

        t = text.lower().strip()

        # Normalize common punctuation variants
        t = t.replace("’", "'").replace("`", "'")

        # Explicit unknown phrases
        explicit_patterns = [
            r"\bi\s*(?:do not|dont|do n't|don't)\s*know\b",
            r"\bno\s*idea\b",
            r"\bnot\s*sure\b",
            r"\bidk\b",
            r"\bcan't\s*say\b",
            r"\bcannot\s*say\b",
            r"\bi\s*(?:do not|dont|don't)\s*remember\b",
            r"\bi\s*have\s*no\s*idea\b",
        ]

        for pat in explicit_patterns:
            if re.search(pat, t):
                return True, "explicit_unknown"

        # Short or single-word answers with no technical terms -> low effort
        wc = self._count_words(text)
        if wc <= 3:
            tech = self._extract_technical_terms(text)
            if not tech:
                return True, "too_short"

        return False, ""
    
    def compare_with_keywords(self, answer: str, expected_keywords: List[str]) -> Dict:
        """Compare answer with expected keywords"""
        answer_lower = answer.lower()
        
        found_keywords = []
        missing_keywords = []
        
        for keyword in expected_keywords:
            if keyword.lower() in answer_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        match_percentage = (len(found_keywords) / len(expected_keywords) * 100) if expected_keywords else 0
        
        return {
            "found": found_keywords,
            "missing": missing_keywords,
            "match_percentage": round(match_percentage, 2),
            "keyword_count": len(found_keywords)
        }
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (simple word overlap)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)


# Standalone function for testing
def analyze_text(text: str) -> Dict:
    """Quick function to analyze text"""
    analyzer = NLPAnalyzer()
    return analyzer.analyze_answer(text)


if __name__ == "__main__":
    # Test the analyzer
    analyzer = NLPAnalyzer()
    test_answer = "Object-oriented programming is a paradigm that uses objects and classes. It includes inheritance, polymorphism, and encapsulation."
    result = analyzer.analyze_answer(test_answer)
    print("Analysis Result:", result)
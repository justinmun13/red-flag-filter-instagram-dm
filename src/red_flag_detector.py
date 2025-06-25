import re
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RedFlag:
    category: str
    pattern: str
    risk_level: RiskLevel
    explanation: str
    confidence: float

class RedFlagDetector:
    def __init__(self):
        self.patterns = self._load_patterns()
        self.ai_prompt = self._create_ai_prompt()
    
    def _load_patterns(self) -> Dict:
        """Load red flag patterns and rules"""
        return {
            "manipulation": {
                "love_bombing": {
                    "patterns": [
                        r"\b(you['\s]re\s+perfect|soulmate|meant\s+to\s+be)\b",
                        r"\b(love\s+you|my\s+everything)\b.*\b(day|week|hour)\b",
                        r"\b(never\s+felt\s+this\s+way|you['\s]re\s+different)\b"
                    ],
                    "risk_level": RiskLevel.MEDIUM,
                    "explanation": "Excessive romantic declarations too early in conversation"
                },
                "guilt_tripping": {
                    "patterns": [
                        r"\b(if\s+you\s+really\s+cared|you\s+don['\s]t\s+care)\b",
                        r"\b(fine\s+whatever|forget\s+it\s+then)\b",
                        r"\b(you['\s]re\s+being\s+mean|why\s+are\s+you\s+ignoring)\b"
                    ],
                    "risk_level": RiskLevel.HIGH,
                    "explanation": "Attempting to manipulate through guilt and emotional pressure"
                }
            },
            "boundary_violations": {
                "persistent_messaging": {
                    "patterns": [
                        r"\b(hello\?+|hey\?+|respond\s+please)\b",
                        r"\b(why\s+aren['\s]t\s+you\s+responding|answer\s+me)\b"
                    ],
                    "risk_level": RiskLevel.HIGH,
                    "explanation": "Not respecting communication boundaries"
                },
                "sexual_content": {
                    "patterns": [
                        r"\b(send\s+pics|nudes|sexy\s+photo)\b",
                        r"\b(what\s+are\s+you\s+wearing|bedroom|naked)\b"
                    ],
                    "risk_level": RiskLevel.HIGH,
                    "explanation": "Inappropriate sexual requests"
                }
            },
            "financial_scams": {
                "money_requests": {
                    "patterns": [
                        r"\b(need\s+money|financial\s+help|emergency)\b",
                        r"\b(send\s+\$|venmo|cashapp|paypal)\b",
                        r"\b(bitcoin|crypto|investment\s+opportunity)\b"
                    ],
                    "risk_level": RiskLevel.CRITICAL,
                    "explanation": "Potential financial scam or money request"
                }
            },
            "controlling_behavior": {
                "personal_info": {
                    "patterns": [
                        r"\b(what['\s]s\s+your\s+address|where\s+do\s+you\s+live)\b",
                        r"\b(send\s+your\s+location|meet\s+me\s+now)\b",
                        r"\b(give\s+me\s+your\s+number|what['\s]s\s+your\s+phone)\b"
                    ],
                    "risk_level": RiskLevel.HIGH,
                    "explanation": "Requesting sensitive personal information too early"
                }
            },
            "aggressive_language": {
                "threats": {
                    "patterns": [
                        r"\b(you['\s]ll\s+regret|i['\s]ll\s+find\s+you)\b",
                        r"\b(bitch|slut|whore)\b",
                        r"\b(kill|hurt|destroy)\b"
                    ],
                    "risk_level": RiskLevel.CRITICAL,
                    "explanation": "Threatening or aggressive language"
                }
            }
        }
    
    def _create_ai_prompt(self) -> str:
        """Create prompt for AI-based analysis"""
        return """
        You are a dating safety expert. Analyze this message for red flags in dating conversations.
        Look for signs of:
        1. Manipulation (love bombing, guilt trips, gaslighting)
        2. Boundary violations (persistence after rejection, inappropriate requests)
        3. Financial scams (money requests, crypto schemes)
        4. Controlling behavior (demanding personal info, excessive possessiveness)
        5. Aggressive language (threats, insults, degrading comments)
        6. Catfishing indicators (inconsistent stories, avoiding verification)
        
        Rate the overall risk level: LOW, MEDIUM, HIGH, or CRITICAL
        Provide specific red flags found and explanations.
        
        Message to analyze: "{message}"
        
        Respond in JSON format:
        {{
            "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
            "red_flags": [
                {{
                    "category": "category_name",
                    "explanation": "specific concern",
                    "confidence": 0.0-1.0
                }}
            ],
            "overall_assessment": "brief explanation",
            "recommended_action": "block|caution|safe_to_continue"
        }}
        """
    
    def analyze_message(self, message: str, sender_info: Dict = None) -> Dict:
        """Analyze a message for red flags"""
        results = {
            "message": message,
            "risk_level": RiskLevel.LOW,
            "red_flags": [],
            "confidence": 0.0,
            "recommendations": []
        }
        
        # Pattern-based detection
        pattern_flags = self._detect_patterns(message.lower())
        results["red_flags"].extend(pattern_flags)
        
        # Context analysis (if sender info available)
        if sender_info:
            context_flags = self._analyze_context(message, sender_info)
            results["red_flags"].extend(context_flags)
        
        # Determine overall risk level
        if results["red_flags"]:
            # Create a mapping for risk level priority
            risk_priority = {
                RiskLevel.LOW: 1,
                RiskLevel.MEDIUM: 2,
                RiskLevel.HIGH: 3,
                RiskLevel.CRITICAL: 4
            }
            
            # Find the highest priority risk level
            highest_priority = max(risk_priority[flag.risk_level] for flag in results["red_flags"])
            
            # Map back to the corresponding RiskLevel
            for level, priority in risk_priority.items():
                if priority == highest_priority:
                    results["risk_level"] = level
                    break
            
            results["confidence"] = sum(flag.confidence for flag in results["red_flags"]) / len(results["red_flags"])
        
        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results["risk_level"], results["red_flags"])
        
        return results
    
    def _detect_patterns(self, message: str) -> List[RedFlag]:
        """Detect red flags using pattern matching"""
        flags = []
        
        for category, subcategories in self.patterns.items():
            for subcategory, data in subcategories.items():
                for pattern in data["patterns"]:
                    if re.search(pattern, message, re.IGNORECASE):
                        flag = RedFlag(
                            category=f"{category}_{subcategory}",
                            pattern=pattern,
                            risk_level=data["risk_level"],
                            explanation=data["explanation"],
                            confidence=0.8
                        )
                        flags.append(flag)
        
        return flags
    
    def _analyze_context(self, message: str, sender_info: Dict) -> List[RedFlag]:
        """Analyze contextual red flags"""
        flags = []
        
        # Check for multiple messages in short time
        if sender_info.get("message_frequency", 0) > 5:
            flags.append(RedFlag(
                category="boundary_violation_spam",
                pattern="multiple_messages",
                risk_level=RiskLevel.MEDIUM,
                explanation="Sending too many messages in short time period",
                confidence=0.7
            ))
        
        # Check for new account
        if sender_info.get("account_age_days", 999) < 7:
            flags.append(RedFlag(
                category="suspicious_account",
                pattern="new_account",
                risk_level=RiskLevel.MEDIUM,
                explanation="Very new account - potential fake profile",
                confidence=0.6
            ))
        
        return flags
    
    def _generate_recommendations(self, risk_level: RiskLevel, flags: List[RedFlag]) -> List[str]:
        """Generate safety recommendations based on analysis"""
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "🚨 BLOCK IMMEDIATELY - This person shows dangerous behavior patterns",
                "📸 Screenshot the conversation for evidence",
                "📞 Consider reporting to Instagram and local authorities if threatened"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "⚠️ PROCEED WITH EXTREME CAUTION",
                "🚫 Do not share personal information",
                "👥 Tell a friend about this interaction",
                "🔒 Consider blocking if behavior continues"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "⚡ BE CAUTIOUS - Some concerning patterns detected",
                "🎭 Keep conversations light and public",
                "🚫 Avoid sharing personal details",
                "👀 Watch for escalating behavior"
            ])
        else:
            recommendations.append("✅ Conversation appears relatively safe, but stay alert")
        
        # Add specific recommendations based on flag categories
        flag_categories = [flag.category for flag in flags]
        
        if any("financial" in cat for cat in flag_categories):
            recommendations.append("💰 NEVER send money to someone you haven't met in person")
        
        if any("manipulation" in cat for cat in flag_categories):
            recommendations.append("🧠 Trust your instincts - manipulation tactics are red flags")
        
        if any("personal_info" in cat for cat in flag_categories):
            recommendations.append("🔐 Keep personal information private until you've met safely")
        
        return recommendations

# Example usage and testing
if __name__ == "__main__":
    detector = RedFlagDetector()
    
    # Test messages
    test_messages = [
        "Hey beautiful, you're perfect! I've never felt this way about anyone. We're soulmates!",
        "Why aren't you responding? If you really cared about me you'd answer.",
        "I need help with an emergency. Can you send me $200 on Venmo?",
        "What's your address? I want to come see you right now.",
        "You're being a bitch. I'll find you and make you regret ignoring me.",
        "Hi! How's your day going? 😊"
    ]
    
    print("🚩 RED FLAG FILTER - TEST RESULTS 🚩\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: {message}")
        result = detector.analyze_message(message)
        
        print(f"Risk Level: {result['risk_level'].value.upper()}")
        print(f"Confidence: {result['confidence']:.2f}")
        
        if result['red_flags']:
            print("Red Flags Found:")
            for flag in result['red_flags']:
                print(f"  - {flag.category}: {flag.explanation}")
        
        print("Recommendations:")
        for rec in result['recommendations']:
            print(f"  {rec}")
        
        print("-" * 50)
#!/usr/bin/env python3
"""
Enhanced Red Flag Detector - Improved Accuracy Version
Combines comprehensive pattern detection with better false positive filtering
"""

import re
import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

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
        """Load comprehensive red flag patterns and rules"""
        return {
            "manipulation": {
                "love_bombing": {
                    "patterns": [
                        r"\b(you['\s]re\s+perfect|soulmate|meant\s+to\s+be)\b",
                        r"\b(love\s+you|my\s+everything)\b.*\b(day|week|hour)\b",
                        r"\b(never\s+felt\s+this\s+way|you['\s]re\s+different)\b",
                        r"\b(you['\s]re\s+special|not\s+like\s+other\s+girls)\b",
                        r"\b(can['\s]t\s+live\s+without\s+you|need\s+you)\b",
                        r"\b(you['\s]re\s+my\s+world|my\s+everything)\b",
                        r"\b(destiny|fate|meant\s+to\s+be\s+together)\b"
                    ],
                    "risk_level": RiskLevel.HIGH,
                    "explanation": "Love bombing - Excessive romantic declarations too early in conversation"
                },
                "guilt_tripping": {
                    "patterns": [
                        r"\b(if\s+you\s+really\s+cared|you\s+don['\s]t\s+care)\b",
                        r"\b(fine\s+whatever|forget\s+it\s+then)\b",
                        r"\b(you['\s]re\s+being\s+mean|why\s+are\s+you\s+ignoring)\b",
                        r"\b(i\s+thought\s+you\s+were\s+different|guess\s+i\s+was\s+wrong)\b"
                    ],
                    "risk_level": RiskLevel.HIGH,
                    "explanation": "Guilt tripping - Attempting to manipulate through guilt and emotional pressure"
                },
                "gaslighting": {
                    "patterns": [
                        r"\b(you['\s]re\s+overreacting|being\s+dramatic)\b",
                        r"\b(that\s+never\s+happened|you['\s]re\s+imagining)\b",
                        r"\b(you['\s]re\s+too\s+sensitive|crazy)\b",
                        r"\b(i\s+never\s+said\s+that|you\s+misunderstood)\b",
                        r"\b(you['\s]re\s+being\s+paranoid|insecure)\b"
                    ],
                    "risk_level": RiskLevel.HIGH,
                    "explanation": "Gaslighting - Attempting to make you question your own reality or feelings"
                }
            },
            "boundary_violations": {
                "persistent_messaging": {
                    "patterns": [
                        r"\b(hello\?+|hey\?+|respond\s+please)\b",
                        r"\b(why\s+aren['\s]t\s+you\s+responding|answer\s+me)\b",
                        r"\b(ignoring\s+me|reply\s+to\s+me)\b"
                    ],
                    "risk_level": RiskLevel.MEDIUM,
                    "explanation": "Persistent messaging - Not respecting communication boundaries"
                },
                "sexual_content": {
                    "patterns": [
                        r"\b(send\s+pics|nudes|sexy\s+photo)\b",
                        r"\b(what\s+are\s+you\s+wearing|bedroom|naked)\b",
                        r"\b(show\s+me|let\s+me\s+see)\b.*\b(body|pics)\b",
                        r"\b(you['\s]re\s+so\s+sexy|hot\s+body)\b",
                        r"\b(turn\s+me\s+on|getting\s+hard)\b"
                    ],
                    "risk_level": RiskLevel.HIGH,
                    "explanation": "Sexual pressure - Inappropriate sexual requests or comments"
                }
            },
            "financial_scams": {
                "money_requests": {
                    "patterns": [
                        r"\b(need\s+money|financial\s+help|emergency.*money)\b",
                        r"\b(send\s+\$|venmo|cashapp|paypal|zelle)\b",
                        r"\b(bitcoin|crypto|investment\s+opportunity)\b",
                        r"\b(stranded|stuck|trapped).*\b(money|cash|help|funds)\b",
                        r"\b(lend|loan|borrow).*\b(money|cash|\$)\b",
                        r"\b(desperate|urgent|immediate).*\b(money|cash|help)\b",
                        r"\b(wire\s+transfer|money\s+order|bank\s+transfer)\b"
                    ],
                    "risk_level": RiskLevel.CRITICAL,
                    "explanation": "Financial scam - Money request detected (major red flag)"
                },
                "sophisticated_scams": {
                    "patterns": [
                        r"\b(stranded|stuck|trapped|lost).*\b(island|country|airport|hotel)\b",
                        r"\b(promise.*repay|guarantee.*return|pay.*back)\b",
                        r"\b(temporary.*loan|short.*term|just.*until)\b",
                        r"\b(trust.*me|you.*know.*me|good.*for.*it)\b.*\b(money|loan)\b",
                        r"\b(family.*emergency|medical.*bill|travel.*problems)\b",
                        r"\b(inheritance|lottery|prize).*\b(fee|tax|processing)\b"
                    ],
                    "risk_level": RiskLevel.CRITICAL,
                    "explanation": "Sophisticated financial scam - Elaborate story with money request"
                }
            },
            "controlling_behavior": {
                "personal_info": {
                    "patterns": [
                        r"\b(what['\s]s\s+your\s+address|where\s+do\s+you\s+live)\b",
                        r"\b(send\s+your\s+location|meet\s+me\s+now)\b",
                        r"\b(give\s+me\s+your\s+number|what['\s]s\s+your\s+phone)\b",
                        r"\b(where\s+do\s+you\s+work|what\s+school)\b"
                    ],
                    "risk_level": RiskLevel.HIGH,
                    "explanation": "Personal information fishing - Requesting sensitive details too early"
                },
                "isolation": {
                    "patterns": [
                        r"\b(don['\s]t\s+tell\s+anyone|keep\s+this\s+between\s+us)\b",
                        r"\b(your\s+friends\s+don['\s]t\s+understand|wouldn['\s]t\s+get\s+it)\b",
                        r"\b(your\s+family\s+wouldn['\s]t\s+approve|won['\s]t\s+like)\b",
                        r"\b(nobody\s+gets\s+us|they['\s]re\s+jealous)\b",
                        r"\b(delete\s+this\s+conversation|clear\s+your\s+history)\b"
                    ],
                    "risk_level": RiskLevel.HIGH,
                    "explanation": "Isolation tactics - Attempting to separate you from support network"
                }
            },
            "pressure_tactics": {
                "urgency": {
                    "patterns": [
                        r"\b(right\s+now|immediately|urgent|asap)\b",
                        r"\b(can['\s]t\s+wait|need\s+to\s+know\s+now)\b",
                        r"\b(limited\s+time|act\s+fast|hurry)\b",
                        r"\b(before\s+it['\s]s\s+too\s+late|last\s+chance)\b",
                        r"\b(decide\s+now|yes\s+or\s+no)\b"
                    ],
                    "risk_level": RiskLevel.MEDIUM,
                    "explanation": "Pressure tactics - Creating false urgency to bypass rational thinking"
                }
            },
            "aggressive_language": {
                "threats": {
                    "patterns": [
                        r"\b(you['\s]ll\s+regret|i['\s]ll\s+find\s+you)\b",
                        r"\b(bitch|slut|whore|cunt)\b",
                        r"\b(i['\s]ll\s+kill\s+you|i['\s]ll\s+hurt\s+you)\b",
                        r"\b(you['\s]re\s+dead|i['\s]ll\s+destroy\s+you)\b",
                        r"\b(watch\s+your\s+back|you['\s]ll\s+be\s+sorry)\b"
                    ],
                    "risk_level": RiskLevel.CRITICAL,
                    "explanation": "Direct threats - Aggressive or threatening language toward recipient"
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
    
    def analyze_message(self, message: str, sender_info: Dict = None) -> Dict[str, Any]:
        """
        Analyze a message for red flags
        
        Args:
            message: The message text to analyze
            sender_info: Optional context about the sender
            
        Returns:
            Dict containing analysis results
        """
        if not message or not isinstance(message, str):
            return {
                'risk_level': RiskLevel.LOW,
                'red_flags': [],
                'recommendations': [],
                'confidence': 0.0,
                'message_analyzed': ""
            }
        
        results = {
            "message_analyzed": message[:100] + "..." if len(message) > 100 else message,
            "risk_level": RiskLevel.LOW,
            "red_flags": [],
            "confidence": 0.0,
            "recommendations": []
        }
        
        try:
            # Pattern-based detection
            pattern_flags = self._detect_patterns(message.lower())
            if pattern_flags:  # Only extend if not None/empty
                results["red_flags"].extend(pattern_flags)
            
            # Advanced financial pattern detection
            advanced_flags = self._analyze_advanced_financial_patterns(message.lower())
            if advanced_flags:  # Only extend if not None/empty
                results["red_flags"].extend(advanced_flags)
            
            # Context analysis (if sender info available)
            if sender_info:
                context_flags = self._analyze_context(message, sender_info)
                if context_flags:  # Only extend if not None/empty
                    results["red_flags"].extend(context_flags)
            
            # Filter false positives - IMPROVED VERSION
            results["red_flags"] = self._filter_false_positives(message, results["red_flags"])
            
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
                
                # Calculate confidence as average of all flags
                results["confidence"] = sum(flag.confidence for flag in results["red_flags"]) / len(results["red_flags"])
            
            # Generate recommendations
            results["recommendations"] = self._generate_recommendations(results["risk_level"], results["red_flags"])
            
        except Exception as e:
            print(f"Error in analyze_message: {e}")
            # Return safe defaults on error
            results["risk_level"] = RiskLevel.LOW
            results["red_flags"] = []
            results["confidence"] = 0.0
            results["recommendations"] = ["Analysis error occurred - exercise caution"]
        
        return results
    
    def _detect_patterns(self, message: str) -> List[RedFlag]:
        """Detect red flags using pattern matching"""
        flags = []
        
        try:
            # Standard pattern detection
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
                            break  # Only add one flag per subcategory to avoid duplicates
        except Exception as e:
            print(f"Error in _detect_patterns: {e}")
        
        return flags
    
    def _analyze_advanced_financial_patterns(self, message: str) -> List[RedFlag]:
        """Analyze advanced financial scam patterns with sophisticated stories"""
        flags = []
        
        try:
            message_lower = message.lower()
            
            # Advanced pattern: Stranded/stuck story + money request
            stranded_indicators = ['stranded', 'stuck', 'trapped', 'lost', 'can\'t get home', 'need to get back']
            money_indicators = ['money', 'cash', 'funds', 'help', 'loan', 'borrow', 'lend', '$']
            repayment_indicators = ['pay back', 'repay', 'return', 'guarantee', 'promise', 'when i get back']
            
            has_stranded = any(indicator in message_lower for indicator in stranded_indicators)
            has_money = any(indicator in message_lower for indicator in money_indicators)
            has_repayment = any(indicator in message_lower for indicator in repayment_indicators)
            
            if has_stranded and has_money:
                confidence = 0.95 if has_repayment else 0.9
                flags.append(RedFlag(
                    category="financial_scam_stranded",
                    pattern="stranded_money_combination",
                    risk_level=RiskLevel.CRITICAL,
                    explanation="Stranded/stuck story combined with money request - classic advance fee scam",
                    confidence=confidence
                ))
            
            # Advanced pattern: Future repayment promises (often false)
            future_promises = ['when i get back', 'as soon as', 'i promise', 'i guarantee', 'you know i\'m good for it']
            if has_money and any(promise in message_lower for promise in future_promises):
                flags.append(RedFlag(
                    category="financial_scam_promise",
                    pattern="money_with_future_promise",
                    risk_level=RiskLevel.CRITICAL,
                    explanation="Money request with future repayment promise - high risk of non-repayment",
                    confidence=0.9
                ))
            
            # Advanced pattern: Urgency + personal connection exploitation
            urgency_words = ['urgent', 'immediate', 'asap', 'right now', 'today', 'desperate']
            personal_appeals = ['you know me', 'we\'re friends', 'trust me', 'you\'re the only one']
            
            has_urgency = any(word in message_lower for word in urgency_words)
            has_personal = any(appeal in message_lower for appeal in personal_appeals)
            
            if has_money and has_urgency and has_personal:
                flags.append(RedFlag(
                    category="financial_scam_manipulation",
                    pattern="urgent_personal_money_request",
                    risk_level=RiskLevel.CRITICAL,
                    explanation="Combines urgency, personal connection, and money request - manipulation tactic",
                    confidence=0.95
                ))
                
        except Exception as e:
            print(f"Error in _analyze_advanced_financial_patterns: {e}")
        
        return flags
    
    def _filter_false_positives(self, message: str, flags: List[RedFlag]) -> List[RedFlag]:
        """Enhanced false positive filtering with better context awareness"""
        filtered_flags = []
        
        try:
            message_lower = message.lower()
            
            for flag in flags:
                is_false_positive = False
                
                # Enhanced filtering for physical injury/pain mentions
                if 'hurt' in flag.category.lower() or 'threat' in flag.category.lower():
                    innocent_contexts = [
                        'hurt my back', 'hurt myself', 'hurt his back', 'hurt her back',
                        'back hurts', 'back pain', 'hurt my knee', 'hurt my ankle',
                        'workout hurt', 'exercise hurt', 'gym hurt', 'pulled muscle',
                        'sore', 'injured', 'sprained', 'twisted', 'strained',
                        'physical therapy', 'therapist said', 'doctor said'
                    ]
                    
                    if any(context in message_lower for context in innocent_contexts):
                        is_false_positive = True
                    
                    # Check if it's self-inflicted injury (not threatening others)
                    self_injury_patterns = [
                        r'\b(i|my|myself|me)\s+.*\bhurt\b',
                        r'\bhurt\s+.*\b(my|myself|me)\b',
                        r'\b(his|her|their)\s+.*\bhurt\b'
                    ]
                    
                    if any(re.search(pattern, message_lower) for pattern in self_injury_patterns):
                        is_false_positive = True
                
                # Enhanced filtering for gaming/sports/social contexts
                if any(word in flag.category.lower() for word in ['threat', 'aggressive', 'hurt', 'gaslighting']):
                    friendly_contexts = [
                        # Gaming terms
                        'game', 'gaming', 'play', 'dub', 'win', 'victory', 'match',
                        'brothaa', 'brotha', 'bro', 'king', 'homie', 'buddy', 'dude',
                        'witness', 'witnessed', 'crazy good', 'insane', 'wild',
                        
                        # Sports terms
                        'sports', 'team', 'scored', 'goal', 'touchdown', 'basketball',
                        'football', 'soccer', 'baseball', 'tennis', 'golf',
                        
                        # Social media/content
                        'video', 'reel', 'movie', 'show', 'clip', 'watch', 'saw',
                        'youtube', 'tiktok', 'instagram', 'story', 'post',
                        'funny', 'hilarious', 'lol', 'haha', 'joke', 'meme',
                        
                        # Positive exclamations
                        'awesome', 'amazing', 'congrats', 'congratulations',
                        'glad', 'happy', 'excited', 'stoked'
                    ]
                    
                    if any(context in message_lower for context in friendly_contexts):
                        is_false_positive = True
                
                # Enhanced gaslighting filter - be more specific about what constitutes gaslighting
                if 'gaslighting' in flag.category.lower():
                    # Check if it's actually expressing positive emotions or celebrating
                    positive_contexts = [
                        'glad you', 'happy you', 'awesome that you', 'great that you',
                        'witness', 'see', 'experience', 'enjoy', 'celebrate',
                        'dub', 'win', 'victory', 'success', 'achievement'
                    ]
                    
                    # Check if message contains celebratory language
                    celebratory_words = ['crazy good', 'insane win', 'wild victory', 'amazing', 'awesome']
                    
                    if (any(context in message_lower for context in positive_contexts) or 
                        any(word in message_lower for word in celebratory_words)):
                        is_false_positive = True
                    
                    # Additional check: if the message is clearly about a shared positive experience
                    shared_experience_patterns = [
                        r'\bglad\s+you\s+(got\s+to|could|were\s+able\s+to)\b',
                        r'\bwitness\s+(it|that|the)\b',
                        r'\bsaw\s+(it|that|the)\b.*\b(person|live|firsthand)\b'
                    ]
                    
                    if any(re.search(pattern, message_lower) for pattern in shared_experience_patterns):
                        is_false_positive = True
                
                # Filter based on overall message tone
                if self._is_positive_message_tone(message_lower):
                    # If the overall message tone is positive/celebratory, be more lenient
                    if flag.risk_level == RiskLevel.HIGH and flag.confidence < 0.9:
                        is_false_positive = True
                
                # Only keep flags that aren't false positives
                if not is_false_positive:
                    filtered_flags.append(flag)
                    
        except Exception as e:
            print(f"Error in _filter_false_positives: {e}")
            # If filtering fails, return original flags to be safe
            return flags
        
        return filtered_flags
    
    def _is_positive_message_tone(self, message_lower: str) -> bool:
        """Check if the overall message tone is positive/celebratory"""
        try:
            positive_indicators = [
                'lol', 'haha', '😊', '😄', '🎉', '💪', '👑',
                'awesome', 'amazing', 'great', 'good', 'nice',
                'congrats', 'celebration', 'happy', 'glad',
                'excited', 'stoked', 'pumped', 'thrilled'
            ]
            
            negative_indicators = [
                'angry', 'mad', 'furious', 'hate', 'stupid',
                'idiot', 'kill', 'die', 'hurt', 'destroy',
                'revenge', 'payback', 'sorry', 'regret'
            ]
            
            positive_count = sum(1 for indicator in positive_indicators if indicator in message_lower)
            negative_count = sum(1 for indicator in negative_indicators if indicator in message_lower)
            
            # Consider positive if more positive than negative indicators
            return positive_count > negative_count and positive_count > 0
            
        except Exception:
            return False
    
    def _analyze_context(self, message: str, sender_info: Dict) -> List[RedFlag]:
        """Analyze contextual red flags"""
        flags = []
        
        try:
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
                
        except Exception as e:
            print(f"Error in _analyze_context: {e}")
        
        return flags
    
    def _generate_recommendations(self, risk_level: RiskLevel, flags: List[RedFlag]) -> List[str]:
        """Generate safety recommendations based on analysis"""
        recommendations = []
        
        try:
            if risk_level == RiskLevel.CRITICAL:
                recommendations.extend([
                    "🚨 BLOCK IMMEDIATELY - This person shows dangerous behavior patterns",
                    "📸 Screenshot the conversation for evidence",
                    "📞 Consider reporting to Instagram and local authorities if threatened",
                    "💰 NEVER send money to someone you've only met online"
                ])
            elif risk_level == RiskLevel.HIGH:
                recommendations.extend([
                    "⚠️ PROCEED WITH EXTREME CAUTION",
                    "🚫 Do not share personal information",
                    "👥 Tell a trusted friend about this interaction",
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
            
            if any("sexual" in cat for cat in flag_categories):
                recommendations.append("🚫 You're not obligated to send photos or engage sexually")
                
        except Exception as e:
            print(f"Error in _generate_recommendations: {e}")
            recommendations = ["Analysis error - exercise general caution"]
        
        return recommendations

# Test function
def test_detector():
    """Test the enhanced red flag detector"""
    detector = RedFlagDetector()
    
    test_messages = [
        "Hey! How's your day going? 😊",
        "You're so different from other girls, I usually don't do this but I love you",
        "Why aren't you responding? If you really cared about me you'd answer right now",
        "I'm stranded at the airport and need $300 for a flight home. I promise I'll pay you back",
        "Send me some pics, what are you wearing? You're so sexy",
        "Don't tell anyone about us, your friends wouldn't understand our connection",
        "You're being a bitch. I'll find you and make you regret ignoring me",
        "What's your address? I want to come see you right now",
        "Crazy dub brothaaaa glad you got to witness it in person",  # Should NOT be flagged
        "But I hurt my back so my physical therapist said don't lift heavy",  # Should NOT be flagged
        "Just tell me when king",  # Should NOT be flagged
        "Miss you too man 🥲"  # Should NOT be flagged
    ]
    
    print("🚩 ENHANCED RED FLAG DETECTOR TEST")
    print("=" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n[Test {i}] Message: \"{message}\"")
        
        try:
            result = detector.analyze_message(message)
            
            risk_level = result['risk_level'].value.upper()
            print(f"Risk Level: {risk_level}")
            print(f"Confidence: {result['confidence']:.2f}")
            
            if result['red_flags']:
                print("Red Flags Found:")
                for flag in result['red_flags']:
                    print(f"  - {flag.category}: {flag.explanation}")
            else:
                print("No red flags detected")
            
            print("Recommendations:")
            for rec in result['recommendations'][:3]:  # Show first 3
                print(f"  {rec}")
                
        except Exception as e:
            print(f"Error testing message: {e}")
        
        print("-" * 60)
    
    print("\n✅ Enhanced detector test complete!")

if __name__ == "__main__":
    test_detector()
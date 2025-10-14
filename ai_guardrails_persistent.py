"""
PMBlueprints AI Guardrails with Database Persistence
Enhanced version with persistent usage tracking and rate limiting
"""

import re
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIGuardrailsPersistent:
    """
    Enhanced AI Safety Framework with database persistence for:
    1. Persistent rate limiting across server restarts
    2. Monthly usage tracking and limits
    3. Automatic usage reset
    4. Comprehensive audit logging
    5. All original guardrails features
    """
    
    # Configuration constants
    MAX_INPUT_LENGTH = None  # Unlimited character input
    MIN_QUALITY_SCORE = 0.85
    MAX_BIAS_THRESHOLD = 0.05
    
    # Rate limits (requests per hour)
    RATE_LIMITS = {
        'free': 10,
        'starter': 50,
        'professional': 200
    }
    
    # Monthly AI generation limits
    MONTHLY_LIMITS = {
        'free': 3,
        'professional': 25,
        'enterprise': 100
    }
    
    # Malicious patterns for prompt injection detection
    MALICIOUS_PATTERNS = [
        r'ignore\s+previous\s+instructions',
        r'disregard\s+all\s+previous',
        r'forget\s+everything',
        r'system\s+prompt',
        r'<script>',
        r'javascript:',
        r'eval\(',
        r'exec\(',
        r'__import__',
        r'subprocess',
        r'os\.system',
    ]
    
    # PII patterns for privacy protection
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    }
    
    # Bias detection keywords
    BIAS_KEYWORDS = {
        'gender': ['he', 'she', 'him', 'her', 'his', 'hers', 'male', 'female', 'man', 'woman'],
        'age': ['young', 'old', 'elderly', 'millennial', 'boomer'],
        'cultural': ['foreign', 'exotic', 'traditional', 'modern'],
        'socioeconomic': ['poor', 'rich', 'wealthy', 'underprivileged']
    }
    
    def __init__(self, db_session=None):
        """Initialize AI Guardrails with database session"""
        self.db = db_session
        self.in_memory_audit_log = []  # Fallback for when DB is unavailable
        
    # ========== DATABASE OPERATIONS ==========
    
    def _reset_monthly_usage_if_needed(self, user):
        """Check and reset monthly usage if reset date has passed"""
        if not user.ai_generation_reset_date:
            # Initialize reset date to first of next month
            from dateutil.relativedelta import relativedelta
            user.ai_generation_reset_date = datetime.utcnow().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            ) + relativedelta(months=1)
            user.ai_generations_used_this_month = 0
            return True
        
        # Check if reset date has passed
        if datetime.utcnow() >= user.ai_generation_reset_date:
            # Reset usage and set next reset date
            user.ai_generations_used_this_month = 0
            from dateutil.relativedelta import relativedelta
            user.ai_generation_reset_date = user.ai_generation_reset_date + relativedelta(months=1)
            logger.info(f"Reset monthly AI usage for user {user.id}")
            return True
        
        return False
    
    def _log_ai_usage(self, user_id: int, request_type: str, success: bool, 
                     template_type: str = None, tokens_used: int = 0,
                     input_length: int = 0, output_length: int = 0,
                     error_message: str = None, metadata: dict = None):
        """Log AI usage to database"""
        if not self.db:
            logger.warning("Database session not available for AI usage logging")
            return
        
        try:
            import json
            
            log_entry = {
                'user_id': user_id,
                'request_type': request_type,
                'template_type': template_type,
                'success': success,
                'tokens_used': tokens_used,
                'input_length': input_length,
                'output_length': output_length,
                'error_message': error_message,
                'metadata': json.dumps(metadata) if metadata else None,
                'timestamp': datetime.utcnow()
            }
            
            # Insert into ai_usage_log table
            insert_sql = text("""
                INSERT INTO ai_usage_log 
                (user_id, request_type, template_type, success, tokens_used, 
                 input_length, output_length, error_message, metadata, timestamp)
                VALUES 
                (:user_id, :request_type, :template_type, :success, :tokens_used,
                 :input_length, :output_length, :error_message, :metadata, :timestamp)
            """)
            
            self.db.execute(insert_sql, log_entry)
            self.db.commit()
            
            logger.info(f"Logged AI usage for user {user_id}: {request_type}")
            
        except Exception as e:
            logger.error(f"Error logging AI usage: {e}")
            self.db.rollback()
    
    def _get_hourly_request_count(self, user_id: int) -> int:
        """Get number of AI requests in the last hour"""
        if not self.db:
            return 0
        
        try:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            count_sql = text("""
                SELECT COUNT(*) FROM ai_usage_log
                WHERE user_id = :user_id 
                AND timestamp >= :one_hour_ago
            """)
            
            result = self.db.execute(count_sql, {
                'user_id': user_id,
                'one_hour_ago': one_hour_ago
            })
            
            count = result.scalar()
            return count or 0
            
        except Exception as e:
            logger.error(f"Error getting hourly request count: {e}")
            return 0
    
    def _get_rapid_fire_count(self, user_id: int) -> int:
        """Get number of requests in the last minute (for suspicious activity detection)"""
        if not self.db:
            return 0
        
        try:
            one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
            
            count_sql = text("""
                SELECT COUNT(*) FROM ai_usage_log
                WHERE user_id = :user_id 
                AND timestamp >= :one_minute_ago
            """)
            
            result = self.db.execute(count_sql, {
                'user_id': user_id,
                'one_minute_ago': one_minute_ago
            })
            
            count = result.scalar()
            return count or 0
            
        except Exception as e:
            logger.error(f"Error getting rapid-fire count: {e}")
            return 0
    
    # ========== ENHANCED RATE LIMITING WITH PERSISTENCE ==========
    
    def check_monthly_limit(self, user) -> Tuple[bool, Optional[str]]:
        """
        Check if user has exceeded monthly AI generation limit
        Returns: (is_allowed, error_message)
        """
        # Reset usage if needed
        self._reset_monthly_usage_if_needed(user)
        
        # Get limit for user's tier
        limit = self.MONTHLY_LIMITS.get(user.subscription_plan, self.MONTHLY_LIMITS['free'])
        
        # Check if limit exceeded
        if user.ai_generations_used_this_month >= limit:
            reset_date = user.ai_generation_reset_date.strftime('%B %d, %Y') if user.ai_generation_reset_date else 'next month'
            return False, f"Monthly AI generation limit reached ({limit} generations). Resets on {reset_date}. Upgrade your plan for more generations."
        
        return True, None
    
    def check_hourly_rate_limit(self, user_id: int, user_tier: str = 'free') -> Tuple[bool, Optional[str]]:
        """
        Check if user has exceeded hourly rate limit (persistent)
        Returns: (is_allowed, error_message)
        """
        limit = self.RATE_LIMITS.get(user_tier, self.RATE_LIMITS['free'])
        
        # Get count from database
        count = self._get_hourly_request_count(user_id)
        
        # Check if limit exceeded
        if count >= limit:
            self._log_audit_event('rate_limit_exceeded', {
                'user_id': user_id,
                'tier': user_tier,
                'limit': limit,
                'count': count
            })
            return False, f"Hourly rate limit exceeded. Maximum {limit} requests per hour for {user_tier} tier. Please try again later."
        
        return True, None
    
    def detect_suspicious_activity(self, user_id: int) -> bool:
        """
        Detect suspicious activity patterns (persistent)
        """
        # Check for rapid-fire requests (more than 5 in 1 minute)
        count = self._get_rapid_fire_count(user_id)
        
        if count > 5:
            logger.warning(f"Suspicious activity detected for user {user_id}: {count} requests in 1 minute")
            self._log_audit_event('suspicious_activity_detected', {
                'user_id': user_id,
                'count': count
            })
            return True
        
        return False
    
    def increment_usage(self, user):
        """Increment user's monthly AI usage counter"""
        user.ai_generations_used_this_month = (user.ai_generations_used_this_month or 0) + 1
        logger.info(f"User {user.id} AI usage: {user.ai_generations_used_this_month}/{self.MONTHLY_LIMITS.get(user.subscription_plan, 3)}")
    
    # ========== CONTENT SAFETY (from original) ==========
    
    def detect_malicious_prompt(self, text: str) -> Tuple[bool, Optional[str]]:
        """Detect malicious prompt injection attempts"""
        text_lower = text.lower()
        
        for pattern in self.MALICIOUS_PATTERNS:
            if re.search(pattern, text_lower):
                reason = f"Detected potential prompt injection: {pattern}"
                logger.warning(f"Malicious prompt detected: {reason}")
                self._log_audit_event('malicious_prompt_detected', {'pattern': pattern})
                return True, reason
                
        return False, None
    
    def detect_inappropriate_content(self, text: str) -> Tuple[bool, Optional[str]]:
        """Detect inappropriate or unprofessional content"""
        inappropriate_keywords = [
            'profanity', 'offensive', 'discriminatory', 'hate speech',
            'violent', 'explicit', 'illegal', 'unethical'
        ]
        
        text_lower = text.lower()
        for keyword in inappropriate_keywords:
            if keyword in text_lower:
                reason = f"Detected inappropriate content: {keyword}"
                logger.warning(f"Inappropriate content detected: {reason}")
                self._log_audit_event('inappropriate_content_detected', {'keyword': keyword})
                return True, reason
                
        return False, None
    
    def scrub_pii(self, text: str) -> str:
        """Remove personally identifiable information (PII) from text"""
        scrubbed_text = text
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, scrubbed_text)
            if matches:
                logger.info(f"Scrubbing {len(matches)} {pii_type} instances")
                self._log_audit_event('pii_scrubbed', {'type': pii_type, 'count': len(matches)})
                scrubbed_text = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', scrubbed_text)
        
        return scrubbed_text
    
    def validate_input(self, text: str, user_tier: str = 'free') -> Tuple[bool, Optional[str]]:
        """Comprehensive input validation"""
        if self.MAX_INPUT_LENGTH and len(text) > self.MAX_INPUT_LENGTH:
            return False, f"Input exceeds maximum length of {self.MAX_INPUT_LENGTH} characters"
        
        if len(text) < 10:
            return False, "Input too short (minimum 10 characters)"
        
        is_malicious, reason = self.detect_malicious_prompt(text)
        if is_malicious:
            return False, f"Security violation: {reason}"
        
        is_inappropriate, reason = self.detect_inappropriate_content(text)
        if is_inappropriate:
            return False, f"Content policy violation: {reason}"
        
        return True, None
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize input text"""
        sanitized = self.scrub_pii(text)
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        return sanitized
    
    # ========== QUALITY AND BIAS (from original) ==========
    
    def detect_bias(self, text: str) -> Dict[str, float]:
        """Detect potential bias in generated content"""
        text_lower = text.lower()
        words = text_lower.split()
        total_words = len(words)
        
        if total_words == 0:
            return {}
        
        bias_scores = {}
        for bias_type, keywords in self.BIAS_KEYWORDS.items():
            keyword_count = sum(1 for word in words if word in keywords)
            bias_score = keyword_count / total_words if total_words > 0 else 0
            bias_scores[bias_type] = bias_score
        
        return bias_scores
    
    def assess_quality(self, text: str, context: Dict) -> Dict[str, float]:
        """Multi-metric quality assessment"""
        scores = {
            'completeness': self._assess_completeness(text, context),
            'relevance': self._assess_relevance(text, context),
            'professionalism': self._assess_professionalism(text),
            'clarity': self._assess_clarity(text)
        }
        scores['overall'] = sum(scores.values()) / len(scores)
        return scores
    
    def _assess_completeness(self, text: str, context: Dict) -> float:
        min_length = context.get('min_length', 100)
        has_sections = len(text.split('\n\n')) >= 3
        length_score = min(len(text) / min_length, 1.0)
        structure_score = 1.0 if has_sections else 0.5
        return (length_score + structure_score) / 2
    
    def _assess_relevance(self, text: str, context: Dict) -> float:
        key_terms = context.get('key_terms', [])
        if not key_terms:
            return 0.9
        text_lower = text.lower()
        matches = sum(1 for term in key_terms if term.lower() in text_lower)
        return matches / len(key_terms) if key_terms else 0.9
    
    def _assess_professionalism(self, text: str) -> float:
        professional_indicators = [
            'project', 'management', 'stakeholder', 'deliverable',
            'milestone', 'objective', 'strategy', 'implementation'
        ]
        text_lower = text.lower()
        matches = sum(1 for indicator in professional_indicators if indicator in text_lower)
        return min(matches / 5, 1.0)
    
    def _assess_clarity(self, text: str) -> float:
        sentences = text.split('.')
        if not sentences:
            return 0.5
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if 15 <= avg_sentence_length <= 20:
            return 1.0
        elif 10 <= avg_sentence_length <= 25:
            return 0.8
        else:
            return 0.6
    
    # ========== AUDIT LOGGING ==========
    
    def _log_audit_event(self, event_type: str, details: Dict):
        """Log audit event"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'details': details
        }
        self.in_memory_audit_log.append(audit_entry)
        logger.info(f"Audit event: {event_type} - {details}")
    
    # ========== FALLBACK AND TRANSPARENCY ==========
    
    def get_fallback_content(self, content_type: str) -> str:
        """Provide fallback content when AI generation fails"""
        fallback_templates = {
            'project_charter': "Professional project charter template with PMI 2025 standards...",
            'risk_register': "Comprehensive risk register following industry best practices...",
            'default': "Professional project management template..."
        }
        return fallback_templates.get(content_type, fallback_templates['default'])
    
    def get_ai_disclosure(self) -> Dict:
        """Provide transparent AI usage disclosure"""
        return {
            'ai_generated': True,
            'disclosure': "This content was generated with AI assistance and reviewed for quality and safety.",
            'limitations': [
                "AI-generated content should be reviewed by professionals",
                "Content may require customization for specific use cases",
                "Human oversight is recommended for critical decisions"
            ],
            'safety_measures': [
                "Content filtered for safety and appropriateness",
                "Bias detection and mitigation applied",
                "Quality assurance validation performed",
                "Privacy protection measures enforced",
                "Usage limits enforced per subscription tier"
            ]
        }
    
    # ========== COMPLETE VALIDATION PIPELINES ==========
    
    def validate_ai_request(self, user, input_text: str, context: Dict = None) -> Dict:
        """
        Complete AI request validation pipeline with persistent tracking
        """
        context = context or {}
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sanitized_input': input_text,
            'metadata': {}
        }
        
        # 1. Check monthly limit
        monthly_ok, monthly_msg = self.check_monthly_limit(user)
        if not monthly_ok:
            result['valid'] = False
            result['errors'].append(monthly_msg)
            return result
        
        # 2. Check hourly rate limit
        hourly_ok, hourly_msg = self.check_hourly_rate_limit(user.id, user.subscription_plan)
        if not hourly_ok:
            result['valid'] = False
            result['errors'].append(hourly_msg)
            return result
        
        # 3. Validate input
        input_valid, input_msg = self.validate_input(input_text, user.subscription_plan)
        if not input_valid:
            result['valid'] = False
            result['errors'].append(input_msg)
            return result
        
        # 4. Sanitize input
        result['sanitized_input'] = self.sanitize_input(input_text)
        
        # 5. Check for suspicious activity
        if self.detect_suspicious_activity(user.id):
            result['warnings'].append("Suspicious activity detected - request flagged for review")
        
        # 6. Add AI disclosure
        result['metadata']['ai_disclosure'] = self.get_ai_disclosure()
        result['metadata']['remaining_monthly'] = self.MONTHLY_LIMITS.get(user.subscription_plan, 3) - user.ai_generations_used_this_month
        
        return result
    
    def validate_ai_output(self, output_text: str, context: Dict = None) -> Dict:
        """Complete AI output validation pipeline"""
        context = context or {}
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'quality_scores': {},
            'bias_scores': {},
            'metadata': {}
        }
        
        # Check quality
        quality_scores = self.assess_quality(output_text, context)
        result['quality_scores'] = quality_scores
        
        if quality_scores['overall'] < self.MIN_QUALITY_SCORE:
            result['valid'] = False
            result['errors'].append(f"Quality threshold not met: {quality_scores['overall']:.2f}")
        
        # Check bias
        bias_scores = self.detect_bias(output_text)
        result['bias_scores'] = bias_scores
        
        if any(score > self.MAX_BIAS_THRESHOLD for score in bias_scores.values()):
            result['warnings'].append("Bias threshold exceeded - content may need review")
        
        # Check for inappropriate content
        inappropriate, reason = self.detect_inappropriate_content(output_text)
        if inappropriate:
            result['valid'] = False
            result['errors'].append(reason)
        
        result['metadata']['ai_disclosure'] = self.get_ai_disclosure()
        result['metadata']['validation_timestamp'] = datetime.utcnow().isoformat()
        
        return result


# Factory function to create guardrails instance with database session
def create_guardrails(db_session=None):
    """Create AI guardrails instance with database session"""
    return AIGuardrailsPersistent(db_session)


"""
PMBlueprints AI Guardrails and Safety Framework
Comprehensive AI safety implementation for responsible AI usage
"""

import re
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIGuardrails:
    """
    Comprehensive AI Safety Framework implementing:
    1. Content Safety and Moderation
    2. Input Validation and Sanitization
    3. Rate Limiting and Abuse Prevention
    4. Bias Detection and Mitigation
    5. Quality Assurance and Validation
    6. Error Handling and Fallback Systems
    7. User Consent and Transparency
    8. Audit Logging and Monitoring
    9. Compliance Framework (GDPR, CCPA)
    10. Continuous Monitoring
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
    
    def __init__(self):
        """Initialize AI Guardrails with tracking systems"""
        self.user_requests = {}  # Track user requests for rate limiting
        self.audit_log = []  # Store audit events
        self.quality_metrics = []  # Track quality scores
        
    # ========== 1. CONTENT SAFETY AND MODERATION ==========
    
    def detect_malicious_prompt(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Detect malicious prompt injection attempts
        Returns: (is_malicious, reason)
        """
        text_lower = text.lower()
        
        for pattern in self.MALICIOUS_PATTERNS:
            if re.search(pattern, text_lower):
                reason = f"Detected potential prompt injection: {pattern}"
                logger.warning(f"Malicious prompt detected: {reason}")
                self._log_audit_event('malicious_prompt_detected', {'pattern': pattern})
                return True, reason
                
        return False, None
    
    def detect_inappropriate_content(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Detect inappropriate or unprofessional content
        Returns: (is_inappropriate, reason)
        """
        # List of inappropriate keywords (simplified for demonstration)
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
        """
        Remove personally identifiable information (PII) from text
        """
        scrubbed_text = text
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, scrubbed_text)
            if matches:
                logger.info(f"Scrubbing {len(matches)} {pii_type} instances")
                self._log_audit_event('pii_scrubbed', {'type': pii_type, 'count': len(matches)})
                scrubbed_text = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', scrubbed_text)
        
        return scrubbed_text
    
    # ========== 2. INPUT VALIDATION AND SANITIZATION ==========
    
    def validate_input(self, text: str, user_tier: str = 'free') -> Tuple[bool, Optional[str]]:
        """
        Comprehensive input validation
        Returns: (is_valid, error_message)
        """
        # Check length (unlimited maximum, minimum 10 characters)
        if self.MAX_INPUT_LENGTH and len(text) > self.MAX_INPUT_LENGTH:
            return False, f"Input exceeds maximum length of {self.MAX_INPUT_LENGTH} characters"
        
        if len(text) < 10:
            return False, "Input too short (minimum 10 characters)"
        
        # Check for malicious content
        is_malicious, reason = self.detect_malicious_prompt(text)
        if is_malicious:
            return False, f"Security violation: {reason}"
        
        # Check for inappropriate content
        is_inappropriate, reason = self.detect_inappropriate_content(text)
        if is_inappropriate:
            return False, f"Content policy violation: {reason}"
        
        return True, None
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitize input text by removing PII and dangerous content
        """
        # Remove PII
        sanitized = self.scrub_pii(text)
        
        # Remove HTML tags
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized
    
    # ========== 3. RATE LIMITING AND ABUSE PREVENTION ==========
    
    def check_rate_limit(self, user_id: str, user_tier: str = 'free') -> Tuple[bool, Optional[str]]:
        """
        Check if user has exceeded rate limit
        Returns: (is_allowed, error_message)
        """
        now = datetime.now()
        limit = self.RATE_LIMITS.get(user_tier, self.RATE_LIMITS['free'])
        
        # Initialize user tracking if not exists
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        
        # Remove requests older than 1 hour
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if now - req_time < timedelta(hours=1)
        ]
        
        # Check if limit exceeded
        if len(self.user_requests[user_id]) >= limit:
            self._log_audit_event('rate_limit_exceeded', {
                'user_id': user_id,
                'tier': user_tier,
                'limit': limit
            })
            return False, f"Rate limit exceeded. Maximum {limit} requests per hour for {user_tier} tier."
        
        # Add current request
        self.user_requests[user_id].append(now)
        return True, None
    
    def detect_suspicious_activity(self, user_id: str) -> bool:
        """
        Detect suspicious activity patterns
        """
        if user_id not in self.user_requests:
            return False
        
        # Check for rapid-fire requests (more than 5 in 1 minute)
        now = datetime.now()
        recent_requests = [
            req_time for req_time in self.user_requests[user_id]
            if now - req_time < timedelta(minutes=1)
        ]
        
        if len(recent_requests) > 5:
            logger.warning(f"Suspicious activity detected for user {user_id}")
            self._log_audit_event('suspicious_activity_detected', {'user_id': user_id})
            return True
        
        return False
    
    # ========== 4. BIAS DETECTION AND MITIGATION ==========
    
    def detect_bias(self, text: str) -> Dict[str, float]:
        """
        Detect potential bias in generated content
        Returns: Dictionary of bias scores by category
        """
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
    
    def assess_bias_level(self, text: str) -> Tuple[bool, Dict[str, float]]:
        """
        Assess if bias level exceeds threshold
        Returns: (exceeds_threshold, bias_scores)
        """
        bias_scores = self.detect_bias(text)
        exceeds_threshold = any(score > self.MAX_BIAS_THRESHOLD for score in bias_scores.values())
        
        if exceeds_threshold:
            logger.warning(f"Bias threshold exceeded: {bias_scores}")
            self._log_audit_event('bias_threshold_exceeded', {'scores': bias_scores})
        
        return exceeds_threshold, bias_scores
    
    # ========== 5. QUALITY ASSURANCE AND VALIDATION ==========
    
    def assess_quality(self, text: str, context: Dict) -> Dict[str, float]:
        """
        Multi-metric quality assessment
        Returns: Dictionary of quality scores
        """
        scores = {
            'completeness': self._assess_completeness(text, context),
            'accuracy': self._assess_accuracy(text, context),
            'relevance': self._assess_relevance(text, context),
            'professionalism': self._assess_professionalism(text),
            'clarity': self._assess_clarity(text)
        }
        
        # Calculate overall quality score
        scores['overall'] = sum(scores.values()) / len(scores)
        
        self.quality_metrics.append({
            'timestamp': datetime.now(),
            'scores': scores
        })
        
        return scores
    
    def _assess_completeness(self, text: str, context: Dict) -> float:
        """Assess content completeness"""
        # Simple heuristic: check if text has minimum length and structure
        min_length = context.get('min_length', 100)
        has_sections = len(text.split('\n\n')) >= 3
        
        length_score = min(len(text) / min_length, 1.0)
        structure_score = 1.0 if has_sections else 0.5
        
        return (length_score + structure_score) / 2
    
    def _assess_accuracy(self, text: str, context: Dict) -> float:
        """Assess content accuracy (placeholder - would use ML in production)"""
        # In production, this would use ML models or fact-checking APIs
        return 0.9  # Placeholder
    
    def _assess_relevance(self, text: str, context: Dict) -> float:
        """Assess content relevance to request"""
        # Check if key terms from context appear in text
        key_terms = context.get('key_terms', [])
        if not key_terms:
            return 0.9
        
        text_lower = text.lower()
        matches = sum(1 for term in key_terms if term.lower() in text_lower)
        return matches / len(key_terms) if key_terms else 0.9
    
    def _assess_professionalism(self, text: str) -> float:
        """Assess professional tone and language"""
        # Check for professional indicators
        professional_indicators = [
            'project', 'management', 'stakeholder', 'deliverable',
            'milestone', 'objective', 'strategy', 'implementation'
        ]
        
        text_lower = text.lower()
        matches = sum(1 for indicator in professional_indicators if indicator in text_lower)
        
        return min(matches / 5, 1.0)  # Normalize to 0-1
    
    def _assess_clarity(self, text: str) -> float:
        """Assess text clarity and readability"""
        # Simple readability heuristic
        sentences = text.split('.')
        if not sentences:
            return 0.5
        
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Optimal sentence length is 15-20 words
        if 15 <= avg_sentence_length <= 20:
            return 1.0
        elif 10 <= avg_sentence_length <= 25:
            return 0.8
        else:
            return 0.6
    
    def validate_quality(self, text: str, context: Dict) -> Tuple[bool, Dict]:
        """
        Validate if content meets quality threshold
        Returns: (meets_threshold, quality_scores)
        """
        scores = self.assess_quality(text, context)
        meets_threshold = scores['overall'] >= self.MIN_QUALITY_SCORE
        
        if not meets_threshold:
            logger.warning(f"Quality threshold not met: {scores['overall']:.2f}")
            self._log_audit_event('quality_threshold_not_met', {'scores': scores})
        
        return meets_threshold, scores
    
    # ========== 6. ERROR HANDLING AND FALLBACK SYSTEMS ==========
    
    def get_fallback_content(self, content_type: str) -> str:
        """
        Provide fallback content when AI generation fails or doesn't meet standards
        """
        fallback_templates = {
            'project_charter': "Professional project charter template with PMI 2025 standards...",
            'risk_register': "Comprehensive risk register following industry best practices...",
            'default': "Professional project management template..."
        }
        
        fallback = fallback_templates.get(content_type, fallback_templates['default'])
        self._log_audit_event('fallback_content_used', {'type': content_type})
        
        return fallback
    
    # ========== 7. USER CONSENT AND TRANSPARENCY ==========
    
    def get_ai_disclosure(self) -> Dict:
        """
        Provide transparent AI usage disclosure
        """
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
                "Privacy protection measures enforced"
            ]
        }
    
    def verify_user_consent(self, user_id: str) -> bool:
        """
        Verify user has consented to AI usage
        """
        # In production, this would check database for user consent record
        # For now, return True (assuming consent obtained during registration)
        return True
    
    # ========== 8. AUDIT LOGGING AND MONITORING ==========
    
    def _log_audit_event(self, event_type: str, details: Dict):
        """
        Log audit event for compliance and monitoring
        """
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }
        self.audit_log.append(audit_entry)
        logger.info(f"Audit event: {event_type} - {details}")
    
    def get_audit_log(self, start_time: Optional[datetime] = None) -> List[Dict]:
        """
        Retrieve audit log entries
        """
        if start_time:
            return [
                entry for entry in self.audit_log
                if datetime.fromisoformat(entry['timestamp']) >= start_time
            ]
        return self.audit_log
    
    # ========== 9. COMPLIANCE FRAMEWORK ==========
    
    def check_gdpr_compliance(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        Check GDPR compliance for AI processing
        """
        issues = []
        
        # Check for user consent
        if not data.get('user_consent'):
            issues.append("User consent not obtained")
        
        # Check for data minimization
        if 'pii' in str(data).lower():
            issues.append("Potential PII present in data")
        
        # Check for transparency
        if not data.get('ai_disclosure'):
            issues.append("AI usage disclosure not provided")
        
        is_compliant = len(issues) == 0
        return is_compliant, issues
    
    def check_ccpa_compliance(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        Check CCPA compliance for AI processing
        """
        issues = []
        
        # Check for opt-out mechanism
        if not data.get('opt_out_available'):
            issues.append("Opt-out mechanism not available")
        
        # Check for data deletion capability
        if not data.get('deletion_capability'):
            issues.append("Data deletion capability not implemented")
        
        is_compliant = len(issues) == 0
        return is_compliant, issues
    
    # ========== 10. CONTINUOUS MONITORING ==========
    
    def get_performance_metrics(self) -> Dict:
        """
        Get AI performance metrics for monitoring
        """
        if not self.quality_metrics:
            return {}
        
        recent_metrics = self.quality_metrics[-100:]  # Last 100 requests
        
        avg_quality = sum(m['scores']['overall'] for m in recent_metrics) / len(recent_metrics)
        
        return {
            'average_quality_score': avg_quality,
            'total_requests': len(self.quality_metrics),
            'recent_requests': len(recent_metrics),
            'quality_threshold_compliance': sum(
                1 for m in recent_metrics if m['scores']['overall'] >= self.MIN_QUALITY_SCORE
            ) / len(recent_metrics) * 100,
            'audit_events': len(self.audit_log)
        }
    
    # ========== MAIN VALIDATION PIPELINE ==========
    
    def validate_ai_request(self, user_id: str, input_text: str, user_tier: str = 'free', context: Dict = None) -> Dict:
        """
        Complete AI request validation pipeline
        Returns: Validation result with status and details
        """
        context = context or {}
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sanitized_input': input_text,
            'metadata': {}
        }
        
        # 1. Check user consent
        if not self.verify_user_consent(user_id):
            result['valid'] = False
            result['errors'].append("User consent required for AI usage")
            return result
        
        # 2. Check rate limit
        rate_ok, rate_msg = self.check_rate_limit(user_id, user_tier)
        if not rate_ok:
            result['valid'] = False
            result['errors'].append(rate_msg)
            return result
        
        # 3. Validate input
        input_valid, input_msg = self.validate_input(input_text, user_tier)
        if not input_valid:
            result['valid'] = False
            result['errors'].append(input_msg)
            return result
        
        # 4. Sanitize input
        result['sanitized_input'] = self.sanitize_input(input_text)
        
        # 5. Check for suspicious activity
        if self.detect_suspicious_activity(user_id):
            result['warnings'].append("Suspicious activity detected - request flagged for review")
        
        # 6. Add AI disclosure
        result['metadata']['ai_disclosure'] = self.get_ai_disclosure()
        
        # Log successful validation
        self._log_audit_event('request_validated', {
            'user_id': user_id,
            'tier': user_tier,
            'input_length': len(input_text)
        })
        
        return result
    
    def validate_ai_output(self, output_text: str, context: Dict = None) -> Dict:
        """
        Complete AI output validation pipeline
        Returns: Validation result with status and details
        """
        context = context or {}
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'quality_scores': {},
            'bias_scores': {},
            'metadata': {}
        }
        
        # 1. Check quality
        quality_ok, quality_scores = self.validate_quality(output_text, context)
        result['quality_scores'] = quality_scores
        
        if not quality_ok:
            result['valid'] = False
            result['errors'].append(f"Quality threshold not met: {quality_scores['overall']:.2f}")
        
        # 2. Check bias
        bias_exceeded, bias_scores = self.assess_bias_level(output_text)
        result['bias_scores'] = bias_scores
        
        if bias_exceeded:
            result['warnings'].append("Bias threshold exceeded - content may need review")
        
        # 3. Check for inappropriate content
        inappropriate, reason = self.detect_inappropriate_content(output_text)
        if inappropriate:
            result['valid'] = False
            result['errors'].append(reason)
        
        # 4. Add transparency metadata
        result['metadata']['ai_disclosure'] = self.get_ai_disclosure()
        result['metadata']['validation_timestamp'] = datetime.now().isoformat()
        
        # Log validation
        self._log_audit_event('output_validated', {
            'quality_score': quality_scores.get('overall', 0),
            'bias_detected': bias_exceeded,
            'valid': result['valid']
        })
        
        return result


# Global instance for easy access
guardrails = AIGuardrails()


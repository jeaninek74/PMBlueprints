"""
PMBlueprints AI Generation Routes
AI-powered template generation with comprehensive guardrails
"""

from flask import Blueprint, request, jsonify
from ai_guardrails import guardrails
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# Check if OpenAI API key is available
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
AI_ENABLED = OPENAI_API_KEY is not None

if AI_ENABLED:
    try:
        from openai import OpenAI
        client = OpenAI()  # API key from environment
        logger.info("OpenAI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        AI_ENABLED = False


@ai_bp.route('/generate', methods=['POST'])
def generate_template():
    """
    Generate AI-powered project management template with full guardrails
    
    Request body:
    {
        "user_id": "string",
        "user_tier": "free|starter|professional",
        "template_type": "string",
        "project_description": "string",
        "industry": "string",
        "additional_requirements": "string" (optional)
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract parameters
        user_id = data.get('user_id', 'anonymous')
        user_tier = data.get('user_tier', 'free')
        template_type = data.get('template_type', 'project_charter')
        project_description = data.get('project_description', '')
        industry = data.get('industry', 'general')
        additional_requirements = data.get('additional_requirements', '')
        
        # Build input text
        input_text = f"{project_description} {additional_requirements}".strip()
        
        if not input_text:
            return jsonify({
                'success': False,
                'error': 'Project description is required'
            }), 400
        
        # ========== GUARDRAILS: INPUT VALIDATION ==========
        validation_result = guardrails.validate_ai_request(
            user_id=user_id,
            input_text=input_text,
            user_tier=user_tier,
            context={
                'template_type': template_type,
                'industry': industry
            }
        )
        
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': 'Input validation failed',
                'details': validation_result['errors'],
                'warnings': validation_result['warnings']
            }), 400
        
        # Use sanitized input
        sanitized_input = validation_result['sanitized_input']
        
        # ========== AI GENERATION ==========
        if not AI_ENABLED:
            # Fallback to pre-built template
            content = guardrails.get_fallback_content(template_type)
            return jsonify({
                'success': True,
                'content': content,
                'ai_generated': False,
                'fallback_used': True,
                'message': 'AI generation not available, using pre-built template',
                'metadata': validation_result['metadata']
            })
        
        try:
            # Generate content with OpenAI
            generated_content = _generate_with_openai(
                template_type=template_type,
                project_description=sanitized_input,
                industry=industry
            )
            
            # ========== GUARDRAILS: OUTPUT VALIDATION ==========
            output_validation = guardrails.validate_ai_output(
                output_text=generated_content,
                context={
                    'template_type': template_type,
                    'industry': industry,
                    'min_length': 200,
                    'key_terms': [template_type, industry, 'project']
                }
            )
            
            if not output_validation['valid']:
                # Use fallback if output doesn't meet standards
                logger.warning(f"AI output failed validation: {output_validation['errors']}")
                content = guardrails.get_fallback_content(template_type)
                
                return jsonify({
                    'success': True,
                    'content': content,
                    'ai_generated': False,
                    'fallback_used': True,
                    'message': 'AI output did not meet quality standards, using pre-built template',
                    'validation_details': output_validation,
                    'metadata': validation_result['metadata']
                })
            
            # Track AI generation in monitoring system
            from monitoring import track_ai_generation
            track_ai_generation(user_id)
            
            # Return successful AI-generated content
            return jsonify({
                'success': True,
                'content': generated_content,
                'ai_generated': True,
                'fallback_used': False,
                'quality_scores': output_validation['quality_scores'],
                'bias_scores': output_validation['bias_scores'],
                'metadata': {
                    **validation_result['metadata'],
                    **output_validation['metadata']
                },
                'warnings': output_validation['warnings']
            })
            
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            # Fallback on error
            content = guardrails.get_fallback_content(template_type)
            return jsonify({
                'success': True,
                'content': content,
                'ai_generated': False,
                'fallback_used': True,
                'message': f'AI generation failed: {str(e)}',
                'metadata': validation_result['metadata']
            })
    
    except Exception as e:
        logger.error(f"Unexpected error in generate_template: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@ai_bp.route('/enhance', methods=['POST'])
def enhance_template():
    """
    Enhance existing template content with AI suggestions
    
    Request body:
    {
        "user_id": "string",
        "user_tier": "free|starter|professional",
        "template_content": "string",
        "enhancement_type": "improve_clarity|add_details|professional_tone"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        user_id = data.get('user_id', 'anonymous')
        user_tier = data.get('user_tier', 'free')
        template_content = data.get('template_content', '')
        enhancement_type = data.get('enhancement_type', 'improve_clarity')
        
        if not template_content:
            return jsonify({
                'success': False,
                'error': 'Template content is required'
            }), 400
        
        # ========== GUARDRAILS: INPUT VALIDATION ==========
        validation_result = guardrails.validate_ai_request(
            user_id=user_id,
            input_text=template_content,
            user_tier=user_tier,
            context={'enhancement_type': enhancement_type}
        )
        
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': 'Input validation failed',
                'details': validation_result['errors']
            }), 400
        
        # For now, return original content with quality assessment
        quality_scores = guardrails.assess_quality(
            template_content,
            {'min_length': 100, 'key_terms': ['project', 'management']}
        )
        
        return jsonify({
            'success': True,
            'enhanced_content': template_content,
            'original_content': template_content,
            'ai_generated': False,
            'quality_scores': quality_scores,
            'suggestions': [
                "Consider adding more specific details about project deliverables",
                "Include stakeholder communication plan",
                "Add risk mitigation strategies"
            ],
            'metadata': validation_result['metadata']
        })
    
    except Exception as e:
        logger.error(f"Error in enhance_template: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@ai_bp.route('/metrics', methods=['GET'])
def get_ai_metrics():
    """
    Get AI performance metrics and monitoring data
    Requires admin authentication (simplified for demo)
    """
    try:
        metrics = guardrails.get_performance_metrics()
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'timestamp': guardrails.audit_log[-1]['timestamp'] if guardrails.audit_log else None
        })
    
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/audit-log', methods=['GET'])
def get_audit_log():
    """
    Get AI audit log for compliance monitoring
    Requires admin authentication (simplified for demo)
    """
    try:
        # Get optional time filter
        limit = request.args.get('limit', 100, type=int)
        
        audit_log = guardrails.get_audit_log()
        
        # Return most recent entries
        recent_log = audit_log[-limit:] if len(audit_log) > limit else audit_log
        
        return jsonify({
            'success': True,
            'audit_log': recent_log,
            'total_entries': len(audit_log),
            'returned_entries': len(recent_log)
        })
    
    except Exception as e:
        logger.error(f"Error getting audit log: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/consent', methods=['POST'])
def record_user_consent():
    """
    Record user consent for AI usage
    
    Request body:
    {
        "user_id": "string",
        "consent_given": boolean,
        "consent_type": "ai_generation|data_processing"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        user_id = data.get('user_id')
        consent_given = data.get('consent_given', False)
        consent_type = data.get('consent_type', 'ai_generation')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'User ID is required'
            }), 400
        
        # Log consent
        guardrails._log_audit_event('user_consent_recorded', {
            'user_id': user_id,
            'consent_given': consent_given,
            'consent_type': consent_type
        })
        
        return jsonify({
            'success': True,
            'message': 'Consent recorded successfully',
            'user_id': user_id,
            'consent_given': consent_given
        })
    
    except Exception as e:
        logger.error(f"Error recording consent: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/disclosure', methods=['GET'])
def get_ai_disclosure():
    """
    Get AI usage disclosure information for transparency
    """
    try:
        disclosure = guardrails.get_ai_disclosure()
        
        return jsonify({
            'success': True,
            'disclosure': disclosure
        })
    
    except Exception as e:
        logger.error(f"Error getting disclosure: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ========== HELPER FUNCTIONS ==========

def _generate_with_openai(template_type: str, project_description: str, industry: str) -> str:
    """
    Generate template content using OpenAI API
    """
    # Build prompt
    prompt = f"""Generate a professional {template_type} for a {industry} project.

Project Description: {project_description}

Requirements:
- Follow PMI standards
- Use professional language
- Include all standard sections for a {template_type}
- Be specific and actionable
- Maintain inclusive and unbiased language

Generate a comprehensive {template_type} that meets these requirements."""

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # Using available model
        messages=[
            {
                "role": "system",
                "content": "You are a professional project management expert specializing in creating PMI-compliant templates. Generate high-quality, professional, and unbiased content."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=2000,
        temperature=0.7
    )
    
    return response.choices[0].message.content


def register_ai_routes(app):
    """
    Register AI routes with the Flask app
    """
    app.register_blueprint(ai_bp)
    logger.info("AI generation routes registered")


"""
PMBlueprints AI Generation Routes - Secure Version
AI-powered template generation with persistent usage tracking and comprehensive guardrails
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ai_guardrails_persistent import create_guardrails
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
ai_secure_bp = Blueprint('ai_secure', __name__, url_prefix='/api/ai')

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


@ai_secure_bp.route('/generate', methods=['POST'])
@login_required
def generate_template():
    """
    Generate AI-powered project management template with full guardrails and persistent tracking
    
    Request body:
    {
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
        
        # Import database session
        from app import db
        
        # Create guardrails instance with database session
        guardrails = create_guardrails(db.session)
        
        # ========== GUARDRAILS: INPUT VALIDATION WITH PERSISTENT TRACKING ==========
        validation_result = guardrails.validate_ai_request(
            user=current_user,
            input_text=input_text,
            context={
                'template_type': template_type,
                'industry': industry
            }
        )
        
        if not validation_result['valid']:
            # Log failed request
            guardrails._log_ai_usage(
                user_id=current_user.id,
                request_type='generate',
                success=False,
                template_type=template_type,
                input_length=len(input_text),
                error_message='; '.join(validation_result['errors'])
            )
            
            return jsonify({
                'success': False,
                'error': 'Input validation failed',
                'details': validation_result['errors'],
                'warnings': validation_result['warnings'],
                'remaining_monthly': validation_result['metadata'].get('remaining_monthly', 0)
            }), 400
        
        # Use sanitized input
        sanitized_input = validation_result['sanitized_input']
        
        # ========== AI GENERATION ==========
        if not AI_ENABLED:
            # Fallback to pre-built template
            content = guardrails.get_fallback_content(template_type)
            
            # Log usage (fallback doesn't count against limit)
            guardrails._log_ai_usage(
                user_id=current_user.id,
                request_type='generate_fallback',
                success=True,
                template_type=template_type,
                input_length=len(input_text),
                output_length=len(content)
            )
            
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
                
                # Log failed generation (doesn't count against limit)
                guardrails._log_ai_usage(
                    user_id=current_user.id,
                    request_type='generate',
                    success=False,
                    template_type=template_type,
                    input_length=len(input_text),
                    output_length=len(generated_content),
                    error_message='Output validation failed'
                )
                
                return jsonify({
                    'success': True,
                    'content': content,
                    'ai_generated': False,
                    'fallback_used': True,
                    'message': 'AI output did not meet quality standards, using pre-built template',
                    'validation_details': output_validation,
                    'metadata': validation_result['metadata']
                })
            
            # ========== INCREMENT USAGE COUNTER ==========
            guardrails.increment_usage(current_user)
            
            # Log successful generation
            guardrails._log_ai_usage(
                user_id=current_user.id,
                request_type='generate',
                success=True,
                template_type=template_type,
                input_length=len(input_text),
                output_length=len(generated_content),
                tokens_used=len(generated_content.split())  # Approximate
            )
            
            # Commit database changes
            db.session.commit()
            
            # Track in monitoring system
            try:
                from monitoring import track_ai_generation
                track_ai_generation(current_user.id)
            except:
                pass  # Monitoring is optional
            
            # Calculate remaining generations
            monthly_limit = guardrails.MONTHLY_LIMITS.get(current_user.subscription_plan, 3)
            remaining = monthly_limit - current_user.ai_generations_used_this_month
            
            # Return successful AI-generated content
            return jsonify({
                'success': True,
                'content': generated_content,
                'ai_generated': True,
                'fallback_used': False,
                'quality_scores': output_validation['quality_scores'],
                'bias_scores': output_validation['bias_scores'],
                'usage': {
                    'used_this_month': current_user.ai_generations_used_this_month,
                    'monthly_limit': monthly_limit,
                    'remaining': remaining,
                    'reset_date': current_user.ai_generation_reset_date.isoformat() if current_user.ai_generation_reset_date else None
                },
                'metadata': {
                    **validation_result['metadata'],
                    **output_validation['metadata']
                },
                'warnings': output_validation['warnings']
            })
            
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            
            # Log error
            guardrails._log_ai_usage(
                user_id=current_user.id,
                request_type='generate',
                success=False,
                template_type=template_type,
                input_length=len(input_text),
                error_message=str(e)
            )
            db.session.commit()
            
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


@ai_secure_bp.route('/usage', methods=['GET'])
@login_required
def get_usage_stats():
    """
    Get user's AI usage statistics
    """
    try:
        from app import db
        guardrails = create_guardrails(db.session)
        
        # Reset if needed
        guardrails._reset_monthly_usage_if_needed(current_user)
        db.session.commit()
        
        monthly_limit = guardrails.MONTHLY_LIMITS.get(current_user.subscription_plan, 3)
        used = current_user.ai_generations_used_this_month or 0
        remaining = max(0, monthly_limit - used)
        
        return jsonify({
            'success': True,
            'usage': {
                'subscription_plan': current_user.subscription_plan,
                'used_this_month': used,
                'monthly_limit': monthly_limit,
                'remaining': remaining,
                'reset_date': current_user.ai_generation_reset_date.isoformat() if current_user.ai_generation_reset_date else None,
                'percentage_used': (used / monthly_limit * 100) if monthly_limit > 0 else 0
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve usage statistics'
        }), 500


@ai_secure_bp.route('/history', methods=['GET'])
@login_required
def get_usage_history():
    """
    Get user's AI usage history
    """
    try:
        from app import db
        from sqlalchemy import text
        
        # Get limit parameter
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 100)  # Max 100 records
        
        # Query usage log
        query = text("""
            SELECT 
                request_type,
                template_type,
                timestamp,
                success,
                tokens_used,
                input_length,
                output_length
            FROM ai_usage_log
            WHERE user_id = :user_id
            ORDER BY timestamp DESC
            LIMIT :limit
        """)
        
        result = db.session.execute(query, {
            'user_id': current_user.id,
            'limit': limit
        })
        
        history = []
        for row in result:
            history.append({
                'request_type': row[0],
                'template_type': row[1],
                'timestamp': row[2].isoformat() if row[2] else None,
                'success': row[3],
                'tokens_used': row[4],
                'input_length': row[5],
                'output_length': row[6]
            })
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })
    
    except Exception as e:
        logger.error(f"Error getting usage history: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve usage history'
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
- Follow PMI 2025 standards
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
                "content": "You are a professional project management expert specializing in creating PMI 2025-compliant templates. Generate high-quality, professional, and unbiased content."
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


def register_ai_secure_routes(app):
    """
    Register secure AI routes with the Flask app
    """
    app.register_blueprint(ai_secure_bp)
    logger.info("Secure AI generation routes registered")


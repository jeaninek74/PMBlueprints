"""
AI Suggestions Routes - FREE feature for users
Provides quick AI-powered suggestions without full template generation
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
ai_suggestions_bp = Blueprint('ai_suggestions', __name__)

# Check if OpenAI API key is available
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
AI_ENABLED = OPENAI_API_KEY is not None

if AI_ENABLED:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialized for AI suggestions")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        AI_ENABLED = False


@ai_suggestions_bp.route('/suggestions')
@login_required
def suggestions_page():
    """AI Suggestions page"""
    return render_template('ai_suggestions.html')


@ai_suggestions_bp.route('/api/suggest', methods=['POST'])
@login_required
def get_suggestion():
    """
    Get AI suggestion based on user query
    
    Request body:
    {
        "template_type": "Risk Register",
        "question": "What risks should I include for a software project?",
        "context": "Optional additional context"
    }
    """
    if not AI_ENABLED:
        return jsonify({
            'success': False,
            'error': 'AI suggestions are currently unavailable'
        }), 503
    
    try:
        data = request.get_json()
        template_type = data.get('template_type', 'Project Management')
        question = data.get('question', '')
        context = data.get('context', '')
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        # Build prompt for AI
        prompt = f"""You are a PMI-certified project management expert helping users fill out project management templates.

Template Type: {template_type}
User Question: {question}
{f'Additional Context: {context}' if context else ''}

Provide a helpful, concise suggestion (2-4 bullet points) that the user can use in their template. 
Focus on practical, actionable items that follow PMI best practices.
Keep the response under 200 words."""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a PMI-certified project management expert providing brief, actionable suggestions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        suggestion = response.choices[0].message.content.strip()
        
        # Track usage (optional)
        if hasattr(current_user, 'openai_usage_count'):
            from app import db
            current_user.openai_usage_count = (current_user.openai_usage_count or 0) + 1
            db.session.commit()
        
        logger.info(f"AI suggestion provided to user {current_user.id}")
        
        return jsonify({
            'success': True,
            'suggestion': suggestion
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating AI suggestion: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate suggestion. Please try again.'
        }), 500


@ai_suggestions_bp.route('/api/suggest/quick', methods=['POST'])
@login_required
def quick_suggestion():
    """
    Quick suggestions for common template sections
    
    Request body:
    {
        "template_type": "Risk Register",
        "section": "risks" | "stakeholders" | "milestones" | "resources"
    }
    """
    if not AI_ENABLED:
        return jsonify({
            'success': False,
            'error': 'AI suggestions are currently unavailable'
        }), 503
    
    try:
        data = request.get_json()
        template_type = data.get('template_type', 'Project Management')
        section = data.get('section', '')
        
        # Predefined prompts for quick suggestions
        prompts = {
            'risks': f"List 5 common risks for a {template_type} project with brief mitigation strategies.",
            'stakeholders': f"List 5 key stakeholder types for a {template_type} project and their typical roles.",
            'milestones': f"Suggest 5 typical milestones for a {template_type} project in chronological order.",
            'resources': f"List 5 essential resource types needed for a {template_type} project.",
            'deliverables': f"List 5 common deliverables for a {template_type} project.",
            'tasks': f"List 5 key tasks for the planning phase of a {template_type} project."
        }
        
        if section not in prompts:
            return jsonify({
                'success': False,
                'error': 'Invalid section type'
            }), 400
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a PMI-certified project management expert. Provide concise, bullet-point lists."},
                {"role": "user", "content": prompts[section]}
            ],
            max_tokens=250,
            temperature=0.7
        )
        
        suggestion = response.choices[0].message.content.strip()
        
        # Track usage
        if hasattr(current_user, 'openai_usage_count'):
            from app import db
            current_user.openai_usage_count = (current_user.openai_usage_count or 0) + 1
            db.session.commit()
        
        return jsonify({
            'success': True,
            'suggestion': suggestion
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating quick suggestion: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate suggestion. Please try again.'
        }), 500


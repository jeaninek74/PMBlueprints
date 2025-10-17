"""
AI Suggestions Routes
Handles AI-powered template suggestions with tier-based access control
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import logging
import os
import openai
from datetime import datetime

logger = logging.getLogger(__name__)

ai_suggestions_bp = Blueprint('ai_suggestions', __name__, url_prefix='/ai/suggestions')

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

@ai_suggestions_bp.route('/')
def index():
    """AI Suggestions page - public view, suggestions require login"""
    from flask_login import current_user
    from utils.subscription_security import get_usage_stats
    
    usage_stats = get_usage_stats(current_user) if current_user.is_authenticated else None
    
    return render_template('ai_suggestions.html', usage_stats=usage_stats)

@ai_suggestions_bp.route('/get', methods=['POST'])
@login_required
def get_suggestions():
    """Get AI-powered template suggestions"""
    from utils.subscription_security import check_usage_limit
    from database import db
    from models import AISuggestionHistory, Template
    
    try:
        # Check usage quota
        can_suggest, remaining, limit = check_usage_limit(current_user, 'ai_suggestions')
        
        if not can_suggest:
            return jsonify({
                'error': f'You have reached your AI suggestions limit ({limit} per month). Please upgrade your subscription.',
                'upgrade_required': True,
                'remaining': 0,
                'limit': limit
            }), 403
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        project_description = data.get('project_description', '')
        industry = data.get('industry', '')
        project_phase = data.get('project_phase', '')
        team_size = data.get('team_size', '')
        
        if not project_description:
            return jsonify({'error': 'Project description is required'}), 400
        
        # Get available templates from database
        templates_query = Template.query
        if industry:
            templates_query = templates_query.filter_by(industry=industry)
        
        available_templates = templates_query.limit(50).all()
        template_list = "\n".join([f"- {t.name} ({t.category})" for t in available_templates])
        
        # Generate suggestions using OpenAI
        prompt = f"""
You are an expert project management consultant. Based on the following project details, 
recommend the most relevant templates and provide actionable suggestions.

Project Details:
- Description: {project_description}
- Industry: {industry or 'Not specified'}
- Project Phase: {project_phase or 'Not specified'}
- Team Size: {team_size or 'Not specified'}

Available Templates:
{template_list}

Please provide:
1. Top 5 recommended templates from the list above
2. Why each template is relevant
3. Best practices for using these templates
4. Additional suggestions for project success

Format your response as JSON with this structure:
{{
    "recommended_templates": [
        {{"name": "Template Name", "reason": "Why it's relevant", "priority": "High/Medium/Low"}}
    ],
    "best_practices": ["Practice 1", "Practice 2", ...],
    "additional_suggestions": ["Suggestion 1", "Suggestion 2", ...]
}}
"""
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert project management consultant. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        suggestions_text = response.choices[0].message.content
        
        # Try to parse as JSON, fallback to text if it fails
        import json
        try:
            suggestions_data = json.loads(suggestions_text)
        except:
            # Fallback: create structured response from text
            suggestions_data = {
                "recommended_templates": [],
                "best_practices": [],
                "additional_suggestions": [suggestions_text]
            }
        
        # Track usage
        current_user.ai_suggestions_this_month += 1
        
        # Save suggestion history
        history = AISuggestionHistory(
            user_id=current_user.id,
            project_description=project_description,
            industry=industry,
            project_phase=project_phase,
            team_size=team_size,
            suggestions=suggestions_text,
            created_at=datetime.utcnow()
        )
        db.session.add(history)
        db.session.commit()
        
        # Find actual template IDs for recommendations
        recommended_with_ids = []
        for rec in suggestions_data.get('recommended_templates', []):
            template_name = rec.get('name', '')
            # Try to find matching template
            template = Template.query.filter(
                Template.name.ilike(f'%{template_name}%')
            ).first()
            
            if template:
                rec['template_id'] = template.id
                rec['template_url'] = f"/templates/{template.id}"
            
            recommended_with_ids.append(rec)
        
        suggestions_data['recommended_templates'] = recommended_with_ids
        
        # Return success
        return jsonify({
            'success': True,
            'suggestions': suggestions_data,
            'history_id': history.id,
            'remaining': remaining - 1,
            'limit': limit
        })
        
    except openai.error.RateLimitError:
        logger.error("OpenAI rate limit exceeded")
        return jsonify({'error': 'AI service is currently busy. Please try again in a moment.'}), 429
    
    except openai.error.AuthenticationError:
        logger.error("OpenAI authentication error")
        return jsonify({'error': 'AI service configuration error. Please contact support.'}), 500
    
    except Exception as e:
        logger.error(f"AI suggestions error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@ai_suggestions_bp.route('/history')
@login_required
def history():
    """View suggestion history"""
    from models import AISuggestionHistory
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    history_query = AISuggestionHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(AISuggestionHistory.created_at.desc())
    
    pagination = history_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('ai/suggestions_history.html', 
                         history=pagination.items,
                         pagination=pagination)

@ai_suggestions_bp.route('/export/<int:history_id>')
@login_required
def export(history_id):
    """Export suggestions as PDF or document"""
    from models import AISuggestionHistory
    from docx import Document
    import io
    from flask import send_file
    
    history = AISuggestionHistory.query.get_or_404(history_id)
    
    # Verify ownership
    if history.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Create Word document
        doc = Document()
        doc.add_heading('AI Template Suggestions', 0)
        
        doc.add_heading('Project Details', level=1)
        doc.add_paragraph(f"Description: {history.project_description}")
        doc.add_paragraph(f"Industry: {history.industry or 'Not specified'}")
        doc.add_paragraph(f"Project Phase: {history.project_phase or 'Not specified'}")
        doc.add_paragraph(f"Team Size: {history.team_size or 'Not specified'}")
        
        doc.add_heading('AI Suggestions', level=1)
        doc.add_paragraph(history.suggestions)
        
        doc.add_paragraph(f"\nGenerated on: {history.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save to BytesIO
        file_data = io.BytesIO()
        doc.save(file_data)
        file_data.seek(0)
        
        filename = f"AI_Suggestions_{history.id}.docx"
        
        return send_file(
            file_data,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return jsonify({'error': 'Error exporting suggestions'}), 500


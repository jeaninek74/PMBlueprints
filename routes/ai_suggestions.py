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

ai_suggestions_bp = Blueprint('ai_suggestions', __name__)

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
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if this is a quick suggestion or custom question
        template_type = data.get('template_type', '')
        section = data.get('section', '')
        question = data.get('question', '')
        context = data.get('context', '')
        
        # For backward compatibility
        project_description = data.get('project_description', '')
        industry = data.get('industry', '')
        project_phase = data.get('project_phase', '')
        team_size = data.get('team_size', '')
        
        # Generate prompt based on request type
        if section:
            # Quick suggestion
            prompt = f"""
You are an expert project management consultant. Provide a comprehensive list of {section} for a {template_type} project.

Provide 8-12 specific, actionable items that are relevant for this type of project.
Format as a numbered list with brief explanations.

Example format:
1. Item name - Brief explanation of why it's important
2. Item name - Brief explanation
...
"""
        elif question:
            # Custom question
            prompt = f"""
You are an expert project management consultant. Answer the following question:

Template Type: {template_type}
Question: {question}
Context: {context or 'None provided'}

Provide a detailed, professional answer with specific recommendations and best practices.
"""
        else:
            # Legacy format for backward compatibility
            templates_query = Template.query
            if industry:
                templates_query = templates_query.filter_by(industry=industry)
            
            available_templates = templates_query.limit(50).all()
            template_list = "\n".join([f"- {t.name} ({t.category})" for t in available_templates])
            
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
"""
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert project management consultant with deep knowledge of PMBOK 7th Edition and modern project management practices."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        suggestions_text = response.choices[0].message.content
        
        # Save suggestion history
        history = AISuggestionHistory(
            user_id=current_user.id,
            project_description=question or f"{template_type} - {section}" or project_description,
            industry=industry or template_type,
            project_phase=project_phase or '',
            team_size=team_size or context,
            suggestions=suggestions_text,
            created_at=datetime.utcnow()
        )
        db.session.add(history)
        db.session.commit()
        
        # Return success
        return jsonify({
            'success': True,
            'suggestion': suggestions_text,
            'history_id': history.id
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


"""
API Routes
RESTful API endpoints for frontend and external integrations
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/templates')
def get_templates():
    """Get templates with filtering and pagination"""
    try:
        from app import Template
        
        # Get query parameters
        industry = request.args.get('industry')
        category = request.args.get('category')
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sort_by = request.args.get('sort_by', 'downloads')  # name, downloads, rating
        sort_order = request.args.get('sort_order', 'desc')  # asc, desc
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        # Build query
        query = Template.query
        
        if industry:
            query = query.filter(Template.industry == industry)
        
        if category:
            query = query.filter(Template.category == category)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Template.name.ilike(search_term) | 
                Template.description.ilike(search_term) |
                Template.tags.ilike(search_term)
            )
        
        # Apply sorting
        if sort_by == 'name':
            if sort_order == 'desc':
                query = query.order_by(Template.name.desc())
            else:
                query = query.order_by(Template.name.asc())
        elif sort_by == 'rating':
            if sort_order == 'desc':
                query = query.order_by(Template.rating.desc())
            else:
                query = query.order_by(Template.rating.asc())
        else:  # downloads
            if sort_order == 'desc':
                query = query.order_by(Template.downloads.desc())
            else:
                query = query.order_by(Template.downloads.asc())
        
        # Get paginated results
        templates = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'templates': [t.to_dict() for t in templates.items],
            'pagination': {
                'page': templates.page,
                'pages': templates.pages,
                'per_page': templates.per_page,
                'total': templates.total,
                'has_next': templates.has_next,
                'has_prev': templates.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"API templates error: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch templates'}), 500

@api_bp.route('/templates/<int:template_id>')
def get_template(template_id):
    """Get single template details"""
    try:
        from app import Template
        
        template = Template.query.get_or_404(template_id)
        
        return jsonify({
            'success': True,
            'template': template.to_dict()
        })
        
    except Exception as e:
        logger.error(f"API template detail error: {e}")
        return jsonify({'success': False, 'error': 'Template not found'}), 404

@api_bp.route('/industries')
def get_industries():
    """Get list of available industries"""
    try:
        from app import Template
        
        industries = Template.query.with_entities(Template.industry)\
            .distinct().order_by(Template.industry).all()
        
        return jsonify({
            'success': True,
            'industries': [i[0] for i in industries]
        })
        
    except Exception as e:
        logger.error(f"API industries error: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch industries'}), 500

@api_bp.route('/categories')
def get_categories():
    """Get list of available categories"""
    try:
        from app import Template
        
        categories = Template.query.with_entities(Template.category)\
            .distinct().order_by(Template.category).all()
        
        return jsonify({
            'success': True,
            'categories': [c[0] for c in categories]
        })
        
    except Exception as e:
        logger.error(f"API categories error: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch categories'}), 500

@api_bp.route('/search')
def search_templates():
    """Search templates"""
    try:
        from app import Template
        
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': False, 'error': 'Search query required'}), 400
        
        # Search in name and description
        templates = Template.query.filter(
            Template.name.contains(query) | 
            Template.description.contains(query)
        ).order_by(Template.downloads.desc()).limit(20).all()
        
        return jsonify({
            'success': True,
            'query': query,
            'results': [t.to_dict() for t in templates],
            'count': len(templates)
        })
        
    except Exception as e:
        logger.error(f"API search error: {e}")
        return jsonify({'success': False, 'error': 'Search failed'}), 500

@api_bp.route('/user/profile')
@login_required
def get_user_profile():
    """Get current user profile"""
    try:
        return jsonify({
            'success': True,
            'user': current_user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"API user profile error: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch profile'}), 500

@api_bp.route('/user/downloads')
@login_required
def get_user_downloads():
    """Get user download history"""
    try:
        from app import Download
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)
        
        downloads = Download.query.filter_by(user_id=current_user.id)\
            .order_by(Download.downloaded_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'downloads': [{
                'id': d.id,
                'template': d.template.to_dict(),
                'downloaded_at': d.downloaded_at.isoformat()
            } for d in downloads.items],
            'pagination': {
                'page': downloads.page,
                'pages': downloads.pages,
                'per_page': downloads.per_page,
                'total': downloads.total
            }
        })
        
    except Exception as e:
        logger.error(f"API user downloads error: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch downloads'}), 500

@api_bp.route('/user/stats')
@login_required
def get_user_stats():
    """Get user statistics"""
    try:
        from app import Download
        
        total_downloads = Download.query.filter_by(user_id=current_user.id).count()
        
        # Downloads by industry
        industry_stats = {}
        downloads = Download.query.filter_by(user_id=current_user.id).all()
        for download in downloads:
            industry = download.template.industry
            industry_stats[industry] = industry_stats.get(industry, 0) + 1
        
        # Calculate remaining downloads for free users
        downloads_remaining = None
        if current_user.subscription_plan == 'free':
            downloads_remaining = max(0, 10 - current_user.downloads_used)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_downloads': total_downloads,
                'downloads_used': current_user.downloads_used,
                'downloads_remaining': downloads_remaining,
                'subscription_plan': current_user.subscription_plan,
                'subscription_status': current_user.subscription_status,
                'industry_breakdown': industry_stats,
                'member_since': current_user.created_at.isoformat() if current_user.created_at else None
            }
        })
        
    except Exception as e:
        logger.error(f"API user stats error: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch stats'}), 500

@api_bp.route('/ai/generate', methods=['POST'])
def ai_generate():
    """Generate AI template"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({
                'success': False, 
                'error': 'Prompt required'
            }), 400
        
        # Generate AI template (simplified version)
        result = generate_ai_template(prompt)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"AI generate error: {e}")
        return jsonify({'success': False, 'error': 'AI generation failed'}), 500

@api_bp.route('/ai/suggestions', methods=['POST'])
@login_required
def ai_suggestions():
    """Generate AI template suggestions"""
    try:
        data = request.get_json()
        industry = data.get('industry', '')
        project_type = data.get('project_type', '')
        description = data.get('description', '')
        
        if not industry or not project_type:
            return jsonify({
                'success': False, 
                'error': 'Industry and project type required'
            }), 400
        
        # Generate AI suggestions (simplified version)
        suggestions = generate_ai_suggestions(industry, project_type, description)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"AI suggestions error: {e}")
        return jsonify({'success': False, 'error': 'AI suggestions failed'}), 500

@api_bp.route('/templates/popular')
def get_popular_templates():
    """Get most popular templates"""
    try:
        from app import Template
        
        # Get top 10 most downloaded templates
        popular_templates = Template.query.order_by(Template.downloads.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'popular_templates': [t.to_dict() for t in popular_templates]
        })
        
    except Exception as e:
        logger.error(f"Popular templates error: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch popular templates'}), 500

@api_bp.route('/stats')
def get_platform_stats():
    """Get platform statistics"""
    try:
        from app import Template, User, Download, db
        
        # Get real stats from database
        total_templates = Template.query.count()
        total_users = User.query.count()
        total_downloads = Download.query.count()
        
        # Get unique counts
        industries_count = db.session.query(Template.industry).distinct().count()
        categories_count = db.session.query(Template.category).distinct().count()
        
        stats = {
            'total_templates': total_templates,
            'total_users': total_users,
            'total_downloads': total_downloads,
            'industries_count': industries_count,
            'categories_count': categories_count
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Platform stats error: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch stats'}), 500

def generate_ai_template(prompt):
    """Generate AI template based on prompt"""
    try:
        # Simplified AI template generation
        template_content = {
            'name': f'AI Generated Template: {prompt[:50]}...',
            'description': f'Custom template generated based on: {prompt}',
            'sections': [
                'Project Overview',
                'Objectives and Goals', 
                'Scope Definition',
                'Timeline and Milestones',
                'Resource Requirements',
                'Risk Assessment',
                'Success Criteria'
            ],
            'content': f'This template was generated based on your request: "{prompt}". It includes standard project management sections adapted to your specific needs.',
            'generated_at': '2025-10-10T10:53:00Z'
        }
        
        return template_content
        
    except Exception as e:
        logger.error(f"AI template generation error: {e}")
        return None

def generate_ai_suggestions(industry, project_type, description):
    """Generate AI-powered template suggestions"""
    try:
        # This is a simplified version. In production, integrate with OpenAI API
        suggestions = []
        
        base_templates = {
            'Technology': [
                'Software Development Project Charter',
                'Agile Sprint Planning Template',
                'Technical Risk Assessment',
                'API Documentation Template',
                'DevOps Pipeline Template'
            ],
            'Healthcare': [
                'Clinical Trial Project Plan',
                'HIPAA Compliance Checklist',
                'Medical Device Development',
                'Patient Safety Risk Register',
                'Healthcare Quality Metrics'
            ],
            'Construction': [
                'Construction Project Charter',
                'Safety Management Plan',
                'Material Procurement Template',
                'Site Inspection Checklist',
                'Construction Risk Matrix'
            ],
            'Finance': [
                'Financial Project Charter',
                'Budget Tracking Template',
                'Compliance Risk Assessment',
                'Audit Planning Template',
                'Investment Analysis Framework'
            ]
        }
        
        # Get templates for the industry
        industry_templates = base_templates.get(industry, [
            'Generic Project Charter',
            'Risk Management Template',
            'Stakeholder Analysis',
            'Project Timeline Template',
            'Budget Planning Template'
        ])
        
        # Create suggestions based on project type
        for i, template_name in enumerate(industry_templates[:5]):
            suggestions.append({
                'id': f'ai_suggestion_{i+1}',
                'name': template_name,
                'description': f'AI-generated {template_name.lower()} tailored for {industry.lower()} {project_type.lower()} projects.',
                'confidence': 0.9 - (i * 0.1),
                'industry': industry,
                'category': 'AI Generated',
                'estimated_time_savings': f'{20 + (i * 5)}-{30 + (i * 10)} hours'
            })
        
        return suggestions
        
    except Exception as e:
        logger.error(f"AI suggestion generation error: {e}")
        return []

"""
Template Routes
Handles template browsing, viewing, and downloading
"""

from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
import logging
import os
from datetime import datetime
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

templates_bp = Blueprint('templates', __name__, url_prefix='/templates')

@templates_bp.route('/')
@templates_bp.route('/browse')
def browse():
    """Browse all templates with filtering"""
    from models import Template
    
    # Get filter parameters
    industry = request.args.get('industry', '')
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    # Build query
    query = Template.query
    
    if industry:
        query = query.filter(Template.industry == industry)
    
    if category:
        query = query.filter(Template.category == category)
    
    if search:
        query = query.filter(
            (Template.name.ilike(f'%{search}%')) |
            (Template.description.ilike(f'%{search}%'))
        )
    
    # Get all matching templates (limit to 100 for performance)
    # Order by industry first (chronological), then by name within each industry
    templates = query.order_by(Template.industry, Template.name).all()
    
    # Get unique industries and categories for filters
    all_templates = Template.query.all()
    industries = sorted(list(set(t.industry for t in all_templates if t.industry)))
    categories = sorted(list(set(t.category for t in all_templates if t.category)))
    
    return render_template('templates/browse.html',
                         templates=templates,
                         industries=industries,
                         categories=categories,
                         current_industry=industry,
                         current_category=category,
                         current_search=search)

@templates_bp.route('/preview/<int:template_id>')
def preview(template_id):
    """Preview template before purchasing"""
    from models import Template
    
    template = Template.query.get_or_404(template_id)
    
    # Check if user has already purchased this template
    has_purchased = False
    if current_user.is_authenticated:
        from models import TemplatePurchase
        purchase = TemplatePurchase.query.filter_by(
            user_id=current_user.id,
            template_id=template_id
        ).first()
        has_purchased = purchase is not None
    
    return render_template('templates/preview.html',
                         template=template,
                         has_purchased=has_purchased)

@templates_bp.route('/<int:template_id>')
def detail(template_id):
    """View template details"""
    from models import Template
    
    template = Template.query.get_or_404(template_id)
    
    # Check if user has already purchased this template
    has_purchased = False
    if current_user.is_authenticated:
        from models import TemplatePurchase
        purchase = TemplatePurchase.query.filter_by(
            user_id=current_user.id,
            template_id=template_id
        ).first()
        has_purchased = purchase is not None
    
    return render_template('templates/detail.html',
                         template=template,
                         has_purchased=has_purchased)

@templates_bp.route('/download/<int:template_id>')
@login_required
def download(template_id):
    """Download a template (requires quota)"""
    from models import Template, TemplatePurchase
    from database import db
    from utils.subscription_security import check_usage_limit, track_usage
    
    template = Template.query.get_or_404(template_id)
    
    # Check if user has already purchased this specific template
    purchase = TemplatePurchase.query.filter_by(
        user_id=current_user.id,
        template_id=template_id
    ).first()
    
    if purchase:
        # User has purchased this template, allow download
        try:
            # Track the download
            template.downloads_count += 1
            db.session.commit()
            
            # Serve the file
            file_path = os.path.join('public/templates', template.file_path)
            if os.path.exists(file_path):
                return send_file(file_path,
                               as_attachment=True,
                               download_name=f"{template.name}.{template.file_format}")
            else:
                flash('Template file not found', 'error')
                return redirect(url_for('templates.detail', template_id=template_id))
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            flash('An error occurred while downloading', 'error')
            return redirect(url_for('templates.detail', template_id=template_id))
    
    # Check usage quota
    can_download, remaining, limit = check_usage_limit(current_user, 'downloads')
    
    if not can_download:
        flash(f'You have reached your download limit ({limit} per month). Please upgrade your plan or purchase this template individually.', 'warning')
        return redirect(url_for('payment.pricing'))
    
    # User has quota, proceed with download
    try:
        # Track usage
        current_user.downloads_this_month += 1
        template.downloads_count += 1
        
        # Create download record
        from models import DownloadHistory
        download_record = DownloadHistory(
            user_id=current_user.id,
            template_id=template_id,
            download_date=datetime.utcnow()
        )
        db.session.add(download_record)
        db.session.commit()
        
        # Serve the file
        file_path = os.path.join('public/templates', template.file_path)
        if os.path.exists(file_path):
            return send_file(file_path,
                           as_attachment=True,
                           download_name=f"{template.name}.{template.file_format}")
        else:
            flash('Template file not found', 'error')
            return redirect(url_for('templates.detail', template_id=template_id))
            
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        db.session.rollback()
        flash('An error occurred while downloading', 'error')
        return redirect(url_for('templates.detail', template_id=template_id))

@templates_bp.route('/thumbnail/<int:template_id>')
def thumbnail(template_id):
    """Serve template thumbnail image - REAL thumbnails only"""
    from models import Template
    
    template = Template.query.get_or_404(template_id)
    
    # Only serve real thumbnails that exist
    if template.thumbnail_path and os.path.exists(template.thumbnail_path):
        return send_file(template.thumbnail_path, mimetype='image/png')
    else:
        # If thumbnail doesn't exist, generate it on-the-fly from actual template file
        from utils.thumbnail_generator import ThumbnailGenerator
        from database import db
        
        if template.file_path and os.path.exists(template.file_path):
            generator = ThumbnailGenerator()
            thumbnail_path = generator.generate_thumbnail(
                template.file_path,
                template.id,
                template.file_format
            )
            
            if thumbnail_path:
                template.thumbnail_path = thumbnail_path
                db.session.commit()
                return send_file(thumbnail_path, mimetype='image/png')
        
        # If all else fails, return a branded "no preview" image
        default_thumb = os.path.join('static', 'images', 'no_preview.png')
        if os.path.exists(default_thumb):
            return send_file(default_thumb, mimetype='image/png')
        else:
            # Return 404 if no thumbnail can be generated
            from flask import abort
            abort(404)

@templates_bp.route('/favorite/<int:template_id>', methods=['POST'])
@login_required
def favorite(template_id):
    """Add/remove template from favorites"""
    from models import Template, Favorite
    from database import db
    
    template = Template.query.get_or_404(template_id)
    
    # Check if already favorited
    existing = Favorite.query.filter_by(
        user_id=current_user.id,
        template_id=template_id
    ).first()
    
    if existing:
        # Remove from favorites
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'status': 'removed', 'favorited': False})
    else:
        # Add to favorites
        favorite = Favorite(
            user_id=current_user.id,
            template_id=template_id
        )
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'status': 'added', 'favorited': True})

@templates_bp.route('/api/list')
def api_list():
    """API endpoint to list templates (for AJAX calls)"""
    from models import Template
    
    industry = request.args.get('industry', '')
    category = request.args.get('category', '')
    
    query = Template.query
    
    if industry:
        query = query.filter(Template.industry == industry)
    
    if category:
        query = query.filter(Template.category == category)
    
    templates = query.order_by(Template.name).all()
    
    return jsonify({
        'templates': [{
            'id': t.id,
            'name': t.name,
            'description': t.description,
            'category': t.category,
            'industry': t.industry,
            'file_format': t.file_format,
            'thumbnail_url': url_for('templates.thumbnail', template_id=t.id, _external=True),
            'detail_url': url_for('templates.detail', template_id=t.id, _external=True)
        } for t in templates]
    })


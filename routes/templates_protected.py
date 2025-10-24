"""
Protected Template Routes with Comprehensive Error Handling
This file adds error protection to all template operations
"""

from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
import logging
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from utils.error_protection import PlatformProtection

logger = logging.getLogger(__name__)

templates_bp = Blueprint('templates', __name__, url_prefix='/templates')

@templates_bp.route('/')
@templates_bp.route('/browse')
@PlatformProtection.safe_route(return_type='html')
def browse():
    """Browse all templates with filtering - PROTECTED"""
    from models import Template
    
    # Get filter parameters safely
    industry = PlatformProtection.safe_string_operation(lambda: request.args.get('industry', '').strip())
    category = PlatformProtection.safe_string_operation(lambda: request.args.get('category', '').strip())
    search = PlatformProtection.safe_string_operation(lambda: request.args.get('search', '').strip())
    
    logger.info(f"Browse filters - industry: '{industry}', category: '{category}', search: '{search}'")
    
    # Safe database query for templates
    def get_templates():
        if industry and category:
            # Try AND first
            query_and = Template.query.filter(
                (Template.industry == industry) & (Template.category == category)
            )
            if search:
                query_and = query_and.filter(
                    (Template.name.ilike(f'%{search}%')) |
                    (Template.description.ilike(f'%{search}%'))
                )
            templates = query_and.order_by(Template.industry, Template.name).all()
            
            # Fall back to industry only if no results
            if len(templates) == 0:
                query_industry = Template.query.filter(Template.industry == industry)
                if search:
                    query_industry = query_industry.filter(
                        (Template.name.ilike(f'%{search}%')) |
                        (Template.description.ilike(f'%{search}%'))
                    )
                templates = query_industry.order_by(Template.industry, Template.name).all()
        else:
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
            templates = query.order_by(Template.industry, Template.name).all()
        
        return templates
    
    templates = PlatformProtection.safe_database_query(Template, get_templates, default=[])
    
    # Safe database query for filters
    industries = PlatformProtection.safe_database_query(
        Template,
        lambda: sorted([i[0] for i in Template.query.with_entities(Template.industry).distinct().all() if i[0]]),
        default=[]
    )
    
    categories = PlatformProtection.safe_database_query(
        Template,
        lambda: sorted([c[0] for c in Template.query.with_entities(Template.category).distinct().all() if c[0]]),
        default=[]
    )
    
    return render_template('templates/browse.html',
                         templates=templates or [],
                         industries=industries or [],
                         categories=categories or [],
                         current_industry=industry,
                         current_category=category,
                         current_search=search)


@templates_bp.route('/download/<int:template_id>')
@login_required
@PlatformProtection.safe_route(return_type='redirect')
def download(template_id):
    """Download a template (requires quota) - PROTECTED"""
    from models import Template, TemplatePurchase, DownloadHistory
    from database import db
    from utils.subscription_security import check_usage_limit
    
    # Safely get template
    template = PlatformProtection.safe_database_query(
        Template,
        lambda: Template.query.get(template_id),
        default=None
    )
    
    if not template:
        flash('Template not found', 'error')
        return redirect(url_for('templates.browse'))
    
    # Validate template data
    is_valid, error_msg = PlatformProtection.validate_template_data(template)
    if not is_valid:
        logger.error(f"Invalid template data for ID {template_id}: {error_msg}")
        flash('Template data is incomplete. Please contact support.', 'error')
        return redirect(url_for('templates.browse'))
    
    # Check if user has purchased this template
    purchase = PlatformProtection.safe_database_query(
        TemplatePurchase,
        lambda: TemplatePurchase.query.filter_by(
            user_id=current_user.id,
            template_id=template_id
        ).first(),
        default=None
    )
    
    if purchase:
        # User has purchased, allow download
        file_path, error = PlatformProtection.safe_template_file_access(template.file_path)
        
        if error:
            flash(f'Cannot download template: {error}', 'error')
            return redirect(url_for('templates.detail', template_id=template_id))
        
        try:
            # Track download
            template.downloads_count = (template.downloads_count or 0) + 1
            db.session.commit()
            
            # Serve file
            return send_file(file_path,
                           as_attachment=True,
                           download_name=f"{template.name}.{template.file_format}")
        except Exception as e:
            logger.error(f"Download error for template {template_id}: {str(e)}")
            db.session.rollback()
            flash('An error occurred while downloading. Please try again.', 'error')
            return redirect(url_for('templates.detail', template_id=template_id))
    
    # Check usage quota
    try:
        can_download, remaining, limit = check_usage_limit(current_user, 'downloads')
    except Exception as e:
        logger.error(f"Error checking usage limit: {str(e)}")
        can_download, remaining, limit = False, 0, 0
    
    if not can_download:
        flash(f'You have reached your download limit ({limit} per month). Please upgrade your plan or purchase this template individually.', 'warning')
        return redirect(url_for('payment.pricing'))
    
    # User has quota, proceed with download
    file_path, error = PlatformProtection.safe_template_file_access(template.file_path)
    
    if error:
        flash(f'Cannot download template: {error}', 'error')
        return redirect(url_for('templates.detail', template_id=template_id))
    
    try:
        # Track usage
        current_user.downloads_this_month = (current_user.downloads_this_month or 0) + 1
        template.downloads_count = (template.downloads_count or 0) + 1
        
        # Create download record
        download_record = DownloadHistory(
            user_id=current_user.id,
            template_id=template_id,
            download_date=datetime.utcnow()
        )
        db.session.add(download_record)
        db.session.commit()
        
        # Serve file
        return send_file(file_path,
                       as_attachment=True,
                       download_name=f"{template.name}.{template.file_format}")
        
    except Exception as e:
        logger.error(f"Download error for template {template_id}: {str(e)}")
        db.session.rollback()
        flash('An error occurred while downloading. Please try again or contact support.', 'error')
        return redirect(url_for('templates.detail', template_id=template_id))


@templates_bp.route('/detail/<int:template_id>')
@PlatformProtection.safe_route(return_type='html')
def detail(template_id):
    """View template details - PROTECTED"""
    from models import Template
    
    template = PlatformProtection.safe_database_query(
        Template,
        lambda: Template.query.get(template_id),
        default=None
    )
    
    if not template:
        flash('Template not found', 'error')
        return redirect(url_for('templates.browse'))
    
    # Validate template data
    is_valid, error_msg = PlatformProtection.validate_template_data(template)
    if not is_valid:
        logger.error(f"Invalid template data for ID {template_id}: {error_msg}")
        flash('Template data is incomplete. Please contact support.', 'error')
        return redirect(url_for('templates.browse'))
    
    # Check if file exists
    file_path, error = PlatformProtection.safe_template_file_access(template.file_path)
    file_exists = (file_path is not None)
    
    if not file_exists:
        logger.warning(f"Template {template_id} file missing: {error}")
    
    return render_template('templates/detail.html',
                         template=template,
                         file_exists=file_exists)


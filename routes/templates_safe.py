"""
Safe Template Routes with comprehensive error handling
"""

from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

templates_bp = Blueprint('templates', __name__, url_prefix='/templates')

@templates_bp.route('/')
@templates_bp.route('/browse')
def browse():
    """Browse all templates with filtering - SAFE VERSION"""
    try:
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
        
        # Get all matching templates
        templates = query.order_by(Template.industry, Template.name).limit(100).all()
        
        # Get unique industries and categories for filters
        all_templates = Template.query.all()
        industries = sorted(list(set(t.industry for t in all_templates if t.industry)))
        categories = sorted(list(set(t.category for t in all_templates if t.category)))
        
        logger.info(f"Browse: {len(templates)} templates, {len(industries)} industries, {len(categories)} categories")
        
        return render_template('templates/browse.html',
                             templates=templates,
                             industries=industries,
                             categories=categories,
                             current_industry=industry,
                             current_category=category,
                             current_search=search)
    
    except Exception as e:
        logger.error(f"Browse error: {str(e)}", exc_info=True)
        # Return error page with details
        return render_template('errors/500.html', error=str(e)), 500


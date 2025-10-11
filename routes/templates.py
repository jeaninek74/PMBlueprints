
"""
Templates Routes
Handles template browsing, searching, and downloading
"""

from flask import Blueprint, render_template, request, jsonify, send_file, abort
from flask_login import login_required, current_user
import os
import logging
from sqlalchemy import func

logger = logging.getLogger(__name__)

templates_bp = Blueprint('templates', __name__)

@templates_bp.route('/')
def browse():
    """Browse all templates"""
    try:
        # Import here to avoid circular imports
        from app import db, Template, init_db
        
        # Ensure database is initialized
        try:
            # Test if templates table exists by trying to count
            Template.query.count()
        except Exception:
            # If table doesn't exist, initialize database
            logger.info("Database not initialized, initializing now...")
            init_db()

        # Get filter parameters
        industry = request.args.get('industry')
        category = request.args.get('category')
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = 12

        # Build the query
        query = Template.query

        if industry:
            query = query.filter(Template.industry == industry)

        if category:
            query = query.filter(Template.category == category)

        if search:
            search_term = f"%{search}%"
            query = query.filter(Template.name.ilike(search_term) | Template.description.ilike(search_term))

        # Paginate the results
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Get unique industries and categories for filters
        industries = [row[0] for row in db.session.query(Template.industry).distinct().order_by(Template.industry).all()]
        categories = [row[0] for row in db.session.query(Template.category).distinct().order_by(Template.category).all()]

        return render_template('templates/browse.html',
                             templates=pagination,
                             industries=industries,
                             categories=categories,
                             current_industry=industry,
                             current_category=category,
                             current_search=search)

    except Exception as e:
        logger.error(f"Template browse error: {e}")
        # Create a mock pagination object to prevent template errors
        class MockPagination:
            def __init__(self):
                self.items = []
                self.pages = 0
                self.page = 1
                self.per_page = 12
                self.total = 0
                self.has_next = False
                self.has_prev = False
        
        mock_pagination = MockPagination()
        
        return render_template('templates/browse.html',
                             templates=mock_pagination,
                             industries=[],
                             categories=[],
                             current_industry=None,
                             current_category=None,
                             current_search='',
                             error_message="Unable to load templates. Please try again later.")

@templates_bp.route('/<int:template_id>')
def detail(template_id):
    """Template detail page"""
    try:
        # Import here to avoid circular imports
        from app import Template, db
        
        template = Template.query.get_or_404(template_id)

        # Get related templates (same industry, different template)
        related = Template.query.filter(
            Template.industry == template.industry,
            Template.id != template.id
        ).limit(4).all()

        return render_template('templates/detail.html',
                             template=template,
                             related=related)

    except Exception as e:
        logger.error(f"Template detail error for template_id {template_id}: {e}")
        # Return a user-friendly error page
        abort(404)

@templates_bp.route('/<int:template_id>/download')
@login_required
def download(template_id):
    """Download template file"""
    try:
        # Import here to avoid circular imports
        from app import db, Template, Download
        
        template = Template.query.get_or_404(template_id)

        # Check if user can download
        if not current_user.can_download():
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Download limit reached. Please upgrade your plan.'
                }), 403

            return render_template('templates/upgrade_required.html',
                                 template=template)

        # Check if premium template requires subscription
        if template.is_premium and current_user.subscription_plan == 'free':
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Premium template requires paid subscription.'
                }), 403

            return render_template('templates/upgrade_required.html',
                                 template=template)

        # Create download record
        download_record = Download(
            user_id=current_user.id,
            template_id=template.id
        )
        db.session.add(download_record)

        # Update user download count
        if current_user.subscription_plan == 'free':
            current_user.downloads_used += 1

        # Update template download count
        template.downloads += 1

        db.session.commit()
        
        # Track download in monitoring system
        from monitoring import track_template_download
        track_template_download(template_id)

        # Serve actual template file - use relative path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(base_dir, 'static', 'templates', template.filename)

        if not os.path.exists(template_path):
            logger.error(f"Template file not found: {template_path}")
            if request.is_json:
                return jsonify({'success': False, 'error': 'Template file not found'}), 404
            abort(404)

        logger.info(f"Template downloaded: {template.name} by {current_user.email}")

        return send_file(
            template_path,
            as_attachment=True,
            download_name=template.filename
        )

    except Exception as e:
        logger.error(f"Template download error: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'Download failed'}), 500
        abort(500)


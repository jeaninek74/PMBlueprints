
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
        from app import db, Template
        
        logger.info("Templates browse route called")
        
        # Test database connection
        template_count = Template.query.count()
        logger.info(f"Database connection successful. Found {template_count} templates")

        # Get filter parameters
        industry = request.args.get('industry')
        category = request.args.get('category')
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = 12

        logger.info(f"Filters - Industry: {industry}, Category: {category}, Search: {search}, Page: {page}")

        # Build the query
        query = Template.query

        if industry:
            query = query.filter(Template.industry == industry)
            logger.info(f"Filtered by industry: {industry}")

        if category:
            query = query.filter(Template.category == category)
            logger.info(f"Filtered by category: {category}")

        if search:
            search_term = f"%{search}%"
            query = query.filter(Template.name.ilike(search_term) | Template.description.ilike(search_term))
            logger.info(f"Filtered by search: {search}")

        # Get total count before pagination
        total_count = query.count()
        logger.info(f"Query returned {total_count} templates")

        # Paginate the results
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        logger.info(f"Pagination: {len(pagination.items)} items on page {page} of {pagination.pages}")

        # Get unique industries and categories for filters
        industries = [row[0] for row in db.session.query(Template.industry).distinct().order_by(Template.industry).all()]
        categories = [row[0] for row in db.session.query(Template.category).distinct().order_by(Template.category).all()]
        
        logger.info(f"Found {len(industries)} industries and {len(categories)} categories")

        return render_template('templates/browse.html',
                             templates=pagination,
                             industries=industries,
                             categories=categories,
                             current_industry=industry,
                             current_category=category,
                             current_search=search)

    except Exception as e:
        logger.error(f"CRITICAL: Template browse error: {e}", exc_info=True)
        
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
        
        error_details = f"Database Error: {str(e)}"
        logger.error(f"Returning error page with message: {error_details}")
        
        return render_template('templates/browse.html',
                             templates=mock_pagination,
                             industries=[],
                             categories=[],
                             current_industry=None,
                             current_category=None,
                             current_search='',
                             error_message=error_details)

@templates_bp.route('/<int:template_id>')
def detail(template_id):
    """Template detail page"""
    try:
        # Import here to avoid circular imports
        from app import Template, db
        
        logger.info(f"Attempting to load template {template_id}")
        
        template = Template.query.get(template_id)
        
        if not template:
            logger.warning(f"Template {template_id} not found in database")
            abort(404)
        
        logger.info(f"Template {template_id} found: {template.name}")

        # Get related templates (same industry, different template)
        try:
            related = Template.query.filter(
                Template.industry == template.industry,
                Template.id != template.id
            ).limit(4).all()
            logger.info(f"Found {len(related)} related templates")
        except Exception as e:
            logger.error(f"Error fetching related templates: {e}")
            related = []

        return render_template('templates/detail.html',
                             template=template,
                             related=related)

    except Exception as e:
        logger.error(f"Template detail error for template_id {template_id}: {str(e)}", exc_info=True)
        # Return a user-friendly error page
        abort(500)

@templates_bp.route('/<int:template_id>/download')
def download(template_id):
    """Download template file"""
    try:
        # Import here to avoid circular imports
        from app import db, Template, Download
        from flask import session
        
        template = Template.query.get_or_404(template_id)

        # Check if user can download (only if logged in)
        if current_user.is_authenticated and not current_user.can_download():
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

        # Create download record (only if logged in)
        if current_user.is_authenticated:
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
        
        # Track download in monitoring system (non-blocking)
        try:
            from monitoring import track_template_download
            track_template_download(template_id)
        except Exception as monitor_error:
            logger.warning(f"Monitoring tracking failed (non-critical): {monitor_error}")

        # Log the download
        user_email = current_user.email if current_user.is_authenticated else 'anonymous'
        logger.info(f"Template downloaded: {template.name} by {user_email}")
        
        # Serve file from static/templates directory using send_from_directory
        from flask import send_from_directory
        import os
        
        # Get absolute path to templates directory
        # Try public/templates first (Railway), then fall back to static/templates (Vercel)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        templates_dir = os.path.join(base_dir, 'public', 'templates')
        if not os.path.exists(templates_dir):
            templates_dir = os.path.join(base_dir, 'static', 'templates')
        
        # Debug logging
        logger.info(f"Base dir: {base_dir}")
        logger.info(f"Templates dir: {templates_dir}")
        logger.info(f"Looking for file: {template.filename}")
        logger.info(f"Templates dir exists: {os.path.exists(templates_dir)}")
        if os.path.exists(templates_dir):
            logger.info(f"Files in templates dir: {os.listdir(templates_dir)[:10]}")
        
        # Check if file exists
        file_path = os.path.join(templates_dir, template.filename)
        if not os.path.exists(file_path):
            logger.error(f"Template file not found: {file_path}")
            if request.is_json:
                return jsonify({"error": "Template file not found"}), 404
            flash("Template file not found", "error")
            return redirect(url_for('templates_bp.browse'))
        
        return send_from_directory(
            templates_dir,
            template.filename,
            as_attachment=True,
            download_name=template.filename
        )

    except Exception as e:
        logger.error(f"Template download error: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'Download failed'}), 500
        abort(500)


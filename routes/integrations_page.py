"""
Platform Integrations Page Routes
"""
from flask import Blueprint, render_template
from flask_login import login_required

integrations_page_bp = Blueprint('integrations_page', __name__)

@integrations_page_bp.route('/integrations')
@login_required
def integrations():
    """Display platform integrations page"""
    return render_template('integrations.html')


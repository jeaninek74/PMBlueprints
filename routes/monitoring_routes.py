"""
Monitoring Dashboard Routes
Provides access to performance monitoring dashboard
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

monitoring_routes_bp = Blueprint('monitoring_routes', __name__)

@monitoring_routes_bp.route('/dashboard')
@login_required
def monitoring_dashboard():
    """
    Performance monitoring dashboard
    Requires authentication (admin users only in production)
    """
    # In production, you might want to restrict this to admin users only
    # if not current_user.is_admin:
    #     abort(403)
    
    return render_template('monitoring_dashboard.html')


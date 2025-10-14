"""
Updated Template Download Route Using Supabase Storage
=======================================================

This file contains the updated download route that fetches templates
from Supabase Storage instead of local filesystem.

To use this:
1. Upload templates to Supabase using upload_templates_to_supabase.py
2. Replace the download function in routes/templates.py with this one
3. Add Supabase initialization at the top of routes/templates.py
"""

import os
import io
import logging
from flask import jsonify, send_file, request, render_template, session, redirect
from flask_login import current_user

# Supabase initialization (add this at the top of routes/templates.py)
try:
    from supabase import create_client, Client
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
    
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        STORAGE_ENABLED = True
        logger.info("✅ Supabase storage initialized")
    else:
        STORAGE_ENABLED = False
        logger.warning("⚠️  Supabase credentials not set")
except ImportError:
    STORAGE_ENABLED = False
    logger.warning("⚠️  Supabase package not installed")

logger = logging.getLogger(__name__)

# Updated download function
def download(template_id):
    """Download template file from Supabase Storage"""
    try:
        # Import here to avoid circular imports
        from app import db, Template, Download
        
        template = Template.query.get_or_404(template_id)

        # Check if user can download (only if logged in)
        if current_user.is_authenticated and not current_user.can_download():
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Download limit reached. Please upgrade your plan.',
                    'upgrade_required': True,
                    'current_plan': current_user.subscription_plan,
                    'downloads_used': current_user.downloads_used,
                    'download_limit': current_user.get_download_limit()
                }), 403

            return render_template('templates/upgrade_required.html',
                                 template=template)

        # Check if premium template requires subscription
        if template.is_premium and current_user.is_authenticated and current_user.subscription_plan == 'free':
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Premium template requires paid subscription.',
                    'upgrade_required': True
                }), 403

            return render_template('templates/upgrade_required.html',
                                 template=template)

        # Check if storage is enabled
        if not STORAGE_ENABLED:
            logger.error("Supabase storage not configured")
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Template downloads are temporarily unavailable. Please try again later.'
                }), 503
            return render_template('error.html',
                                 error='Template downloads are temporarily unavailable'), 503

        # Get file from Supabase Storage
        try:
            # Get public URL
            file_url = supabase.storage.from_('templates').get_public_url(template.filename)
            
            if not file_url:
                raise Exception("Failed to get file URL")
            
            # Option 1: Redirect to Supabase URL (fastest, uses Supabase CDN)
            # Uncomment this for direct redirect:
            # return redirect(file_url)
            
            # Option 2: Download and serve (more control, tracks downloads)
            file_data = supabase.storage.from_('templates').download(template.filename)
            
            if not file_data:
                raise Exception("Failed to download file")
            
        except Exception as e:
            logger.error(f"Supabase storage error for {template.filename}: {e}")
            if request.is_json:
                return jsonify({'success': False, 'error': 'Template file not found'}), 404
            return render_template('error.html',
                                 error='Template file not found'), 404

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
            elif current_user.subscription_plan == 'professional':
                current_user.downloads_used += 1
        
        # Update template download count
        template.downloads += 1
        db.session.commit()
        
        # Track download in monitoring system
        try:
            from monitoring import track_template_download
            track_template_download(template_id)
        except:
            pass  # Monitoring is optional

        # Determine MIME type
        file_ext = template.filename.lower().split('.')[-1]
        mime_types = {
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'pdf': 'application/pdf',
            'xls': 'application/vnd.ms-excel',
            'doc': 'application/msword',
            'ppt': 'application/vnd.ms-powerpoint'
        }
        mime_type = mime_types.get(file_ext, 'application/octet-stream')

        user_email = current_user.email if current_user.is_authenticated else 'anonymous'
        logger.info(f"Template downloaded: {template.name} by {user_email}")

        # Send file to user
        return send_file(
            io.BytesIO(file_data),
            as_attachment=True,
            download_name=template.filename,
            mimetype=mime_type
        )

    except Exception as e:
        logger.error(f"Template download error: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'Download failed'}), 500
        return render_template('error.html',
                             error='Download failed. Please try again.'), 500


# Helper method to add to User model in app.py
def get_download_limit(self):
    """Get download limit based on subscription plan"""
    limits = {
        'free': 3,
        'professional': 10,
        'enterprise': 999999  # Unlimited
    }
    return limits.get(self.subscription_plan, 3)


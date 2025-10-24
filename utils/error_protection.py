"""
Comprehensive Error Protection for PMBlueprints Platform
Prevents crashes and provides graceful error handling
"""

import logging
import os
import traceback
from functools import wraps
from flask import jsonify, render_template, flash, redirect, url_for, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

class PlatformProtection:
    """Centralized error protection for the entire platform"""
    
    @staticmethod
    def safe_file_operation(func):
        """Decorator to protect file operations from crashes"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                logger.error(f"File not found in {func.__name__}: {str(e)}")
                return None
            except PermissionError as e:
                logger.error(f"Permission denied in {func.__name__}: {str(e)}")
                return None
            except OSError as e:
                logger.error(f"OS error in {func.__name__}: {str(e)}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
                return None
        return wrapper
    
    @staticmethod
    def safe_database_operation(func):
        """Decorator to protect database operations from crashes"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            from database import db
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Database error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
                try:
                    db.session.rollback()
                except:
                    pass
                return None
        return wrapper
    
    @staticmethod
    def safe_route(return_type='html'):
        """
        Decorator to protect Flask routes from crashes
        return_type: 'html', 'json', or 'redirect'
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except HTTPException as e:
                    # Let Flask handle HTTP exceptions normally
                    raise
                except Exception as e:
                    logger.error(f"Route error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
                    
                    if return_type == 'json':
                        return jsonify({
                            'success': False,
                            'error': 'An unexpected error occurred. Please try again or contact support.',
                            'details': str(e) if os.getenv('FLASK_ENV') == 'development' else None
                        }), 500
                    elif return_type == 'redirect':
                        flash('An unexpected error occurred. Please try again.', 'error')
                        return redirect(url_for('main.index'))
                    else:  # html
                        return render_template('error.html',
                                             error_message='An unexpected error occurred',
                                             error_details=str(e) if os.getenv('FLASK_ENV') == 'development' else None), 500
            return wrapper
        return decorator
    
    @staticmethod
    def safe_template_file_access(file_path):
        """Safely access template files with comprehensive checks"""
        try:
            # Check if path is provided
            if not file_path:
                logger.error("No file path provided")
                return None, "Template file path is missing"
            
            # Build full path
            full_path = os.path.join('public/templates', file_path)
            
            # Check if file exists
            if not os.path.exists(full_path):
                logger.error(f"Template file not found: {full_path}")
                return None, "Template file not found"
            
            # Check if it's actually a file
            if not os.path.isfile(full_path):
                logger.error(f"Path is not a file: {full_path}")
                return None, "Invalid template file"
            
            # Check file size
            file_size = os.path.getsize(full_path)
            if file_size == 0:
                logger.error(f"Template file is empty: {full_path}")
                return None, "Template file is corrupted (empty)"
            
            # Check file size is reasonable (not too large)
            max_size = 50 * 1024 * 1024  # 50MB
            if file_size > max_size:
                logger.error(f"Template file too large: {full_path} ({file_size} bytes)")
                return None, "Template file is too large"
            
            # Check file permissions
            if not os.access(full_path, os.R_OK):
                logger.error(f"Cannot read template file: {full_path}")
                return None, "Template file is not accessible"
            
            return full_path, None
            
        except Exception as e:
            logger.error(f"Error accessing template file: {str(e)}\n{traceback.format_exc()}")
            return None, "Error accessing template file"
    
    @staticmethod
    def safe_database_query(model, query_func, default=None):
        """Safely execute database queries with error handling"""
        from database import db
        try:
            return query_func()
        except Exception as e:
            logger.error(f"Database query error for {model.__name__}: {str(e)}\n{traceback.format_exc()}")
            try:
                db.session.rollback()
            except:
                pass
            return default
    
    @staticmethod
    def safe_api_call(api_name, api_func, *args, **kwargs):
        """Safely call external APIs with error handling"""
        try:
            return api_func(*args, **kwargs), None
        except TimeoutError as e:
            logger.error(f"{api_name} API timeout: {str(e)}")
            return None, f"{api_name} service is currently unavailable (timeout)"
        except ConnectionError as e:
            logger.error(f"{api_name} API connection error: {str(e)}")
            return None, f"Cannot connect to {api_name} service"
        except Exception as e:
            logger.error(f"{api_name} API error: {str(e)}\n{traceback.format_exc()}")
            return None, f"{api_name} service error: {str(e)}"
    
    @staticmethod
    def validate_template_data(template):
        """Validate template object has all required fields"""
        required_fields = ['id', 'name', 'file_path', 'industry', 'category']
        missing_fields = []
        
        for field in required_fields:
            if not hasattr(template, field) or getattr(template, field) is None:
                missing_fields.append(field)
        
        if missing_fields:
            logger.error(f"Template {template.id if hasattr(template, 'id') else 'unknown'} missing fields: {missing_fields}")
            return False, f"Template data is incomplete (missing: {', '.join(missing_fields)})"
        
        return True, None
    
    @staticmethod
    def safe_integer_conversion(value, default=0):
        """Safely convert value to integer"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_string_operation(func, *args, **kwargs):
        """Safely execute string operations"""
        try:
            return func(*args, **kwargs)
        except (AttributeError, TypeError, ValueError) as e:
            logger.error(f"String operation error: {str(e)}")
            return ""
    
    @staticmethod
    def check_directory_exists(directory_path, create_if_missing=False):
        """Check if directory exists and optionally create it"""
        try:
            if os.path.exists(directory_path):
                return True, None
            
            if create_if_missing:
                os.makedirs(directory_path, exist_ok=True)
                logger.info(f"Created directory: {directory_path}")
                return True, None
            else:
                logger.error(f"Directory not found: {directory_path}")
                return False, "Directory not found"
                
        except Exception as e:
            logger.error(f"Directory check error: {str(e)}\n{traceback.format_exc()}")
            return False, f"Directory error: {str(e)}"
    
    @staticmethod
    def safe_json_response(data=None, success=True, error=None, status_code=200):
        """Create safe JSON response with consistent format"""
        response = {
            'success': success,
            'data': data,
            'error': error
        }
        return jsonify(response), status_code


# Global error handlers for Flask app
def register_error_handlers(app):
    """Register global error handlers for the Flask app"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Resource not found'}), 404
        return render_template('error.html', error_message='Page not found', error_code=404), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from database import db
        try:
            db.session.rollback()
        except:
            pass
        logger.error(f"Internal server error: {str(error)}\n{traceback.format_exc()}")
        
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
        return render_template('error.html', error_message='Internal server error', error_code=500), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Access forbidden'}), 403
        return render_template('error.html', error_message='Access forbidden', error_code=403), 403
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        from database import db
        try:
            db.session.rollback()
        except:
            pass
        logger.error(f"Unexpected error: {str(error)}\n{traceback.format_exc()}")
        
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500
        return render_template('error.html', error_message='An unexpected error occurred', error_code=500), 500


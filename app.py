"""
PMBlueprints Production Platform
Professional Project Management Templates Platform
Production-Ready Implementation
Version: 1.0.1 - Login and Preview fixes
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for, flash, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import secrets
import stripe
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Configure WhiteNoise for serving static files in production
from whitenoise import WhiteNoise
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='static/')
app.wsgi_app.add_files('static/thumbnails/', prefix='static/thumbnails/')

# Production Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Disable template caching in production to ensure updates are visible
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Use Vercel Neon PostgreSQL for production, SQLite for local development
# Vercel sets POSTGRES_URL when Neon database is connected
DATABASE_URL = os.getenv('POSTGRES_URL') or os.getenv('DATABASE_URL', 'sqlite:///pmblueprints.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# PostgreSQL-specific connection pooling
if DATABASE_URL.startswith('postgres'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
    }
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Session Configuration for Vercel Serverless
# Use Redis for session storage (required for serverless)
redis_url = os.getenv('REDIS_URL', None)
if redis_url:
    logger.info("Configuring Redis-backed sessions")
    import redis
    from flask_session import Session
    
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = redis.from_url(redis_url)
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'pmb:'
else:
    logger.warning("REDIS_URL not set, using filesystem sessions (not recommended for production)")
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = '/tmp/flask_sessions'
    app.config['SESSION_PERMANENT'] = True

app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Important for Vercel
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 7 day sessions
app.config['SESSION_COOKIE_NAME'] = 'pmblueprints_session'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)  # Remember me for 30 days
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

# Stripe Configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_dummy_key')
app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_dummy_key')

# Initialize database
from database import db

# Import models after db is imported
from models import User, Template, DownloadHistory, AIGeneratorHistory, AISuggestionHistory, TemplatePurchase, Payment, IntegrationSettings, Favorite

# Initialize database with app
db.init_app(app)

# Auto-create tables on startup
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created/verified")
        if Template.query.count() == 0:
            import json
            with open('templates_catalog.json', 'r') as f:
                templates = json.load(f)
            for t in templates:
                template = Template(id=t.get("id"), name=t.get("name"), description=t.get("description"), industry=t.get("industry"), category=t.get("category"), file_format=t.get("file_type"), file_path=t.get("filename"))
                db.session.add(template)
            db.session.commit()
            logger.info(f"Database populated with {Template.query.count()} templates")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

# Initialize other extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this feature.'
login_manager.login_message_category = 'info'
CORS(app)

# Initialize Flask-Session (must be after app config)
if redis_url:
    from flask_session import Session
    Session(app)
    logger.info("Flask-Session initialized with Redis backend")
else:
    logger.warning("Flask-Session using filesystem backend")

# Initialize performance monitoring
from monitoring import monitor
monitor.init_app(app)

# Note: Upload directory creation removed for serverless compatibility
# All models are now imported from models.py

@login_manager.user_loader
def load_user(user_id):
    logger.info(f"Loading user with ID: {user_id}")
    user = User.query.get(int(user_id))
    if user:
        logger.info(f"User loaded: {user.email}")
    else:
        logger.warning(f"User not found for ID: {user_id}, clearing stale session")
        # Clear the stale session
        from flask import session
        session.clear()
    return user

# Session debugging and management
@app.before_request
def manage_session():
    """Ensure session is properly initialized and logged"""
    logger.info(f"Request: {request.method} {request.path}")
    logger.info(f"Session exists: {bool(session)}")
    logger.info(f"Session ID: {session.get('_id', 'NO_SESSION_ID')}")
    logger.info(f"User authenticated: {current_user.is_authenticated}")
    if current_user.is_authenticated:
        logger.info(f"Current user: {current_user.email} (ID: {current_user.id})")
        # Ensure session is marked as modified to force save
        session.modified = True

@app.after_request
def save_session(response):
    """Ensure session is saved and cookie is set"""
    logger.info(f"Response: {response.status_code}")
    cookie_header = response.headers.get('Set-Cookie')
    if cookie_header:
        logger.info(f"Set-Cookie: {cookie_header[:100]}...")  # Log first 100 chars
    else:
        logger.warning("No Set-Cookie header in response")
    return response

# Import blueprints (with error handling)
try:
    from routes.auth import auth_bp
    from routes.templates import templates_bp
    from routes.payment import payment_bp
    from routes.api import api_bp
    from routes.search_api import search_api_bp
    from routes.ai_generation import ai_bp
    from routes.ai_suggestions import ai_suggestions_bp
    from routes.serve_thumbnails import serve_thumbnails_bp
    from routes.integrations import integrations_bp
    from routes.integrations_page import integrations_page_bp
    from routes.monitoring_routes import monitoring_routes_bp
    from routes.favorites import favorites_bp
    from routes.health import health_bp
    from routes.setup import setup_bp
    from routes.ai_download import ai_download_bp
    from routes.update_industries import update_industries_bp
    from routes.admin_update import admin_bp as admin_update_bp
    from routes.admin_fix_templates import admin_fix_bp
    from routes.ai_generator_advanced import ai_gen_bp as ai_generator_bp
    from routes.payment_secure import payment_secure_bp
    from routes.ai_generation_secure import ai_secure_bp
    from routes.init_db import init_db_bp
    from routes.fix_names import fix_names_bp
    from routes.fix_template_names import fix_template_names_bp
    from routes.fix_actual_industries import fix_actual_industries_bp
    from routes.fix_all_templates import fix_all_templates_bp
    from routes.fix_database_names import fix_database_names_bp
    # from routes.update_thumbnails import update_thumbnails_bp
    from routes.admin_thumbnails import admin_thumbnails_bp
    from routes.alacarte_payment import alacarte_bp
    from routes.migrate import migrate_bp
    from routes.admin import admin_bp
    
    # Initialize OAuth (optional - only if credentials are set)
    try:
        from oauth_config import init_oauth
        from routes.oauth import init_oauth_routes
        if os.getenv('GOOGLE_CLIENT_ID') or os.getenv('APPLE_CLIENT_ID'):
            oauth = init_oauth(app)
            oauth_bp = init_oauth_routes(app, oauth)
            logger.info("OAuth initialized successfully")
        else:
            logger.info("OAuth credentials not set, skipping OAuth initialization")
    except Exception as e:
        logger.warning(f"OAuth initialization skipped: {e}")
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(templates_bp, url_prefix='/templates')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(search_api_bp, url_prefix='/api/search')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(ai_suggestions_bp, url_prefix='/ai_suggestions')  # AI suggestions page and API
    app.register_blueprint(serve_thumbnails_bp)  # Serve thumbnail files
    app.register_blueprint(integrations_bp, url_prefix='/integrations')
    app.register_blueprint(integrations_page_bp)  # Integrations settings page
    app.register_blueprint(monitoring_routes_bp, url_prefix='/monitoring')
    app.register_blueprint(favorites_bp)  # No prefix, routes have /api/ in them
    app.register_blueprint(health_bp)  # Health check routes
    app.register_blueprint(setup_bp)  # Setup and database initialization routes
    app.register_blueprint(ai_download_bp)  # AI template download routes
    app.register_blueprint(ai_generator_bp)
    app.register_blueprint(update_industries_bp)  # Update industries route
    app.register_blueprint(admin_update_bp)  # Admin update routes
    app.register_blueprint(admin_fix_bp)  # Admin fix templates
    app.register_blueprint(payment_secure_bp)  # Secure payment routes
    app.register_blueprint(ai_secure_bp, url_prefix='/api/ai')  # Secure AI routes
    app.register_blueprint(init_db_bp)  # Database initialization routes
    app.register_blueprint(fix_names_bp)  # Fix template and industry names
    app.register_blueprint(fix_template_names_bp)  # Fix template names from filenames
    app.register_blueprint(fix_actual_industries_bp)  # Fix actual incorrect industry names
    app.register_blueprint(fix_all_templates_bp)  # Fix all template and industry issues
    app.register_blueprint(fix_database_names_bp)  # Fix database names directly
    # app.register_blueprint(update_thumbnails_bp)  # Update thumbnail URLs
    app.register_blueprint(admin_thumbnails_bp)  # Admin thumbnail update route
    app.register_blueprint(alacarte_bp)  # À la carte template purchases
    app.register_blueprint(migrate_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')  # Database migration routes
    logger.info("All blueprints registered successfully (including OAuth, AI download, update industries, favorites, ratings, health, setup, secure payment/AI routes, and migrations)")
except ImportError as e:
    logger.warning(f"Blueprint import error: {e}. Using inline routes.")

# SEO routes
@app.route('/robots.txt')
def robots():
    """Serve robots.txt"""
    return send_from_directory(app.static_folder, 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    """Serve sitemap.xml"""
    return send_from_directory(app.static_folder, 'sitemap.xml', mimetype='application/xml')

# Main routes
@app.route('/')
def index():
    """Homepage"""
    try:
        # Get statistics from database using SQLAlchemy
        total_templates = Template.query.count()
        
        # Get distinct industries
        industries = db.session.query(Template.industry).distinct().all()
        industries = sorted([i[0] for i in industries if i[0]])
        industries_count = len(industries)
        
        # Get distinct categories
        categories = db.session.query(Template.category).distinct().all()
        categories = sorted([c[0] for c in categories if c[0]])
        categories_count = len(categories)
        
        # If database is empty, use fallback values
        if total_templates == 0:
            total_templates = "960+"
            industries_count = 30
            categories_count = 19
            industries = ["Technology", "Healthcare", "Construction", "Finance", "Manufacturing", "Education"]
            categories = ["Project Planning", "Risk Management", "Quality Assurance", "Resource Management", "Communication"]
        
        stats = {
            'total_templates': total_templates,
            'total_files': "1,594",  # Total files including all formats
            'industries_count': industries_count,
            'categories_count': categories_count,
            'time_savings': "70%",
            'compliance': "100% PMI 2025"
        }
        
        return render_template('index.html', 
                             stats=stats,
                             industries=industries,
                             categories=categories)
    except Exception as e:
        logger.error(f"Homepage error: {e}")
        # Fallback to hardcoded values if database fails
        stats = {
            'total_templates': "960+",
            'total_files': "1,594",
            'industries_count': 30,
            'categories_count': 45,
            'time_savings': "70%",
            'compliance': "100% PMI 2025"
        }
        return render_template('index.html', stats=stats)

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard - shows purchased templates and AI history"""
    try:
        logger.info(f"Dashboard accessed by user: {current_user.email}")
        
        # Get purchased templates (both subscription and à la carte)
        try:
            purchased_templates = TemplatePurchase.query.filter_by(user_id=current_user.id)\
                .order_by(TemplatePurchase.purchased_at.desc()).all()
            logger.info(f"Loaded {len(purchased_templates)} purchased templates")
        except Exception as e:
            logger.error(f"Error loading purchases: {e}")
            purchased_templates = []
        
        # Get AI suggestions history
        try:
            ai_suggestions = AISuggestionHistory.query.filter_by(user_id=current_user.id)\
                .order_by(AISuggestionHistory.created_at.desc()).all()
            logger.info(f"Loaded {len(ai_suggestions)} AI suggestions")
        except Exception as e:
            logger.error(f"Error loading AI suggestions: {e}")
            ai_suggestions = []
        
        # Get AI generator history
        try:
            ai_generations = AIGeneratorHistory.query.filter_by(user_id=current_user.id)\
                .order_by(AIGeneratorHistory.created_at.desc()).all()
            logger.info(f"Loaded {len(ai_generations)} AI generations")
        except Exception as e:
            logger.error(f"Error loading AI generations: {e}")
            ai_generations = []
        
        # AI Q&A history not implemented yet
        ai_questions = []
        
        # Add version parameter to force cache bypass
        dashboard_version = '4.0.0'  # Updated for new dashboard
        
        logger.info("Rendering dashboard template")
        response = app.make_response(render_template('dashboard_new.html', 
                             purchased_templates=purchased_templates,
                             ai_suggestions=ai_suggestions,
                             ai_generations=ai_generations,
                             ai_questions=[],
                             version=dashboard_version))
        
        # Add cache-control headers to prevent caching of dashboard
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['X-Dashboard-Version'] = dashboard_version
        response.headers['Expires'] = '0'
        
        logger.info("Dashboard rendered successfully")
        return response
    except Exception as e:
        logger.error(f"CRITICAL ERROR in dashboard: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Return a simple error page instead of crashing
        return render_template('errors/500.html', error="Dashboard temporarily unavailable"), 500

@app.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('pricing.html', 
                         stripe_key=app.config['STRIPE_PUBLISHABLE_KEY'])

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@app.route('/ai-generator')
def ai_generator_page():
    """AI Generator page - public view, generation requires login"""
    return render_template('ai_generator_page.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Initialize database
def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Auto-populate templates if database is empty
        if Template.query.count() == 0:
            import json
            logger.info("Populating database with templates...")
            try:
                catalog_path = os.path.join(os.path.dirname(__file__), "templates_catalog.json")
                with open(catalog_path, "r") as f:
                    templates = json.load(f)
                
                for template_data in templates:
                    template = Template(
                        id=template_data.get("id"),
                        name=template_data.get("name"),
                        description=template_data.get("description"),
                        industry=template_data.get("industry"),
                        category=template_data.get("category"),
                        file_type=template_data.get("file_type"),
                        filename=template_data.get("filename"),
                        downloads=template_data.get("downloads", 0),
                        rating=template_data.get("rating", 4.5),
                        tags=",".join(template_data.get("tags", [])),
                        file_size=template_data.get("file_size"),
                        has_formulas=template_data.get("has_formulas", False),
                        has_fields=template_data.get("has_fields", False),
                        is_premium=template_data.get("is_premium", False),
                    )
                    db.session.add(template)
                
                db.session.commit()
                logger.info(f"Database populated with {Template.query.count()} templates")
            except Exception as e:
                logger.error(f"Error populating database: {e}")
        else:
            logger.info(f"Database already contains {Template.query.count()} templates")

if __name__ == '__main__':
    init_db()
    logger.info("Starting PMBlueprints Production Platform")
    app.run(host='0.0.0.0', port=5002, debug=False)

@app.route('/initialize-database-now')
def initialize_database():
    """Initialize database tables and populate with templates"""
    try:
        db.create_all()
        if Template.query.count() == 0:
            with open('templates_catalog.json', 'r') as f:
                templates = json.load(f)
            for t in templates:
                template = Template(id=t.get("id"), name=t.get("name"), description=t.get("description"), 
                                  industry=t.get("industry"), category=t.get("category"), file_type=t.get("file_type"),
                                  filename=t.get("filename"), downloads=t.get("downloads", 0), rating=t.get("rating", 4.5),
                                  tags=",".join(t.get("tags", [])), file_size=t.get("file_size"), 
                                  has_formulas=t.get("has_formulas", False), has_fields=t.get("has_fields", False),
                                  is_premium=t.get("is_premium", False))
                db.session.add(template)
            db.session.commit()
        return jsonify({"success": True, "templates": Template.query.count()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Force rebuild Sat Oct 18 03:51:20 UTC 2025
# Deployment timestamp: 1760763738
# Deployment 1760817624

@app.route('/diagnostic')
def diagnostic():
    """Diagnostic endpoint to test database and authentication"""
    results = []
    
    # Test 1: Basic response
    results.append("✅ Flask app is running")
    
    # Test 2: Database connection
    try:
        from database import db
        from sqlalchemy import text; db.session.execute(text('SELECT 1'))
        results.append("✅ Database connection works")
    except Exception as e:
        results.append(f"❌ Database connection failed: {str(e)}")
        return "<br>".join(results), 500
    
    # Test 3: User model import
    try:
        from models import User
        results.append("✅ User model imports")
    except Exception as e:
        results.append(f"❌ User model import failed: {str(e)}")
        return "<br>".join(results), 500
    
    # Test 4: Query users table
    try:
        user_count = User.query.count()
        results.append(f"✅ Users table query works ({user_count} users)")
    except Exception as e:
        results.append(f"❌ Users table query failed: {str(e)}")
        return "<br>".join(results), 500
    
    # Test 5: Current user check
    try:
        if current_user.is_authenticated:
            results.append(f"✅ User is authenticated: {current_user.email}")
        else:
            results.append("ℹ️ No user authenticated")
    except Exception as e:
        results.append(f"❌ Current user check failed: {str(e)}")
        return "<br>".join(results), 500
    
    # Test 6: Template model
    try:
        from models import Template
        template_count = Template.query.count()
        results.append(f"✅ Templates table query works ({template_count} templates)")
    except Exception as e:
        results.append(f"❌ Templates table query failed: {str(e)}")
        return "<br>".join(results), 500
    
    # Test 7: TemplatePurchase model
    try:
        from models import TemplatePurchase
        purchase_count = TemplatePurchase.query.count()
        results.append(f"✅ TemplatePurchase table query works ({purchase_count} purchases)")
    except Exception as e:
        results.append(f"❌ TemplatePurchase table query failed: {str(e)}")
    
    # Test 8: AIGeneratorHistory model
    try:
        from models import AIGeneratorHistory
        ai_count = AIGeneratorHistory.query.count()
        results.append(f"✅ AIGeneratorHistory table query works ({ai_count} records)")
    except Exception as e:
        results.append(f"❌ AIGeneratorHistory table query failed: {str(e)}")
    
    # Test 9: AISuggestionHistory model
    try:
        from models import AISuggestionHistory
        suggestion_count = AISuggestionHistory.query.count()
        results.append(f"✅ AISuggestionHistory table query works ({suggestion_count} records)")
    except Exception as e:
        results.append(f"❌ AISuggestionHistory table query failed: {str(e)}")
    
    return "<br>".join(results), 200

"""
PMBlueprints Production Platform
Professional Project Management Templates Platform
Production-Ready Implementation
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
app = Flask(__name__)

# Production Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))

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

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
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

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    company = db.Column(db.String(100))
    subscription_plan = db.Column(db.String(20), default='free')
    subscription_status = db.Column(db.String(20), default='active')
    stripe_customer_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    downloads_used = db.Column(db.Integer, default=0)
    # OAuth fields
    oauth_provider = db.Column(db.String(50))  # 'google' or 'apple'
    oauth_id = db.Column(db.String(255))  # OAuth provider's user ID
    email_verified = db.Column(db.Boolean, default=False)
    # Platform integration tokens (stored as JSON)
    platform_tokens = db.Column(db.Text)  # JSON string of platform OAuth tokens
    # OpenAI API key (optional - users can provide their own)
    openai_api_key = db.Column(db.String(255))  # User's own OpenAI API key
    openai_usage_count = db.Column(db.Integer, default=0)  # Track AI generation usage
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def can_download(self):
        if self.subscription_plan == 'free':
            return self.downloads_used < 3
        elif self.subscription_plan == 'professional':
            return self.downloads_used < 10
        return True  # Enterprise: unlimited
    
    def get_ai_generation_limit(self):
        """Get AI generation limit based on subscription plan"""
        limits = {
            'free': 3,
            'professional': 25,
            'enterprise': 100
        }
        return limits.get(self.subscription_plan, 3)
    
    def can_generate_ai(self):
        """Check if user can generate AI documents"""
        limit = self.get_ai_generation_limit()
        return self.openai_usage_count < limit
    
    def get_ai_generations_remaining(self):
        """Get remaining AI generations for current month"""
        limit = self.get_ai_generation_limit()
        return max(0, limit - self.openai_usage_count)
    
    def is_platform_connected(self, platform):
        """Check if user has connected a specific platform"""
        if not self.platform_tokens:
            return False
        try:
            import json
            tokens = json.loads(self.platform_tokens)
            return platform in tokens and tokens[platform].get('access_token')
        except:
            return False
    
    def get_platform_token(self, platform):
        """Get OAuth token for a specific platform"""
        if not self.platform_tokens:
            return None
        try:
            import json
            tokens = json.loads(self.platform_tokens)
            return tokens.get(platform, {}).get('access_token')
        except:
            return None
    
    def has_openai_key(self):
        """Check if user has configured OpenAI API key"""
        return bool(self.openai_api_key)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company': self.company,
            'subscription_plan': self.subscription_plan,
            'subscription_status': self.subscription_status,
            'downloads_used': self.downloads_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    industry = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # xlsx, docx, pdf
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255))
    preview_image = db.Column(db.String(255))
    downloads = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=4.5)
    tags = db.Column(db.Text)
    file_size = db.Column(db.Integer)
    has_formulas = db.Column(db.Boolean, default=False)
    has_fields = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_premium = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'industry': self.industry,
            'category': self.category,
            'file_type': self.file_type,
            'filename': self.filename,
            'downloads': self.downloads,
            'rating': self.rating,
            'tags': self.tags.split(',') if self.tags else [],
            'file_size': self.file_size,
            'has_formulas': self.has_formulas,
            'has_fields': self.has_fields,
            'is_premium': self.is_premium,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Download(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), nullable=False)
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('downloads', lazy=True))
    template = db.relationship('Template', backref=db.backref('download_records', lazy=True))

class Favorite(db.Model):
    """User favorites for templates"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('favorites', lazy=True))
    template = db.relationship('Template', backref=db.backref('favorited_by', lazy=True))
    
    # Ensure unique favorite per user per template
    __table_args__ = (db.UniqueConstraint('user_id', 'template_id', name='unique_user_template_favorite'),)

class TemplateRating(db.Model):
    """User ratings for templates"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text)  # Optional review text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('ratings', lazy=True))
    template = db.relationship('Template', backref=db.backref('user_ratings', lazy=True))
    
    # Ensure unique rating per user per template
    __table_args__ = (db.UniqueConstraint('user_id', 'template_id', name='unique_user_template_rating'),)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stripe_payment_intent_id = db.Column(db.String(100), unique=True)
    amount = db.Column(db.Integer, nullable=False)  # Amount in cents
    currency = db.Column(db.String(3), default='usd')
    status = db.Column(db.String(20), nullable=False)
    plan = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('payments', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    logger.info(f"Loading user with ID: {user_id}")
    user = User.query.get(int(user_id))
    if user:
        logger.info(f"User loaded: {user.email}")
    else:
        logger.warning(f"User not found for ID: {user_id}")
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
    app.register_blueprint(integrations_bp, url_prefix='/api/integrations')
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
    logger.info("All blueprints registered successfully (including OAuth, AI download, update industries, favorites, ratings, health, setup, and secure payment/AI routes)")
except ImportError as e:
    logger.warning(f"Blueprint import error: {e}. Using inline routes.")

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
    """User dashboard"""
    recent_downloads = Download.query.filter_by(user_id=current_user.id)\
        .order_by(Download.downloaded_at.desc()).limit(5).all()
    
    stats = {
        'total_downloads': len(current_user.downloads),
        'downloads_remaining': 10 - current_user.downloads_used if current_user.subscription_plan == 'free' else 'Unlimited',
        'subscription_plan': current_user.subscription_plan.title(),
        'member_since': current_user.created_at.strftime('%B %Y') if current_user.created_at else 'Unknown'
    }
    
    # Add version parameter to force cache bypass (increment when dashboard.html changes)
    dashboard_version = '3.0.0'  # Increment this to force browsers to reload dashboard
    
    response = app.make_response(render_template('dashboard.html', 
                         user=current_user, 
                         recent_downloads=recent_downloads,
                         stats=stats,
                         version=dashboard_version))
    
    # Add cache-control headers to prevent caching of dashboard
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['X-Dashboard-Version'] = dashboard_version
    response.headers['Expires'] = '0'
    
    return response

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
@login_required
def ai_generator_page():
    """AI Generator page"""
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

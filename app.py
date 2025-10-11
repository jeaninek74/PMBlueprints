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
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///pmblueprints.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Stripe Configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_dummy_key')
app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_dummy_key')

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
CORS(app)

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
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def can_download(self):
        if self.subscription_plan == 'free':
            return self.downloads_used < 10
        return True
    
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
    return User.query.get(int(user_id))

# Import blueprints (with error handling)
try:
    from routes.auth import auth_bp
    from routes.templates import templates_bp
    from routes.payment import payment_bp
    from routes.api import api_bp
    from routes.search_api import search_api_bp
    from routes.ai_generation import ai_bp
    from routes.integrations import integrations_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(templates_bp, url_prefix='/templates')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(search_api_bp, url_prefix='/api/search')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(integrations_bp, url_prefix='/api/integrations')
    logger.info("All blueprints registered successfully (including AI routes)")
except ImportError as e:
    logger.warning(f"Blueprint import error: {e}. Using inline routes.")

# Main routes
@app.route('/')
def index():
    """Homepage"""
    try:
        # Use Supabase for statistics (production database with 964 templates)
        from database_supabase import get_supabase_client
        
        supabase = get_supabase_client()
        
        if supabase:
            # Get statistics from Supabase
            total_response = supabase.table("templates").select("id", count="exact").execute()
            total_templates = total_response.count if total_response.count else 964
            
            # Get distinct industries
            industries_response = supabase.table("templates").select("industry").execute()
            industries = list(set(t["industry"] for t in industries_response.data if t.get("industry")))
            industries_count = len(industries)
            
            # Get distinct categories
            categories_response = supabase.table("templates").select("category").execute()
            categories = list(set(t["category"] for t in categories_response.data if t.get("category")))
            categories_count = len(categories)
            
            # Sort for display
            industries = sorted(industries)
            categories = sorted(categories)
        else:
            # Fallback to hardcoded values if Supabase not available
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
    
    return render_template('dashboard.html', 
                         user=current_user, 
                         recent_downloads=recent_downloads,
                         stats=stats)

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

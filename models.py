"""
Database Models
Defines all database tables and relationships
"""

from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    company = db.Column(db.String(100))
    
    # Subscription fields
    subscription_tier = db.Column(db.String(20), default='free')  # free, individual, professional, enterprise
    subscription_status = db.Column(db.String(20), default='active')
    subscription_start_date = db.Column(db.DateTime)
    stripe_customer_id = db.Column(db.String(100))
    
    # Usage tracking
    downloads_this_month = db.Column(db.Integer, default=0)
    ai_suggestions_this_month = db.Column(db.Integer, default=0)
    ai_generations_this_month = db.Column(db.Integer, default=0)
    last_usage_reset = db.Column(db.DateTime, default=datetime.utcnow)
    
    # OAuth fields
    oauth_provider = db.Column(db.String(50))
    oauth_id = db.Column(db.String(255))
    email_verified = db.Column(db.Boolean, default=False)
    
    # Password reset fields (nullable for backward compatibility)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships - COMMENTED OUT to avoid schema mismatch issues
    # These aren't used directly since queries are done explicitly
    # downloads = db.relationship('DownloadHistory', backref='user', lazy='dynamic')
    # ai_generations = db.relationship('AIGeneratorHistory', backref='user', lazy='dynamic')
    # ai_suggestions = db.relationship('AISuggestionHistory', backref='user', lazy='dynamic')
    # purchases = db.relationship('TemplatePurchase', backref='user', lazy='dynamic')
    # payments = db.relationship('Payment', backref='user', lazy='dynamic')
    
    @property
    def name(self):
        """Return full name or None"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return None
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Template(db.Model):
    """Template model"""
    __tablename__ = 'templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), index=True)
    industry = db.Column(db.String(100), index=True)
    file_format = db.Column(db.String(20))  # xlsx, docx, pptx
    file_path = db.Column(db.String(500))
    thumbnail_path = db.Column(db.String(500))
    cloudflare_url = db.Column(db.String(500))  # CDN URL for screenshot (ImgBB/Cloudflare)
    downloads_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - COMMENTED OUT to avoid schema mismatch issues
    # downloads = db.relationship('DownloadHistory', backref='template', lazy='dynamic')
    # purchases = db.relationship('TemplatePurchase', backref='template', lazy='dynamic')
    
    @property
    def thumbnail(self):
        """Generate thumbnail URL based on template name"""
        # Priority 1: Use Cloudflare CDN URL if available
        if self.cloudflare_url:
            return self.cloudflare_url
        # Priority 2: Use stored thumbnail path
        elif self.thumbnail_path:
            return f'/static/thumbnails/{self.thumbnail_path}'
        # Priority 3: Generate thumbnail filename from template name
        else:
            # Remove special characters and replace spaces with underscores
            safe_name_part = self.name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            safe_name = f"{self.industry.replace(' ', '_')}_{safe_name_part}"
            # Remove any remaining special characters except underscores and hyphens
            safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
            return f'/static/thumbnails/{safe_name}.png'
    
    def __repr__(self):
        return f'<Template {self.name}>'

class DownloadHistory(db.Model):
    """Download history model"""
    __tablename__ = 'download_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'), nullable=False)
    download_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Download {self.user_id}:{self.template_id}>'

class AIGeneratorHistory(db.Model):
    """AI Generator history model"""
    __tablename__ = 'ai_generator_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_name = db.Column(db.String(255))
    project_type = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    methodology = db.Column(db.String(50))
    document_type = db.Column(db.String(100))
    file_format = db.Column(db.String(20))
    generated_content = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AIGeneration {self.id}:{self.document_type}>'

class AISuggestionHistory(db.Model):
    """AI Suggestion history model"""
    __tablename__ = 'ai_suggestion_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_description = db.Column(db.Text)
    industry = db.Column(db.String(100))
    project_phase = db.Column(db.String(100))
    team_size = db.Column(db.String(50))
    suggestions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AISuggestion {self.id}>'

class TemplatePurchase(db.Model):
    """Individual template purchase model - minimal schema matching production DB"""
    __tablename__ = 'template_purchase'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'), nullable=False)
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Purchase {self.user_id}:{self.template_id}>'

class Payment(db.Model):
    """Payment history model"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Amount in cents
    currency = db.Column(db.String(3), default='usd')
    status = db.Column(db.String(20))  # completed, pending, failed
    stripe_payment_id = db.Column(db.String(255))
    stripe_invoice_id = db.Column(db.String(255))  # For invoice links
    subscription_tier = db.Column(db.String(20))  # Tier if subscription payment
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'))  # Template if individual purchase
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.id}:{self.amount}>'

class IntegrationSettings(db.Model):
    """Platform integration settings model"""
    __tablename__ = 'integration_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # API tokens (should be encrypted in production)
    monday_api_token = db.Column(db.String(500))
    smartsheet_api_token = db.Column(db.String(500))
    google_sheets_credentials = db.Column(db.Text)
    microsoft_access_token = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship - COMMENTED OUT to avoid schema mismatch issues
    # user = db.relationship('User', backref=db.backref('integration_settings', uselist=False))
    
    def __repr__(self):
        return f'<IntegrationSettings {self.user_id}>'

class Favorite(db.Model):
    """User favorites model"""
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'template_id', name='unique_favorite'),)
    
    def __repr__(self):
        return f'<Favorite {self.user_id}:{self.template_id}>'


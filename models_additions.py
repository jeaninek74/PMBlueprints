"""
Additional database models for purchased templates and AI history
Add these to app.py after the existing models
"""

# Purchase Model - Track individual template purchases (à la carte)
class TemplatePurchase(db.Model):
    """Track individual template purchases for à la carte option"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=True)
    purchase_type = db.Column(db.String(20), default='alacarte')  # 'alacarte' or 'subscription'
    amount_paid = db.Column(db.Integer, nullable=False)  # Amount in cents
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('template_purchases', lazy=True))
    template = db.relationship('Template', backref=db.backref('purchases', lazy=True))
    payment = db.relationship('Payment', backref=db.backref('template_purchases', lazy=True))
    
    __table_args__ = (db.UniqueConstraint('user_id', 'template_id', name='unique_user_template_purchase'),)

# AI Suggestions History
class AISuggestionHistory(db.Model):
    """Track AI suggestions requests and responses"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    industry = db.Column(db.String(100))
    project_type = db.Column(db.String(100))
    team_size = db.Column(db.String(50))
    timeline = db.Column(db.String(50))
    risk_level = db.Column(db.String(50))
    suggestions = db.Column(db.Text)  # JSON string of suggestions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('ai_suggestions', lazy=True, order_by='AISuggestionHistory.created_at.desc()'))

# AI Generator History  
class AIGeneratorHistory(db.Model):
    """Track AI generator requests and responses"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    template_type = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    project_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    additional_context = db.Column(db.Text)
    preferred_format = db.Column(db.String(50))
    generated_content = db.Column(db.Text)  # JSON string of generated content
    status = db.Column(db.String(20), default='completed')  # 'completed', 'failed', 'pending'
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('ai_generations', lazy=True, order_by='AIGeneratorHistory.created_at.desc()'))

# AI Question/Answer History (for Ask a Question feature)
class AIQuestionHistory(db.Model):
    """Track AI question/answer interactions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    industry = db.Column(db.String(100))
    question = db.Column(db.Text, nullable=False)
    additional_context = db.Column(db.Text)
    answer = db.Column(db.Text)
    status = db.Column(db.String(20), default='completed')  # 'completed', 'failed', 'pending'
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('ai_questions', lazy=True, order_by='AIQuestionHistory.created_at.desc()'))


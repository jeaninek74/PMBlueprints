"""
À La Carte Payment Routes
Handles individual template purchases at $50 each
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
import stripe
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

alacarte_bp = Blueprint('alacarte', __name__, url_prefix='/alacarte')

# À la carte pricing
ALACARTE_PRICE = 5000  # $50.00 in cents

@alacarte_bp.route('/purchase/<int:template_id>')
@login_required
def purchase_template(template_id):
    """Purchase page for individual template"""
    try:
        from database import db, Template, TemplatePurchase
        
        # Check if template exists
        template = Template.query.get_or_404(template_id)
        
        # Check if user already purchased this template
        existing_purchase = TemplatePurchase.query.filter_by(
            user_id=current_user.id,
            template_id=template_id
        ).first()
        
        if existing_purchase:
            flash('You already own this template!', 'info')
            return redirect(url_for('dashboard'))
        
        return render_template('payment/alacarte_checkout.html',
                             template=template,
                             price=ALACARTE_PRICE,
                             price_display='$50.00')
        
    except Exception as e:
        logger.error(f"À la carte purchase page error: {e}")
        flash('Purchase page unavailable', 'error')
        return redirect(url_for('templates.browse'))

@alacarte_bp.route('/create-payment-intent', methods=['POST'])
@login_required
def create_payment_intent():
    """Create Stripe payment intent for template purchase"""
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        
        if not template_id:
            return jsonify({'error': 'Template ID required'}), 400
        
        from database import db, Template, TemplatePurchase
        
        # Verify template exists
        template = Template.query.get(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Check if already purchased
        existing_purchase = TemplatePurchase.query.filter_by(
            user_id=current_user.id,
            template_id=template_id
        ).first()
        
        if existing_purchase:
            return jsonify({'error': 'Template already purchased'}), 400
        
        # Create Stripe payment intent
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        
        intent = stripe.PaymentIntent.create(
            amount=ALACARTE_PRICE,
            currency='usd',
            metadata={
                'user_id': current_user.id,
                'template_id': template_id,
                'purchase_type': 'alacarte',
                'template_name': template.name
            },
            description=f'Template Purchase: {template.name}'
        )
        
        return jsonify({
            'clientSecret': intent.client_secret,
            'paymentIntentId': intent.id
        })
        
    except Exception as e:
        logger.error(f"Payment intent creation error: {e}")
        return jsonify({'error': str(e)}), 500

@alacarte_bp.route('/confirm-payment', methods=['POST'])
@login_required
def confirm_payment():
    """Confirm payment and create purchase record"""
    try:
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        template_id = data.get('template_id')
        
        if not payment_intent_id or not template_id:
            return jsonify({'error': 'Missing required data'}), 400
        
        from database import db, Template, TemplatePurchase, Payment
        
        # Verify payment with Stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status != 'succeeded':
            return jsonify({'error': 'Payment not successful'}), 400
        
        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            stripe_payment_intent_id=payment_intent_id,
            amount=ALACARTE_PRICE,
            currency='usd',
            status='succeeded',
            plan='alacarte'
        )
        db.session.add(payment)
        db.session.flush()  # Get payment ID
        
        # Create template purchase record
        purchase = TemplatePurchase(
            user_id=current_user.id,
            template_id=template_id,
            payment_id=payment.id,
            purchase_type='alacarte',
            amount_paid=ALACARTE_PRICE,
            purchased_at=datetime.utcnow()
        )
        db.session.add(purchase)
        db.session.commit()
        
        logger.info(f"User {current_user.id} purchased template {template_id} for ${ALACARTE_PRICE/100}")
        
        return jsonify({
            'success': True,
            'message': 'Template purchased successfully!',
            'redirect': url_for('dashboard')
        })
        
    except Exception as e:
        logger.error(f"Payment confirmation error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Payment confirmation failed'}), 500

@alacarte_bp.route('/success')
@login_required
def purchase_success():
    """Purchase success page"""
    return render_template('payment/purchase_success.html')


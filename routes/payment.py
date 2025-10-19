"""
Payment Routes
Handles subscription management and payment processing
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
import stripe
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')

# Pricing plans configuration - Updated to match new requirements
PRICING_PLANS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'currency': 'usd',
        'interval': None,
        'stripe_price_id': None,
        'features': [
            'Browse all templates',
            'View template details',
            'No downloads',
            'No AI features'
        ],
        'downloads_per_month': 0,
        'ai_suggestions_per_month': 0,
        'ai_generations_per_month': 0,
        'platform_integrations': False
    },
    'individual': {
        'name': 'Individual',
        'price': 5000,  # $50.00 in cents
        'currency': 'usd',
        'interval': 'one-time',
        'stripe_price_id': None,  # Will be created inline
        'features': [
            '1 template download OR',
            '1 AI generation',
            'Choose from 960+ templates',
            'One-time purchase'
        ],
        'downloads_per_month': 1,
        'ai_suggestions_per_month': 0,
        'ai_generations_per_month': 1,
        'platform_integrations': False
    },
    'professional': {
        'name': 'Professional',
        'price': 7500,  # $75.00 in cents
        'currency': 'usd',
        'interval': 'month',
        'stripe_price_id': None,  # Will be created inline
        'features': [
            '2 template downloads per month',
            '4 AI suggestions per month',
            '6 AI generations per month',
            'Monthly subscription'
        ],
        'downloads_per_month': 2,
        'ai_suggestions_per_month': 4,
        'ai_generations_per_month': 6,
        'platform_integrations': False
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 10000,  # $100.00 in cents
        'currency': 'usd',
        'interval': 'month',
        'stripe_price_id': None,  # Will be created inline
        'features': [
            '2 template downloads per month',
            '4 AI suggestions per month',
            '6 AI generations per month',
            'Platform integrations (Monday.com, Smartsheet, Google Sheets, Microsoft 365)',
            'Priority support'
        ],
        'downloads_per_month': 2,
        'ai_suggestions_per_month': 4,
        'ai_generations_per_month': 6,
        'platform_integrations': True
    }
}

@payment_bp.route('/pricing')
def pricing():
    """Display pricing page"""
    return render_template('pricing.html', plans=PRICING_PLANS, stripe_key=STRIPE_PUBLISHABLE_KEY)

@payment_bp.route('/checkout/<tier>', methods=['GET'])
@login_required
def checkout(tier):
    """Create Stripe checkout session for a subscription tier"""
    try:
        if tier not in PRICING_PLANS:
            flash('Invalid subscription tier', 'error')
            return redirect(url_for('payment.pricing'))
        
        plan = PRICING_PLANS[tier]
        
        # Free tier doesn't need checkout
        if tier == 'free':
            flash('You are already on the Free tier', 'info')
            return redirect(url_for('dashboard'))
        
        # Create Stripe customer if not exists
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=f"{current_user.first_name} {current_user.last_name}",
                metadata={'user_id': current_user.id}
            )
            current_user.stripe_customer_id = customer.id
            from database import db
            db.session.commit()
        
        # Determine success and cancel URLs
        success_url = url_for('payment.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = url_for('payment.cancel', _external=True)
        
        # Create checkout session based on tier type
        if plan['interval'] == 'one-time':
            # One-time payment for Individual tier
            checkout_session = stripe.checkout.Session.create(
                customer=current_user.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': plan['currency'],
                        'unit_amount': plan['price'],
                        'product_data': {
                            'name': f"{plan['name']} - PMBlueprints",
                            'description': 'One template download OR one AI generation',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': current_user.id,
                    'tier': tier
                }
            )
        else:
            # Recurring subscription for Professional/Enterprise
            checkout_session = stripe.checkout.Session.create(
                customer=current_user.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': plan['currency'],
                        'unit_amount': plan['price'],
                        'recurring': {
                            'interval': plan['interval']
                        },
                        'product_data': {
                            'name': f"{plan['name']} - PMBlueprints",
                            'description': ', '.join(plan['features']),
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': current_user.id,
                    'tier': tier
                }
            )
        
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        logger.error(f"Checkout error for tier {tier}: {str(e)}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('payment.pricing'))

@payment_bp.route('/checkout/template/<int:template_id>', methods=['GET'])
@login_required
def checkout_individual_template(template_id):
    """Create checkout session for individual template purchase ($50)"""
    try:
        from models import Template
        template = Template.query.get_or_404(template_id)
        
        # Create Stripe customer if not exists
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=f"{current_user.first_name} {current_user.last_name}",
                metadata={'user_id': current_user.id}
            )
            current_user.stripe_customer_id = customer.id
            from database import db
            db.session.commit()
        
        success_url = url_for('payment.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = url_for('templates.detail', template_id=template_id, _external=True)
        
        checkout_session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': 5000,  # $50.00
                    'product_data': {
                        'name': template.name,
                        'description': f'Individual template purchase - {template.category}',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': current_user.id,
                'template_id': template_id,
                'purchase_type': 'individual_template'
            }
        )
        
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        logger.error(f"Individual template checkout error: {str(e)}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('templates.browse'))

@payment_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session_completed(session)
    
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_invoice_payment_succeeded(invoice)
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
    
    return jsonify({'status': 'success'}), 200

def handle_checkout_session_completed(session):
    """Handle successful checkout session"""
    try:
        from database import db
        from models import User, Payment
        
        user_id = session['metadata'].get('user_id')
        tier = session['metadata'].get('tier')
        template_id = session['metadata'].get('template_id')
        purchase_type = session['metadata'].get('purchase_type')
        
        user = User.query.get(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return
        
        # Handle individual template purchase
        if purchase_type == 'individual_template':
            user.subscription_tier = 'individual'
            user.downloads_this_month = 0  # Reset to allow one download
            user.ai_generations_this_month = 0
            
            # Record the payment
            payment = Payment(
                user_id=user_id,
                amount=5000,
                currency='usd',
                status='completed',
                stripe_payment_id=session['payment_intent'],
                description=f'Individual template purchase - Template ID: {template_id}'
            )
            db.session.add(payment)
        
        # Handle tier subscription
        elif tier:
            user.subscription_tier = tier
            user.subscription_status = 'active'
            user.subscription_start_date = datetime.utcnow()
            
            # Reset usage counters
            user.downloads_this_month = 0
            user.ai_suggestions_this_month = 0
            user.ai_generations_this_month = 0
            user.last_usage_reset = datetime.utcnow()
            
            # Record the payment
            plan = PRICING_PLANS.get(tier, {})
            payment = Payment(
                user_id=user_id,
                amount=plan.get('price', 0),
                currency='usd',
                status='completed',
                stripe_payment_id=session.get('payment_intent') or session.get('subscription'),
                description=f'{tier.title()} subscription'
            )
            db.session.add(payment)
        
        db.session.commit()
        logger.info(f"Checkout completed for user {user_id}, tier: {tier}")
        
    except Exception as e:
        logger.error(f"Error handling checkout session: {str(e)}")

def handle_invoice_payment_succeeded(invoice):
    """Handle successful recurring payment"""
    try:
        from database import db
        from models import User, Payment
        
        customer_id = invoice['customer']
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        
        if not user:
            logger.error(f"User with stripe_customer_id {customer_id} not found")
            return
        
        # Reset monthly usage counters
        user.downloads_this_month = 0
        user.ai_suggestions_this_month = 0
        user.ai_generations_this_month = 0
        user.last_usage_reset = datetime.utcnow()
        
        # Record the payment
        payment = Payment(
            user_id=user.id,
            amount=invoice['amount_paid'],
            currency=invoice['currency'],
            status='completed',
            stripe_payment_id=invoice['payment_intent'],
            description=f'Subscription renewal - {user.subscription_tier}'
        )
        db.session.add(payment)
        db.session.commit()
        
        logger.info(f"Invoice payment succeeded for user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling invoice payment: {str(e)}")

def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    try:
        from database import db
        from models import User
        
        customer_id = subscription['customer']
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        
        if not user:
            logger.error(f"User with stripe_customer_id {customer_id} not found")
            return
        
        # Downgrade to free tier
        user.subscription_tier = 'free'
        user.subscription_status = 'cancelled'
        user.downloads_this_month = 0
        user.ai_suggestions_this_month = 0
        user.ai_generations_this_month = 0
        
        db.session.commit()
        logger.info(f"Subscription cancelled for user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling subscription deletion: {str(e)}")

@payment_bp.route('/success')
@login_required
def success():
    """Payment success page"""
    session_id = request.args.get('session_id')
    return render_template('payment/success.html', session_id=session_id)

@payment_bp.route('/cancel')
@login_required
def cancel():
    """Payment cancelled page"""
    return render_template('payment/cancel.html')

@payment_bp.route('/portal')
@login_required
def customer_portal():
    """Redirect to Stripe customer portal"""
    try:
        if not current_user.stripe_customer_id:
            flash('No billing information found', 'error')
            return redirect(url_for('dashboard'))
        
        portal_session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=url_for('dashboard', _external=True)
        )
        
        return redirect(portal_session.url, code=303)
        
    except Exception as e:
        logger.error(f"Error creating portal session: {str(e)}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('dashboard'))


@payment_bp.route('/billing-history')
@login_required
def billing_history():
    """Billing history page with error handling"""
    try:
        from models import Payment
        payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).all()
        logger.info(f"Found {len(payments)} payments for user {current_user.id}")
    except Exception as e:
        logger.error(f"Error fetching payments for user {current_user.id}: {str(e)}")
        # If Payment table doesn't exist or there's an error, show empty list
        payments = []
        flash('Payment history is currently unavailable.', 'info')
    
    return render_template('payment/billing_history.html', payments=payments)



@payment_bp.route('/subscribe/<tier>')
@login_required
def subscribe(tier):
    """
    Subscribe route that redirects to checkout
    This fixes the URL mismatch where pricing page buttons point to /subscribe/
    but the actual checkout route is /checkout/
    """
    logger.info(f"Subscribe route called for tier: {tier}")
    
    # Validate tier
    if tier not in ['professional', 'enterprise', 'individual', 'free']:
        flash('Invalid subscription tier', 'error')
        return redirect(url_for('pricing'))
    
    # Free tier doesn't need checkout
    if tier == 'free':
        flash('You are already on the Free tier', 'info')
        return redirect(url_for('dashboard'))
    
    # Redirect to the actual checkout route
    return redirect(url_for('payment.checkout', tier=tier))


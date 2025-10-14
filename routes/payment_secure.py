"""
Secure Payment Routes with Rate Limiting
Enhanced payment processing with comprehensive security measures
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
import os
from flask_login import login_required, current_user
import stripe
import logging
from datetime import datetime, timedelta
from functools import wraps
import time

logger = logging.getLogger(__name__)

payment_secure_bp = Blueprint('payment_secure', __name__)

# Pricing plans configuration
PRICING_PLANS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'currency': 'usd',
        'interval': 'month',
        'features': [
            '3 template downloads/month',
            'Basic templates',
            '3 AI generations/month',
            'Email support'
        ]
    },
    'professional': {
        'name': 'Professional',
        'price': 5000,  # $50.00 in cents
        'currency': 'usd',
        'interval': 'month',
        'features': [
            '10 template downloads/month',
            'All 960+ templates',
            '25 AI generations/month',
            'Platform integrations',
            'Priority support'
        ]
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 15000,  # $150.00 in cents
        'currency': 'usd',
        'interval': 'month',
        'features': [
            'Unlimited downloads',
            'All 960+ templates',
            '100 AI generations/month',
            'Custom templates',
            'Advanced analytics',
            'Dedicated support'
        ]
    }
}

# ========== RATE LIMITING ==========

# In-memory rate limit tracking (should use Redis in production)
payment_rate_limits = {}

def check_payment_rate_limit(user_id, limit=10, window=3600):
    """
    Check if user has exceeded payment endpoint rate limit
    Args:
        user_id: User ID
        limit: Maximum requests allowed
        window: Time window in seconds (default 1 hour)
    Returns:
        (allowed, remaining, reset_time)
    """
    now = time.time()
    
    if user_id not in payment_rate_limits:
        payment_rate_limits[user_id] = []
    
    # Remove old requests outside the window
    payment_rate_limits[user_id] = [
        req_time for req_time in payment_rate_limits[user_id]
        if now - req_time < window
    ]
    
    # Check if limit exceeded
    if len(payment_rate_limits[user_id]) >= limit:
        oldest_request = min(payment_rate_limits[user_id])
        reset_time = oldest_request + window
        return False, 0, reset_time
    
    # Add current request
    payment_rate_limits[user_id].append(now)
    remaining = limit - len(payment_rate_limits[user_id])
    reset_time = now + window
    
    return True, remaining, reset_time

def rate_limit_payment(limit=10, window=3600):
    """
    Decorator for rate limiting payment endpoints
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            allowed, remaining, reset_time = check_payment_rate_limit(
                current_user.id, limit, window
            )
            
            if not allowed:
                reset_datetime = datetime.fromtimestamp(reset_time)
                logger.warning(f"Rate limit exceeded for user {current_user.id} on payment endpoint")
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many payment requests. Please try again after {reset_datetime.strftime("%H:%M:%S")}',
                    'retry_after': int(reset_time - time.time())
                }), 429
            
            # Add rate limit headers
            response = f(*args, **kwargs)
            if isinstance(response, tuple):
                response_obj, status_code = response
            else:
                response_obj = response
                status_code = 200
            
            # Add rate limit info to response if it's JSON
            if isinstance(response_obj, dict) or hasattr(response_obj, 'get_json'):
                try:
                    if hasattr(response_obj, 'get_json'):
                        data = response_obj.get_json()
                    else:
                        data = response_obj
                    
                    if data:
                        data['rate_limit'] = {
                            'remaining': remaining,
                            'reset': int(reset_time)
                        }
                except:
                    pass
            
            return response_obj, status_code
        
        return decorated_function
    return decorator

# ========== SUBSCRIPTION VALIDATION ==========

def validate_subscription_status(user):
    """
    Validate user's subscription is active and not expired
    Returns: (is_valid, error_message)
    """
    # Check subscription status
    if user.subscription_status not in ['active', 'trialing']:
        return False, "Subscription is not active"
    
    # Check expiration date if set
    if hasattr(user, 'subscription_expires_at') and user.subscription_expires_at:
        if user.subscription_expires_at < datetime.utcnow():
            return False, "Subscription has expired"
    
    return True, None

def require_active_subscription(required_tier=None):
    """
    Decorator to require active subscription for endpoints
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Validate subscription status
            is_valid, error_msg = validate_subscription_status(current_user)
            if not is_valid:
                return jsonify({
                    'error': 'Subscription validation failed',
                    'message': error_msg,
                    'redirect': url_for('pricing')
                }), 403
            
            # Check tier if specified
            if required_tier and current_user.subscription_plan != required_tier:
                return jsonify({
                    'error': 'Insufficient subscription tier',
                    'message': f'This feature requires {required_tier} tier',
                    'current_tier': current_user.subscription_plan,
                    'redirect': url_for('pricing')
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# ========== PAYMENT ENDPOINTS ==========

@payment_secure_bp.route('/api/plans')
def get_pricing_plans():
    """Get all pricing plans - API endpoint"""
    return jsonify({
        'success': True,
        'plans': PRICING_PLANS
    })

@payment_secure_bp.route('/checkout/<plan>')
def checkout(plan):
    """Checkout page for subscription plan"""
    try:
        if plan not in PRICING_PLANS:
            flash('Invalid subscription plan', 'error')
            return redirect(url_for('pricing'))
        
        plan_info = PRICING_PLANS[plan]
        
        # If user is not logged in, show login prompt on checkout page
        user = current_user if current_user.is_authenticated else None
        
        return render_template('payment/checkout.html',
                             plan=plan,
                             plan_info=plan_info,
                             user=user,
                             requires_login=not current_user.is_authenticated)
        
    except Exception as e:
        logger.error(f"Checkout page error: {e}")
        flash('Checkout page unavailable', 'error')
        return redirect(url_for('pricing'))

@payment_secure_bp.route('/create-payment-intent', methods=['POST'])
@login_required
@rate_limit_payment(limit=10, window=3600)  # 10 payment intents per hour
def create_payment_intent():
    """Create Stripe payment intent with rate limiting"""
    try:
        data = request.get_json()
        plan = data.get('plan')
        
        if plan not in PRICING_PLANS:
            return jsonify({'error': 'Invalid plan'}), 400
        
        plan_info = PRICING_PLANS[plan]
        
        # Validate plan price is not zero (free plan shouldn't create payment intent)
        if plan_info['price'] == 0:
            return jsonify({'error': 'Free plan does not require payment'}), 400
        
        # Check if user already has an active subscription
        if current_user.subscription_plan != 'free' and current_user.subscription_status == 'active':
            logger.warning(f"User {current_user.id} attempted to create payment intent with active subscription")
            return jsonify({
                'error': 'Active subscription exists',
                'message': 'Please cancel your current subscription before upgrading'
            }), 400
        
        # Create or get Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=f"{current_user.first_name} {current_user.last_name}",
                metadata={'user_id': current_user.id}
            )
            current_user.stripe_customer_id = customer.id
            from app import db
            db.session.commit()
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=plan_info['price'],
            currency=plan_info['currency'],
            customer=current_user.stripe_customer_id,
            metadata={
                'user_id': current_user.id,
                'plan': plan,
                'user_email': current_user.email
            },
            # Enable multiple payment methods
            payment_method_types=['card'],  # Stripe automatically includes Apple Pay, Google Pay when available
            automatic_payment_methods={'enabled': True}
        )
        
        logger.info(f"Payment intent created for user {current_user.id}: {intent.id}")
        
        return jsonify({
            'client_secret': intent.client_secret,
            'amount': plan_info['price'],
            'currency': plan_info['currency'],
            'payment_intent_id': intent.id
        })
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        return jsonify({'error': 'Payment processing error', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Payment intent error: {e}")
        return jsonify({'error': 'Payment setup failed', 'details': str(e)}), 500

@payment_secure_bp.route('/confirm-payment', methods=['POST'])
@login_required
@rate_limit_payment(limit=20, window=3600)  # 20 confirmations per hour
def confirm_payment():
    """Confirm successful payment and update subscription"""
    try:
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        plan = data.get('plan')
        
        if not payment_intent_id or plan not in PRICING_PLANS:
            return jsonify({'error': 'Invalid payment data'}), 400
        
        # Retrieve payment intent from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status != 'succeeded':
            return jsonify({'error': 'Payment not completed', 'status': intent.status}), 400
        
        # Verify payment intent belongs to this user
        if intent.metadata.get('user_id') != str(current_user.id):
            logger.error(f"Payment intent user mismatch: {intent.metadata.get('user_id')} != {current_user.id}")
            return jsonify({'error': 'Payment verification failed'}), 403
        
        # Import here to avoid circular imports
        from app import db, Payment
        
        # Check if payment already processed
        existing_payment = Payment.query.filter_by(
            stripe_payment_intent_id=payment_intent_id
        ).first()
        
        if existing_payment:
            logger.warning(f"Payment intent {payment_intent_id} already processed")
            return jsonify({
                'success': True,
                'message': 'Payment already processed',
                'redirect': url_for('dashboard')
            })
        
        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            stripe_payment_intent_id=payment_intent_id,
            amount=intent.amount,
            currency=intent.currency,
            status='completed',
            plan=plan
        )
        db.session.add(payment)
        
        # Update user subscription
        current_user.subscription_plan = plan
        current_user.subscription_status = 'active'
        
        # Set subscription expiration date (30 days from now)
        if hasattr(current_user, 'subscription_expires_at'):
            current_user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
        
        # Reset download count for new subscription
        if plan != 'free':
            current_user.downloads_used = 0
        
        # Reset AI generation count
        if hasattr(current_user, 'ai_generations_used_this_month'):
            current_user.ai_generations_used_this_month = 0
        
        db.session.commit()
        
        logger.info(f"Payment confirmed for user {current_user.email}: {plan} plan")
        
        return jsonify({
            'success': True,
            'message': 'Payment successful! Your subscription has been activated.',
            'subscription': {
                'plan': plan,
                'status': 'active',
                'expires_at': current_user.subscription_expires_at.isoformat() if hasattr(current_user, 'subscription_expires_at') and current_user.subscription_expires_at else None
            },
            'redirect': url_for('dashboard')
        })
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe confirmation error: {e}")
        return jsonify({'error': 'Payment confirmation failed', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Payment confirmation error: {e}")
        from app import db
        db.session.rollback()
        return jsonify({'error': 'Subscription update failed', 'details': str(e)}), 500

@payment_secure_bp.route('/cancel-subscription', methods=['POST'])
@login_required
@rate_limit_payment(limit=5, window=3600)  # 5 cancellations per hour
def cancel_subscription():
    """Cancel user subscription"""
    try:
        if current_user.subscription_plan == 'free':
            return jsonify({'error': 'No active subscription to cancel'}), 400
        
        # Import here to avoid circular imports
        from app import db
        
        # Update user subscription
        current_user.subscription_plan = 'free'
        current_user.subscription_status = 'cancelled'
        current_user.downloads_used = 0  # Reset for free plan
        
        if hasattr(current_user, 'ai_generations_used_this_month'):
            current_user.ai_generations_used_this_month = 0
        
        db.session.commit()
        
        logger.info(f"Subscription cancelled for user: {current_user.email}")
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Subscription cancelled successfully'
            })
        
        flash('Subscription cancelled successfully', 'info')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Subscription cancellation error: {e}")
        if request.is_json:
            return jsonify({'error': 'Cancellation failed', 'details': str(e)}), 500
        flash('Cancellation failed', 'error')
        return redirect(url_for('dashboard'))

@payment_secure_bp.route('/billing-history')
@login_required
def billing_history():
    """View billing history"""
    try:
        from app import Payment
        
        payments = Payment.query.filter_by(user_id=current_user.id)\
            .order_by(Payment.created_at.desc()).all()
        
        return render_template('payment/billing_history.html',
                             payments=payments,
                             user=current_user)
        
    except Exception as e:
        logger.error(f"Billing history error: {e}")
        return render_template('errors/500.html'), 500

@payment_secure_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks with signature verification"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        # Verify webhook signature
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        if not webhook_secret:
            logger.warning("STRIPE_WEBHOOK_SECRET not configured, skipping signature verification")
            event = stripe.Event.construct_from(request.get_json(), stripe.api_key)
        else:
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            except stripe.error.SignatureVerificationError as e:
                logger.error(f"Webhook signature verification failed: {e}")
                return jsonify({'error': 'Invalid signature'}), 400
        
        # Handle different event types
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            logger.info(f"Payment succeeded webhook: {payment_intent['id']}")
            
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            logger.warning(f"Payment failed webhook: {payment_intent['id']}")
            
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            logger.info(f"Subscription cancelled webhook: {subscription['id']}")
            
        return jsonify({'status': 'success'})
        
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': 'Webhook processing failed'}), 500

def register_payment_secure_routes(app):
    """Register secure payment routes with the Flask app"""
    app.register_blueprint(payment_secure_bp)
    logger.info("Secure payment routes registered")


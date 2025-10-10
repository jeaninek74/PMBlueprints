"""
Payment Routes
Handles subscription management and payment processing
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
import stripe
import logging

logger = logging.getLogger(__name__)

payment_bp = Blueprint('payment', __name__)

# Pricing plans configuration
PRICING_PLANS = {
    'professional': {
        'name': 'Professional',
        'price': 2900,  # $29.00 in cents
        'currency': 'usd',
        'interval': 'month',
        'features': [
            'Unlimited template downloads',
            'All 960+ templates',
            'AI template generation',
            'Platform integrations',
            'Priority support'
        ]
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 9900,  # $99.00 in cents
        'currency': 'usd',
        'interval': 'month',
        'features': [
            'Everything in Professional',
            'Custom templates',
            'Advanced analytics',
            'Dedicated support',
            'White-label options'
        ]
    }
}

@payment_bp.route('/checkout')
def checkout_redirect():
    """Handle query parameter format and redirect to correct path"""
    plan = request.args.get('plan')
    if plan and plan in PRICING_PLANS:
        return redirect(url_for('payment.checkout', plan=plan))
    else:
        flash('Invalid subscription plan', 'error')
        return redirect(url_for('pricing'))

@payment_bp.route('/checkout/<plan>')
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

@payment_bp.route('/create-payment-intent', methods=['POST'])
@login_required
def create_payment_intent():
    """Create Stripe payment intent"""
    try:
        data = request.get_json()
        plan = data.get('plan')
        
        if plan not in PRICING_PLANS:
            return jsonify({'error': 'Invalid plan'}), 400
        
        plan_info = PRICING_PLANS[plan]
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=plan_info['price'],
            currency=plan_info['currency'],
            customer=current_user.stripe_customer_id,
            metadata={
                'user_id': current_user.id,
                'plan': plan,
                'user_email': current_user.email
            }
        )
        
        return jsonify({
            'client_secret': intent.client_secret,
            'amount': plan_info['price'],
            'currency': plan_info['currency']
        })
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        return jsonify({'error': 'Payment processing error'}), 500
    except Exception as e:
        logger.error(f"Payment intent error: {e}")
        return jsonify({'error': 'Payment setup failed'}), 500

@payment_bp.route('/confirm-payment', methods=['POST'])
@login_required
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
            return jsonify({'error': 'Payment not completed'}), 400
        
        # Import here to avoid circular imports
        from app import db, Payment
        
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
        
        # Reset download count for new subscription
        if plan != 'free':
            current_user.downloads_used = 0
        
        db.session.commit()
        
        logger.info(f"Payment confirmed for user {current_user.email}: {plan} plan")
        
        return jsonify({
            'success': True,
            'message': 'Payment successful! Your subscription has been activated.',
            'redirect': url_for('dashboard')
        })
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe confirmation error: {e}")
        return jsonify({'error': 'Payment confirmation failed'}), 500
    except Exception as e:
        logger.error(f"Payment confirmation error: {e}")
        return jsonify({'error': 'Subscription update failed'}), 500

@payment_bp.route('/cancel-subscription', methods=['POST'])
@login_required
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
            return jsonify({'error': 'Cancellation failed'}), 500
        flash('Cancellation failed', 'error')
        return redirect(url_for('dashboard'))

@payment_bp.route('/billing-history')
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

@payment_bp.route('/invoice/<int:payment_id>')
@login_required
def invoice(payment_id):
    """Generate invoice for payment"""
    try:
        from app import Payment
        
        payment = Payment.query.filter_by(
            id=payment_id,
            user_id=current_user.id
        ).first_or_404()
        
        return render_template('payment/invoice.html',
                             payment=payment,
                             user=current_user,
                             plan_info=PRICING_PLANS.get(payment.plan, {}))
        
    except Exception as e:
        logger.error(f"Invoice generation error: {e}")
        return render_template('errors/500.html'), 500

@payment_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        # Verify webhook signature (in production, use actual webhook secret)
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        if webhook_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            # For development, parse without verification
            event = stripe.Event.construct_from(
                request.get_json(), stripe.api_key
            )
        
        # Handle different event types
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            logger.info(f"Payment succeeded: {payment_intent['id']}")
            
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            logger.warning(f"Payment failed: {payment_intent['id']}")
            
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            logger.info(f"Subscription cancelled: {subscription['id']}")
            
        return jsonify({'status': 'success'})
        
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': 'Webhook processing failed'}), 500

"""
Account Management Routes
Handles user account, billing, subscription management
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
import os

account_bp = Blueprint('account', __name__)

@account_bp.route('/account')
@login_required
def account_page():
    """Display user account page with subscription and billing info"""
    from database import db, TemplatePurchase, Payment, TemplateDownload
    
    # Get purchased templates
    purchased_templates = TemplatePurchase.query.filter_by(
        user_id=current_user.id
    ).order_by(TemplatePurchase.purchase_date.desc()).all()
    
    # Get payment history
    payment_history = Payment.query.filter_by(
        user_id=current_user.id
    ).order_by(Payment.created_at.desc()).all()
    
    # Calculate this month's usage
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    downloads_this_month = TemplateDownload.query.filter(
        TemplateDownload.user_id == current_user.id,
        TemplateDownload.download_date >= first_day_of_month
    ).count()
    
    # Count AI generations this month (from AI history tables)
    from app import AIGeneratorHistory, AISuggestionHistory
    
    ai_generations_this_month = AIGeneratorHistory.query.filter(
        AIGeneratorHistory.user_id == current_user.id,
        AIGeneratorHistory.created_at >= first_day_of_month
    ).count()
    
    ai_generations_this_month += AISuggestionHistory.query.filter(
        AISuggestionHistory.user_id == current_user.id,
        AISuggestionHistory.created_at >= first_day_of_month
    ).count()
    
    return render_template(
        'account.html',
        purchased_templates=purchased_templates,
        payment_history=payment_history,
        downloads_this_month=downloads_this_month,
        ai_generations_this_month=ai_generations_this_month
    )


@account_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    from database import db
    
    name = request.form.get('name')
    company = request.form.get('company')
    
    current_user.name = name
    current_user.company = company
    
    db.session.commit()
    
    flash('Profile updated successfully', 'success')
    return redirect(url_for('account.account_page'))


@account_bp.route('/cancel-subscription', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel user's subscription"""
    from database import db
    import stripe
    
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    try:
        # Cancel Stripe subscription if exists
        if current_user.stripe_subscription_id:
            stripe.Subscription.cancel(current_user.stripe_subscription_id)
        
        # Update user record
        current_user.subscription_tier = 'free'
        current_user.stripe_subscription_id = None
        current_user.subscription_end_date = None
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@account_bp.route('/upgrade-plan/<plan_type>')
@login_required
def upgrade_plan(plan_type):
    """Redirect to Stripe checkout for plan upgrade"""
    import stripe
    
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    # Define price IDs for each plan
    price_ids = {
        'professional': os.getenv('STRIPE_PROFESSIONAL_PRICE_ID'),
        'enterprise': os.getenv('STRIPE_ENTERPRISE_PRICE_ID')
    }
    
    if plan_type not in price_ids:
        flash('Invalid plan type', 'error')
        return redirect(url_for('account.account_page'))
    
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            line_items=[{
                'price': price_ids[plan_type],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('payment.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('account.account_page', _external=True),
            metadata={
                'user_id': current_user.id,
                'plan_type': plan_type
            }
        )
        
        return redirect(checkout_session.url)
    except Exception as e:
        flash(f'Error creating checkout session: {str(e)}', 'error')
        return redirect(url_for('account.account_page'))


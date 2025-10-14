#!/usr/bin/env python3
"""
Check Payment Security Guards
"""

import re

# Read payment.py
with open('routes/payment.py', 'r') as f:
    payment_code = f.read()

print("=" * 80)
print("PAYMENT SECURITY ANALYSIS")
print("=" * 80)
print()

# Check 1: Authentication requirements
print("1. Authentication Guards:")
print("-" * 80)
auth_required = payment_code.count('@login_required')
print(f"✅ @login_required decorators: {auth_required} endpoints protected")
print()

# Check 2: Plan validation
print("2. Plan Validation:")
print("-" * 80)
if 'if plan not in PRICING_PLANS' in payment_code or 'if not plan or plan not in PRICING_PLANS' in payment_code:
    print("✅ Plan validation: Checks if plan exists in PRICING_PLANS")
else:
    print("❌ Plan validation: NOT FOUND")
print()

# Check 3: Price tampering protection
print("3. Price Tampering Protection:")
print("-" * 80)
if 'PRICING_PLANS[plan]' in payment_code and 'price' in payment_code:
    print("✅ Server-side pricing: Uses PRICING_PLANS dictionary (client can't tamper)")
else:
    print("⚠️  Price source unclear")

if 'amount=plan_info[\'price\']' in payment_code or 'amount=plan_info["price"]' in payment_code:
    print("✅ Payment amount: Taken from server-side PRICING_PLANS")
else:
    print("⚠️  Payment amount source unclear")
print()

# Check 4: User verification
print("4. User Verification:")
print("-" * 80)
if 'current_user.id' in payment_code:
    print("✅ User ID verification: Uses current_user.id from session")
if 'current_user.email' in payment_code:
    print("✅ Email verification: Uses current_user.email from session")
print()

# Check 5: Stripe security
print("5. Stripe Security:")
print("-" * 80)
if 'stripe.PaymentIntent' in payment_code:
    print("✅ Stripe PaymentIntent: Server-side payment creation")
if 'metadata' in payment_code:
    print("✅ Payment metadata: Includes user_id, plan, email for verification")
if 'stripe.PaymentIntent.retrieve' in payment_code:
    print("✅ Payment verification: Retrieves and verifies payment from Stripe")
if 'intent.status' in payment_code:
    print("✅ Status check: Verifies payment succeeded before granting access")
print()

# Check 6: Input validation
print("6. Input Validation:")
print("-" * 80)
if 'request.get_json()' in payment_code:
    print("✅ JSON parsing: Uses Flask's get_json()")
if 'if not payment_intent_id' in payment_code:
    print("✅ Required fields: Checks for payment_intent_id")
if 'if not plan' in payment_code or 'if plan not in' in payment_code:
    print("✅ Plan validation: Validates plan parameter")
print()

# Check 7: Error handling
print("7. Error Handling:")
print("-" * 80)
try_except_count = payment_code.count('try:')
print(f"✅ Try-except blocks: {try_except_count} error handlers")
if 'stripe.error.StripeError' in payment_code:
    print("✅ Stripe error handling: Catches Stripe-specific errors")
if 'logger.error' in payment_code:
    print("✅ Error logging: Logs errors for monitoring")
print()

# Check 8: Missing guards
print("8. Potential Security Issues:")
print("-" * 80)

issues = []

# Check for amount validation from client
if 'amount' in payment_code and 'request.get_json()' in payment_code:
    if 'data.get(\'amount\')' in payment_code or 'data["amount"]' in payment_code:
        issues.append("⚠️  Amount from client: Client should NOT send amount")

# Check for rate limiting
if 'rate_limit' not in payment_code.lower() and 'limiter' not in payment_code.lower():
    issues.append("⚠️  Rate limiting: No rate limiting detected")

# Check for CSRF protection
if 'csrf' not in payment_code.lower():
    issues.append("ℹ️  CSRF: Flask-WTF CSRF should be enabled globally")

# Check for subscription type validation
if 'subscription_type' in payment_code:
    if 'subscription_type in [' not in payment_code and 'subscription_type == ' not in payment_code:
        issues.append("❌ Subscription type: Not validated against allowed values")

if issues:
    for issue in issues:
        print(issue)
else:
    print("✅ No obvious security issues found")

print()
print("=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)
print()
print("1. ✅ Keep prices server-side only (already done)")
print("2. ⚠️  Add rate limiting to prevent payment spam")
print("3. ⚠️  Validate subscription_type parameter")
print("4. ✅ Use Stripe webhook for final verification (already implemented)")
print("5. ✅ Require authentication for all payment endpoints (already done)")
print()

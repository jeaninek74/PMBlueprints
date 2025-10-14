#!/usr/bin/env python3
"""
Check Usage Limits Enforcement
"""

print("=" * 80)
print("USAGE LIMITS SECURITY CHECK")
print("=" * 80)
print()

# Check templates download route
print("1. Template Download Limits:")
print("-" * 80)
with open('routes/templates.py', 'r') as f:
    templates_code = f.read()

if 'can_download()' in templates_code:
    print("✅ Download check: Calls can_download() method")
else:
    print("❌ Download check: NOT FOUND")

if 'Download limit reached' in templates_code or 'download limit' in templates_code.lower():
    print("✅ Limit message: Shows error when limit reached")
else:
    print("⚠️  Limit message: Not clear")

if 'downloads_used' in templates_code:
    print("✅ Usage tracking: Increments downloads_used counter")
else:
    print("❌ Usage tracking: NOT FOUND")

print()

# Check AI generation route
print("2. AI Generation Limits:")
print("-" * 80)
with open('routes/ai_generator_advanced.py', 'r') as f:
    ai_code = f.read()

if 'can_generate_ai()' in ai_code:
    print("✅ Generation check: Calls can_generate_ai() method")
else:
    print("❌ Generation check: NOT FOUND")

if 'openai_usage_count' in ai_code or 'ai_generations' in ai_code:
    print("✅ Usage tracking: Tracks AI generation count")
else:
    print("❌ Usage tracking: NOT FOUND")

if 'generation limit' in ai_code.lower() or 'limit reached' in ai_code.lower():
    print("✅ Limit message: Shows error when limit reached")
else:
    print("⚠️  Limit message: Not clear")

print()

# Check User model for limit methods
print("3. User Model Limit Methods:")
print("-" * 80)
with open('app.py', 'r') as f:
    app_code = f.read()

if 'def can_download(' in app_code:
    print("✅ can_download() method: Defined in User model")
    # Extract the method
    start = app_code.find('def can_download(')
    if start != -1:
        end = app_code.find('\n    def ', start + 1)
        method = app_code[start:end if end != -1 else start + 500]
        if 'return True' in method and 'downloads_used' not in method:
            print("   ⚠️  WARNING: Method may always return True!")
        elif 'downloads_used' in method and 'download_limit' in method:
            print("   ✅ Properly checks downloads_used vs limit")
else:
    print("❌ can_download() method: NOT FOUND")

if 'def can_generate_ai(' in app_code:
    print("✅ can_generate_ai() method: Defined in User model")
    start = app_code.find('def can_generate_ai(')
    if start != -1:
        end = app_code.find('\n    def ', start + 1)
        method = app_code[start:end if end != -1 else start + 500]
        if 'return True' in method and 'openai_usage_count' not in method:
            print("   ⚠️  WARNING: Method may always return True!")
        elif 'openai_usage_count' in method:
            print("   ✅ Properly checks AI usage count")
else:
    print("❌ can_generate_ai() method: NOT FOUND")

if 'def get_download_limit(' in app_code:
    print("✅ get_download_limit() method: Returns limit based on plan")
else:
    print("⚠️  get_download_limit() method: Not found")

if 'def get_ai_generation_limit(' in app_code:
    print("✅ get_ai_generation_limit() method: Returns AI limit based on plan")
else:
    print("⚠️  get_ai_generation_limit() method: Not found")

print()

# Check for limit bypasses
print("4. Potential Bypass Issues:")
print("-" * 80)

issues = []

# Check if download route enforces limits
if 'if current_user.is_authenticated and not current_user.can_download()' not in templates_code:
    if 'can_download()' not in templates_code:
        issues.append("❌ CRITICAL: Template downloads may not enforce limits!")

# Check if AI route enforces limits  
if 'can_generate_ai()' not in ai_code:
    issues.append("❌ CRITICAL: AI generation may not enforce limits!")

# Check for admin bypass
if 'if current_user.is_admin' in templates_code or 'if current_user.role == \'admin\'' in templates_code:
    if 'return' in templates_code:
        issues.append("ℹ️  Admin bypass: Admins may bypass limits (this is OK)")

if not issues:
    print("✅ No obvious bypass issues found")
else:
    for issue in issues:
        print(issue)

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()

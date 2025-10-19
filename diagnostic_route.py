"""
Diagnostic route to add to app.py to identify what's failing
Add this to app.py after the imports
"""

diagnostic_code = '''
@app.route('/diagnostic')
def diagnostic():
    """Diagnostic endpoint to test database and authentication"""
    results = []
    
    # Test 1: Basic response
    results.append("✅ Flask app is running")
    
    # Test 2: Database connection
    try:
        from database import db
        db.session.execute('SELECT 1')
        results.append("✅ Database connection works")
    except Exception as e:
        results.append(f"❌ Database connection failed: {str(e)}")
        return "<br>".join(results), 500
    
    # Test 3: User model import
    try:
        from models import User
        results.append("✅ User model imports")
    except Exception as e:
        results.append(f"❌ User model import failed: {str(e)}")
        return "<br>".join(results), 500
    
    # Test 4: Query users table
    try:
        user_count = User.query.count()
        results.append(f"✅ Users table query works ({user_count} users)")
    except Exception as e:
        results.append(f"❌ Users table query failed: {str(e)}")
        return "<br>".join(results), 500
    
    # Test 5: Current user check
    try:
        if current_user.is_authenticated:
            results.append(f"✅ User is authenticated: {current_user.email}")
        else:
            results.append("ℹ️ No user authenticated")
    except Exception as e:
        results.append(f"❌ Current user check failed: {str(e)}")
        return "<br>".join(results), 500
    
    # Test 6: Template model
    try:
        from models import Template
        template_count = Template.query.count()
        results.append(f"✅ Templates table query works ({template_count} templates)")
    except Exception as e:
        results.append(f"❌ Templates table query failed: {str(e)}")
        return "<br>".join(results), 500
    
    # Test 7: TemplatePurchase model
    try:
        from models import TemplatePurchase
        purchase_count = TemplatePurchase.query.count()
        results.append(f"✅ TemplatePurchase table query works ({purchase_count} purchases)")
    except Exception as e:
        results.append(f"❌ TemplatePurchase table query failed: {str(e)}")
    
    # Test 8: AIGeneratorHistory model
    try:
        from models import AIGeneratorHistory
        ai_count = AIGeneratorHistory.query.count()
        results.append(f"✅ AIGeneratorHistory table query works ({ai_count} records)")
    except Exception as e:
        results.append(f"❌ AIGeneratorHistory table query failed: {str(e)}")
    
    # Test 9: AISuggestionHistory model
    try:
        from models import AISuggestionHistory
        suggestion_count = AISuggestionHistory.query.count()
        results.append(f"✅ AISuggestionHistory table query works ({suggestion_count} records)")
    except Exception as e:
        results.append(f"❌ AISuggestionHistory table query failed: {str(e)}")
    
    return "<br>".join(results), 200
'''

print("Add this code to app.py after the imports section:")
print(diagnostic_code)


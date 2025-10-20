"""
Fix category naming inconsistencies in PRODUCTION database
Standardizes category names to match dropdown values
"""

import os
import psycopg2
from urllib.parse import urlparse

def fix_production_categories():
    """Fix category naming in production database"""
    
    # Get production database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return
    
    # Parse database URL
    result = urlparse(database_url)
    
    # Connect to production database
    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
    
    cursor = conn.cursor()
    
    print("Fixing category naming in PRODUCTION database...\n")
    
    # Fix 1: Open Action Item Log → Action Item Log
    cursor.execute("""
        SELECT id, industry, name 
        FROM templates 
        WHERE category = 'Open Action Item Log'
    """)
    open_action_logs = cursor.fetchall()
    
    print(f"Action Item Log standardization:")
    print(f"  Found {len(open_action_logs)} templates with 'Open Action Item Log'")
    
    for template_id, industry, name in open_action_logs:
        print(f"    - {industry}: {name}")
        cursor.execute("""
            UPDATE templates 
            SET category = 'Action Item Log' 
            WHERE id = %s
        """, (template_id,))
    
    # Fix 2: Comprehensive Budget → Budget
    cursor.execute("""
        SELECT id, industry, name 
        FROM templates 
        WHERE category = 'Comprehensive Budget'
    """)
    comprehensive_budgets = cursor.fetchall()
    
    print(f"\nBudget standardization:")
    print(f"  Found {len(comprehensive_budgets)} templates with 'Comprehensive Budget'")
    
    for template_id, industry, name in comprehensive_budgets:
        print(f"    - {industry}: {name}")
        cursor.execute("""
            UPDATE templates 
            SET category = 'Budget' 
            WHERE id = %s
        """, (template_id,))
    
    # Commit changes
    conn.commit()
    
    print(f"\n✅ Fixed {len(open_action_logs) + len(comprehensive_budgets)} templates in production")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM templates WHERE category = 'Action Item Log'")
    action_item_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM templates WHERE category = 'Budget'")
    budget_count = cursor.fetchone()[0]
    
    print(f"\nVerification:")
    print(f"  Action Item Log: {action_item_count} templates")
    print(f"  Budget: {budget_count} templates")
    
    # Check for remaining inconsistencies
    cursor.execute("SELECT COUNT(*) FROM templates WHERE category = 'Open Action Item Log'")
    open_remaining = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM templates WHERE category = 'Comprehensive Budget'")
    comprehensive_remaining = cursor.fetchone()[0]
    
    if open_remaining == 0 and comprehensive_remaining == 0:
        print(f"\n✅ All naming inconsistencies fixed in production!")
    else:
        print(f"\n⚠️ Warning: Some inconsistencies remain in production")
    
    # Close connection
    cursor.close()
    conn.close()

if __name__ == '__main__':
    fix_production_categories()


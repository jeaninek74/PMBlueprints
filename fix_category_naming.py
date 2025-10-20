"""
Fix category naming inconsistencies in the database
Standardizes category names to match dropdown values
"""

import os
from app import app
from models import Template
from database import db

def fix_category_naming():
    """Standardize category names"""
    
    with app.app_context():
        print("Fixing category naming inconsistencies...\n")
        
        # Fix 1: Open Action Item Log → Action Item Log
        open_action_logs = Template.query.filter(
            Template.category == 'Open Action Item Log'
        ).all()
        
        print(f"Action Item Log standardization:")
        print(f"  Found {len(open_action_logs)} templates with 'Open Action Item Log'")
        
        for template in open_action_logs:
            print(f"    - {template.industry}: {template.name}")
            template.category = 'Action Item Log'
        
        # Fix 2: Comprehensive Budget → Budget
        comprehensive_budgets = Template.query.filter(
            Template.category == 'Comprehensive Budget'
        ).all()
        
        print(f"\nBudget standardization:")
        print(f"  Found {len(comprehensive_budgets)} templates with 'Comprehensive Budget'")
        
        for template in comprehensive_budgets:
            print(f"    - {template.industry}: {template.name}")
            template.category = 'Budget'
        
        # Commit changes
        db.session.commit()
        
        print(f"\n✅ Fixed {len(open_action_logs) + len(comprehensive_budgets)} templates")
        
        # Verify
        action_item_count = Template.query.filter(Template.category == 'Action Item Log').count()
        budget_count = Template.query.filter(Template.category == 'Budget').count()
        
        print(f"\nVerification:")
        print(f"  Action Item Log: {action_item_count} templates")
        print(f"  Budget: {budget_count} templates")
        
        # Check for any remaining inconsistencies
        open_action_remaining = Template.query.filter(Template.category == 'Open Action Item Log').count()
        comprehensive_remaining = Template.query.filter(Template.category == 'Comprehensive Budget').count()
        
        if open_action_remaining == 0 and comprehensive_remaining == 0:
            print(f"\n✅ All naming inconsistencies fixed!")
        else:
            print(f"\n⚠️ Warning: Some inconsistencies remain")
            if open_action_remaining > 0:
                print(f"  - Open Action Item Log: {open_action_remaining} templates")
            if comprehensive_remaining > 0:
                print(f"  - Comprehensive Budget: {comprehensive_remaining} templates")

if __name__ == '__main__':
    fix_category_naming()


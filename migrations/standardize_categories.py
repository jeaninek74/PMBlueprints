"""
One-time migration to standardize category names
This ensures dropdown categories match database exactly
"""

def run_migration():
    """Standardize category names in the database"""
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app import db, Template, app
        
        with app.app_context():
            # Define category name mappings
            category_mappings = {
                # Action Item Log variations
                'Open Action Item Log': 'Action Item Log',
                'Development Open Action Item Log': 'Action Item Log',
                'Implementation Open Action Item Log': 'Action Item Log',
                
                # Budget variations
                'Comprehensive Budget': 'Budget',
                'Comprehensive Budget with Instructions': 'Budget',
                'Training Budget Estimates': 'Training Budget',
                
                # KPI Report variations
                'KPI Dashboard': 'KPI Report',
                'KPI Report Dashboard': 'KPI Report',
                'Development KPI Report Dashboard': 'KPI Report',
                'Implementation KPI Report Dashboard': 'KPI Report',
                'KPI Dashboard with Instructions': 'KPI Report',
                
                # Lessons Learned variations
                'Development Lessons Learned': 'Lessons Learned',
                'Implementation Lessons Learned': 'Lessons Learned',
                
                # Project Proposal variations
                'Development Project Proposal': 'Project Proposal',
                'Implementation Project Proposal': 'Project Proposal',
                'Comprehensive Project Proposal Essay': 'Project Proposal',
                
                # RAID Log variations
                'Executive RAID Log Complete': 'RAID Log',
            }
            
            total_updated = 0
            
            # Update each category
            for old_name, new_name in category_mappings.items():
                templates = Template.query.filter_by(category=old_name).all()
                count = len(templates)
                if count > 0:
                    for template in templates:
                        template.category = new_name
                    print(f"✅ Updated {count} templates: '{old_name}' → '{new_name}'")
                    total_updated += count
            
            db.session.commit()
            print(f"\n✅ Migration complete! Total templates updated: {total_updated}")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        try:
            db.session.rollback()
        except:
            pass
        return False

if __name__ == "__main__":
    run_migration()


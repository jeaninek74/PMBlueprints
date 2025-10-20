"""
Comprehensive category naming standardization
Standardizes ALL category names to match correct naming convention
"""

from app import app
from models import Template
from database import db

def standardize_all_categories():
    """Standardize all category names to correct convention"""
    
    with app.app_context():
        print("Standardizing ALL category names...\n")
        
        # Define standardization mappings
        standardizations = {
            # KPI Report variations → KPI Report
            'KPI Report Dashboard': 'KPI Report',
            'Development KPI Report Dashboard': 'KPI Report',
            'Implementation KPI Report Dashboard': 'KPI Report',
            'KPI Dashboard': 'KPI Report',
            'KPI Dashboard with Instructions': 'KPI Report',
            
            # Lessons Learned variations → Lessons Learned
            'Development Lessons Learned': 'Lessons Learned',
            'Implementation Lessons Learned': 'Lessons Learned',
            
            # Action Item Log variations → Action Item Log
            'Open Action Item Log': 'Action Item Log',
            'Development Open Action Item Log': 'Action Item Log',
            'Implementation Open Action Item Log': 'Action Item Log',
            
            # Project Proposal variations → Project Proposal
            'Development Project Proposal': 'Project Proposal',
            'Implementation Project Proposal': 'Project Proposal',
            'Comprehensive Project Proposal Essay': 'Project Proposal',
            
            # Training Budget variations → Training Budget
            'Training Budget Estimates': 'Training Budget',
            
            # Budget variations → Budget
            'Comprehensive Budget': 'Budget',
            'Comprehensive Budget with Instructions': 'Budget',
            
            # RAID Log variations → RAID Log
            'Executive RAID Log Complete': 'RAID Log',
        }
        
        total_fixed = 0
        
        for old_name, new_name in sorted(standardizations.items()):
            templates = Template.query.filter(Template.category == old_name).all()
            
            if templates:
                print(f"\n{old_name} → {new_name}")
                print(f"  Found {len(templates)} templates:")
                
                for template in templates:
                    print(f"    - {template.industry}: {template.name}")
                    template.category = new_name
                    total_fixed += 1
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ Standardized {total_fixed} templates across {len(standardizations)} category variations")
        print(f"{'='*60}")
        
        # Verify final counts
        print(f"\nFinal category counts:")
        final_categories = {
            'KPI Report': Template.query.filter(Template.category == 'KPI Report').count(),
            'Lessons Learned': Template.query.filter(Template.category == 'Lessons Learned').count(),
            'Action Item Log': Template.query.filter(Template.category == 'Action Item Log').count(),
            'Project Proposal': Template.query.filter(Template.category == 'Project Proposal').count(),
            'Training Budget': Template.query.filter(Template.category == 'Training Budget').count(),
            'Budget': Template.query.filter(Template.category == 'Budget').count(),
            'RAID Log': Template.query.filter(Template.category == 'RAID Log').count(),
        }
        
        for cat, count in final_categories.items():
            print(f"  {cat}: {count} templates")
        
        # Check for any remaining variations
        print(f"\nChecking for remaining variations...")
        all_categories = Template.query.with_entities(Template.category).distinct().all()
        categories = sorted([c[0] for c in all_categories if c[0]])
        
        remaining_variations = []
        for cat in categories:
            if any(prefix in cat for prefix in ['Development', 'Implementation', 'Open', 'Comprehensive', 'Executive']):
                if cat not in ['Development', 'Implementation']:  # These are valid industry names
                    count = Template.query.filter(Template.category == cat).count()
                    remaining_variations.append(f"  - {cat} ({count} templates)")
        
        if remaining_variations:
            print(f"\n⚠️ Warning: {len(remaining_variations)} variations still remain:")
            for var in remaining_variations:
                print(var)
        else:
            print(f"\n✅ All variations standardized successfully!")

if __name__ == '__main__':
    standardize_all_categories()


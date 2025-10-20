"""
Comprehensive category naming standardization for PRODUCTION
Standardizes ALL category names to match correct naming convention
"""

import os
import psycopg2
from urllib.parse import urlparse

def standardize_production_categories():
    """Standardize all category names in production database"""
    
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
    
    print("Standardizing ALL category names in PRODUCTION...\n")
    
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
        cursor.execute("""
            SELECT id, industry, name 
            FROM templates 
            WHERE category = %s
        """, (old_name,))
        templates = cursor.fetchall()
        
        if templates:
            print(f"\n{old_name} → {new_name}")
            print(f"  Found {len(templates)} templates:")
            
            for template_id, industry, name in templates:
                print(f"    - {industry}: {name}")
                cursor.execute("""
                    UPDATE templates 
                    SET category = %s 
                    WHERE id = %s
                """, (new_name, template_id))
                total_fixed += 1
    
    # Commit all changes
    conn.commit()
    
    print(f"\n{'='*60}")
    print(f"✅ Standardized {total_fixed} templates in PRODUCTION")
    print(f"{'='*60}")
    
    # Verify final counts
    print(f"\nFinal category counts in PRODUCTION:")
    final_categories = ['KPI Report', 'Lessons Learned', 'Action Item Log', 
                       'Project Proposal', 'Training Budget', 'Budget', 'RAID Log']
    
    for cat in final_categories:
        cursor.execute("SELECT COUNT(*) FROM templates WHERE category = %s", (cat,))
        count = cursor.fetchone()[0]
        print(f"  {cat}: {count} templates")
    
    # Close connection
    cursor.close()
    conn.close()
    
    print(f"\n✅ All category naming standardized in production!")

if __name__ == '__main__':
    standardize_production_categories()


#!/usr/bin/env python3
"""
Fix template catalog - extract proper names and descriptions from filenames
"""
import json
import os
import re

def extract_template_name(filename):
    """Extract human-readable name from filename"""
    # Remove extension
    name = os.path.splitext(filename)[0]
    
    # Remove industry prefix (e.g., "AI_ML_", "Construction_", etc.)
    name = re.sub(r'^[A-Z][a-z]+_[A-Z][a-z]+_', '', name)
    name = re.sub(r'^[A-Z][a-z]+_', '', name)
    
    # Remove 2025_PMI suffix
    name = re.sub(r'_2025_PMI$', '', name)
    name = re.sub(r'_with_Instructions$', '', name)
    
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    
    # Capitalize properly
    name = name.title()
    
    return name

def generate_description(name, category, industry):
    """Generate proper description based on template type"""
    descriptions = {
        'Change Management': f'Comprehensive {name.lower()} for managing organizational changes, stakeholder engagement, and transition planning',
        'Communication': f'Professional {name.lower()} for effective project communication, stakeholder updates, and information distribution',
        'Financial Management': f'Detailed {name.lower()} with automated calculations, variance analysis, and financial tracking',
        'Performance Management': f'Visual {name.lower()} with automated charts, KPIs, and performance metrics for project monitoring',
        'Risk Management': f'Complete {name.lower()} with risk assessment, mitigation strategies, and priority matrices',
        'Resource Management': f'Comprehensive {name.lower()} for resource allocation, capacity planning, and utilization tracking',
        'Quality Management': f'Professional {name.lower()} for quality assurance, control processes, and compliance tracking',
        'Stakeholder Management': f'Detailed {name.lower()} for stakeholder analysis, engagement strategies, and communication planning',
        'Procurement': f'Complete {name.lower()} for vendor management, contract tracking, and procurement processes',
        'Project Planning': f'Comprehensive {name.lower()} with Gantt charts, milestones, dependencies, and resource allocation',
        'Project Initiation': f'Professional {name.lower()} for project kickoff, charter development, and stakeholder alignment',
        'Project Closure': f'Detailed {name.lower()} for project completion, lessons learned, and final deliverables',
    }
    
    # Get description template or use default
    desc_template = descriptions.get(category, f'Professional {name.lower()} for {industry.lower()} projects')
    
    return desc_template

def fix_catalog():
    """Fix the template catalog with proper names and descriptions"""
    catalog_path = 'templates_catalog.json'
    
    print("Loading template catalog...")
    with open(catalog_path, 'r') as f:
        templates = json.load(f)
    
    print(f"Found {len(templates)} templates")
    print("\nFixing template names and descriptions...")
    
    fixed_count = 0
    for template in templates:
        filename = template.get('filename', '')
        category = template.get('category', '')
        industry = template.get('industry', '')
        
        # Extract proper name
        new_name = extract_template_name(filename)
        
        # Generate proper description
        new_description = generate_description(new_name, category, industry)
        
        # Update if changed
        if template.get('name') != new_name or template.get('description') != new_description:
            template['name'] = new_name
            template['description'] = new_description
            fixed_count += 1
    
    print(f"Fixed {fixed_count} templates")
    
    # Save updated catalog
    print("\nSaving updated catalog...")
    with open(catalog_path, 'w') as f:
        json.dump(templates, f, indent=2)
    
    print("✅ Template catalog fixed successfully!")
    
    # Show sample
    print("\nSample of fixed templates:")
    for i, t in enumerate(templates[:5]):
        print(f"\n{i+1}. {t['name']}")
        print(f"   Category: {t['category']}")
        print(f"   Description: {t['description'][:80]}...")

if __name__ == '__main__':
    fix_catalog()


#!/usr/bin/env python3
"""
Fix template catalog - extract proper names and descriptions from filenames (v2)
"""
import json
import os
import re

def extract_template_name(filename):
    """Extract human-readable name from filename"""
    # Remove extension
    name = os.path.splitext(filename)[0]
    
    # Remove common industry prefixes (more comprehensive)
    prefixes_to_remove = [
        'AI_ML_', 'Construction_', 'Healthcare_', 'Technology_', 'Finance_',
        'Manufacturing_', 'Retail_', 'Education_', 'Government_', 'Consulting_',
        'Energy_', 'Telecommunications_', 'Transportation_', 'Real_Estate_',
        'Hospitality_', 'Agriculture_', 'Automotive_', 'Aerospace_', 'Biotechnology_',
        'Chemicals_', 'Defense_', 'Entertainment_', 'Environmental_', 'Insurance_',
        'Legal_', 'Media_', 'Mining_', 'Pharmaceuticals_', 'Utilities_', 'Nonprofit_',
        'General_'
    ]
    
    for prefix in prefixes_to_remove:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    
    # Remove suffixes
    name = re.sub(r'_2025_PMI$', '', name)
    name = re.sub(r'_with_Instructions$', '', name)
    name = re.sub(r'_Template$', '', name)
    
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    
    # Capitalize properly
    name = name.title()
    
    # Fix common acronyms
    name = name.replace('Kpi', 'KPI')
    name = name.replace('Wbs', 'WBS')
    name = name.replace('Pm', 'PM')
    name = name.replace('Roi', 'ROI')
    name = name.replace('Raci', 'RACI')
    name = name.replace('Swot', 'SWOT')
    name = name.replace('Ai', 'AI')
    name = name.replace('Ml', 'ML')
    name = name.replace('It', 'IT')
    
    return name

def generate_description(name, category, industry, file_type):
    """Generate proper description based on template type"""
    
    # Base descriptions by category
    category_descriptions = {
        'Change Management': 'Comprehensive change management planning and tracking with stakeholder engagement strategies',
        'Communication': 'Professional communication planning for effective stakeholder updates and information distribution',
        'Financial Management': 'Detailed financial tracking with automated calculations, variance analysis, and forecasting',
        'Performance Management': 'Visual performance dashboard with automated charts, KPIs, and metrics tracking',
        'Risk Management': 'Complete risk assessment and mitigation planning with priority matrices and tracking',
        'Resource Management': 'Comprehensive resource allocation, capacity planning, and utilization tracking',
        'Quality Management': 'Professional quality assurance and control processes with compliance tracking',
        'Stakeholder Management': 'Detailed stakeholder analysis, engagement strategies, and communication planning',
        'Procurement': 'Complete vendor management, contract tracking, and procurement process documentation',
        'Project Planning': 'Comprehensive project planning with Gantt charts, milestones, dependencies, and timelines',
        'Project Initiation': 'Professional project charter and kickoff documentation for stakeholder alignment',
        'Project Closure': 'Detailed project completion documentation with lessons learned and final deliverables',
        'Schedule Management': 'Comprehensive schedule tracking with milestones, dependencies, and critical path analysis',
        'Cost Management': 'Detailed budget management with cost tracking, forecasting, and variance analysis',
        'Scope Management': 'Professional scope definition, WBS development, and change control processes',
    }
    
    # Get base description
    base_desc = category_descriptions.get(category, f'Professional {category.lower()} template')
    
    # Add file format info
    format_info = {
        'xlsx': 'Excel format with built-in formulas and calculations',
        'docx': 'Word format with professional formatting and structure',
        'csv': 'CSV format for easy import into project management tools'
    }
    
    format_text = format_info.get(file_type, f'{file_type.upper()} format')
    
    return f'{base_desc}. {format_text}.'

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
        file_type = template.get('file_type', 'xlsx')
        
        # Extract proper name
        new_name = extract_template_name(filename)
        
        # Generate proper description
        new_description = generate_description(new_name, category, industry, file_type)
        
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
    for i, t in enumerate(templates[:10]):
        print(f"\n{i+1}. {t['name']}")
        print(f"   Category: {t['category']}")
        print(f"   Industry: {t['industry']}")
        print(f"   Description: {t['description'][:100]}...")

if __name__ == '__main__':
    fix_catalog()


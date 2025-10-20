#!/usr/bin/env python3
"""
Robust AI Components Data Seeding Script
Ensures AI Suggestor and AI Generator have all necessary configuration data
Never crashes - comprehensive error handling
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Template

# AI Suggestor Configuration
TEMPLATE_TYPES = [
    "Project Charter",
    "Project Plan",
    "Risk Management",
    "Quality Management",
    "Resource Management",
    "Communication Plan",
    "Stakeholder Management",
    "Budget Management",
    "Schedule Management",
    "Scope Management",
    "Procurement Management",
    "Change Management",
    "Issue Management",
    "Lessons Learned",
    "Status Report",
    "Project Closure"
]

SECTIONS = {
    "Project Charter": ["Objectives", "Scope", "Stakeholders", "Success Criteria", "Assumptions", "Constraints"],
    "Project Plan": ["Phases", "Milestones", "Deliverables", "Dependencies", "Resources", "Timeline"],
    "Risk Management": ["Risks", "Mitigation Strategies", "Contingency Plans", "Risk Owners", "Probability Assessment", "Impact Analysis"],
    "Quality Management": ["Quality Standards", "Quality Metrics", "Quality Control", "Quality Assurance", "Testing Procedures", "Acceptance Criteria"],
    "Resource Management": ["Team Roles", "Resource Allocation", "Skill Requirements", "Training Needs", "Resource Constraints", "Capacity Planning"],
    "Communication Plan": ["Stakeholder Communication", "Meeting Schedule", "Reporting Structure", "Communication Channels", "Escalation Procedures", "Documentation"],
    "Stakeholder Management": ["Stakeholder Identification", "Stakeholder Analysis", "Engagement Strategy", "Communication Needs", "Influence Assessment", "Stakeholder Register"],
    "Budget Management": ["Cost Estimates", "Budget Allocation", "Cost Control", "Financial Tracking", "Variance Analysis", "Funding Sources"],
    "Schedule Management": ["Timeline", "Critical Path", "Dependencies", "Milestones", "Resource Leveling", "Schedule Baseline"],
    "Scope Management": ["Scope Statement", "Deliverables", "Exclusions", "Acceptance Criteria", "Change Control", "Scope Verification"],
    "Procurement Management": ["Vendor Selection", "Contract Management", "Procurement Strategy", "Supplier Evaluation", "Purchase Orders", "Vendor Performance"],
    "Change Management": ["Change Requests", "Impact Assessment", "Approval Process", "Change Log", "Stakeholder Communication", "Implementation Plan"],
    "Issue Management": ["Issue Log", "Issue Resolution", "Escalation Procedures", "Issue Tracking", "Root Cause Analysis", "Preventive Actions"],
    "Lessons Learned": ["Successes", "Challenges", "Best Practices", "Recommendations", "Process Improvements", "Knowledge Transfer"],
    "Status Report": ["Progress Summary", "Accomplishments", "Upcoming Activities", "Issues and Risks", "Budget Status", "Schedule Status"],
    "Project Closure": ["Final Deliverables", "Acceptance Sign-off", "Resource Release", "Documentation Archive", "Post-Project Review", "Closure Report"]
}

# AI Generator Configuration
METHODOLOGIES = [
    "Agile",
    "Scrum",
    "Kanban",
    "Waterfall",
    "PRINCE2",
    "Lean",
    "Six Sigma",
    "Hybrid"
]

DOCUMENT_FORMATS = [
    "WORD",
    "EXCEL",
    "POWERPOINT"
]

def verify_openai_config():
    """Verify OpenAI API key is configured"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  WARNING: OPENAI_API_KEY not set in environment")
        return False
    
    if len(api_key) < 20:
        print("⚠️  WARNING: OPENAI_API_KEY appears to be invalid (too short)")
        return False
    
    print(f"✅ OpenAI API key configured (length: {len(api_key)})")
    return True

def verify_database_connection():
    """Verify database connection and template data"""
    try:
        with app.app_context():
            template_count = Template.query.count()
            industries = db.session.query(Template.industry).distinct().count()
            categories = db.session.query(Template.category).distinct().count()
            
            print(f"✅ Database connected")
            print(f"   Templates: {template_count}")
            print(f"   Industries: {industries}")
            print(f"   Categories: {categories}")
            
            if template_count == 0:
                print("⚠️  WARNING: No templates in database")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def verify_ai_suggestor_data():
    """Verify AI Suggestor has all necessary data"""
    print("\n📊 AI Suggestor Configuration:")
    print(f"   Template Types: {len(TEMPLATE_TYPES)}")
    print(f"   Sections Defined: {len(SECTIONS)}")
    
    # Verify all template types have sections
    missing_sections = []
    for template_type in TEMPLATE_TYPES:
        if template_type not in SECTIONS:
            missing_sections.append(template_type)
    
    if missing_sections:
        print(f"⚠️  WARNING: {len(missing_sections)} template types missing sections:")
        for tt in missing_sections:
            print(f"      - {tt}")
        return False
    
    # Verify section counts
    min_sections = min(len(sections) for sections in SECTIONS.values())
    max_sections = max(len(sections) for sections in SECTIONS.values())
    avg_sections = sum(len(sections) for sections in SECTIONS.values()) / len(SECTIONS)
    
    print(f"   Sections per type: {min_sections}-{max_sections} (avg: {avg_sections:.1f})")
    
    print("✅ AI Suggestor configuration complete")
    return True

def verify_ai_generator_data():
    """Verify AI Generator has all necessary data"""
    print("\n📊 AI Generator Configuration:")
    print(f"   Methodologies: {len(METHODOLOGIES)}")
    print(f"   Document Formats: {len(DOCUMENT_FORMATS)}")
    
    # List methodologies
    print("   Supported Methodologies:")
    for methodology in METHODOLOGIES:
        print(f"      - {methodology}")
    
    # List formats
    print("   Supported Formats:")
    for format_type in DOCUMENT_FORMATS:
        print(f"      - {format_type}")
    
    print("✅ AI Generator configuration complete")
    return True

def verify_template_categories():
    """Verify template categories match AI Suggestor template types"""
    try:
        with app.app_context():
            db_categories = set(row[0] for row in db.session.query(Template.category).distinct().all())
            config_types = set(TEMPLATE_TYPES)
            
            print("\n📊 Template Category Alignment:")
            print(f"   Database Categories: {len(db_categories)}")
            print(f"   Config Template Types: {len(config_types)}")
            
            # Find mismatches
            in_db_not_config = db_categories - config_types
            in_config_not_db = config_types - db_categories
            
            if in_db_not_config:
                print(f"   ⚠️  Categories in DB but not in config: {len(in_db_not_config)}")
                for cat in sorted(in_db_not_config)[:10]:  # Show first 10
                    print(f"      - {cat}")
                if len(in_db_not_config) > 10:
                    print(f"      ... and {len(in_db_not_config) - 10} more")
            
            if in_config_not_db:
                print(f"   ℹ️  Types in config but not in DB: {len(in_config_not_db)}")
                for tt in sorted(in_config_not_db)[:10]:
                    print(f"      - {tt}")
            
            if not in_db_not_config and not in_config_not_db:
                print("   ✅ Perfect alignment between DB and config")
            
            return True
            
    except Exception as e:
        print(f"❌ Category verification failed: {e}")
        return False

def seed_ai_components(mode='verify'):
    """
    Seed AI components configuration
    
    Modes:
    - 'verify': Only check without making changes
    - 'export': Export current configuration to JSON
    """
    
    print("=" * 80)
    print("AI COMPONENTS DATA SEEDING")
    print("=" * 80)
    print(f"Mode: {mode}")
    print()
    
    try:
        # Verify OpenAI configuration
        openai_ok = verify_openai_config()
        
        # Verify database connection
        db_ok = verify_database_connection()
        
        # Verify AI Suggestor data
        suggestor_ok = verify_ai_suggestor_data()
        
        # Verify AI Generator data
        generator_ok = verify_ai_generator_data()
        
        # Verify template category alignment
        alignment_ok = verify_template_categories()
        
        # Export configuration if requested
        if mode == 'export':
            import json
            config = {
                'template_types': TEMPLATE_TYPES,
                'sections': SECTIONS,
                'methodologies': METHODOLOGIES,
                'document_formats': DOCUMENT_FORMATS
            }
            
            output_file = 'ai_components_config.json'
            with open(output_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"\n✅ Configuration exported to {output_file}")
        
        # Print summary
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"OpenAI API: {'✅ OK' if openai_ok else '❌ FAIL'}")
        print(f"Database: {'✅ OK' if db_ok else '❌ FAIL'}")
        print(f"AI Suggestor: {'✅ OK' if suggestor_ok else '❌ FAIL'}")
        print(f"AI Generator: {'✅ OK' if generator_ok else '❌ FAIL'}")
        print(f"Category Alignment: {'✅ OK' if alignment_ok else '❌ FAIL'}")
        print("=" * 80)
        
        all_ok = openai_ok and db_ok and suggestor_ok and generator_ok and alignment_ok
        
        if all_ok:
            print("\n🎉 All AI components configured correctly!")
        else:
            print("\n⚠️  Some components need attention")
        
        return all_ok
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed AI components configuration')
    parser.add_argument('--mode', choices=['verify', 'export'], 
                       default='verify', help='Operation mode')
    
    args = parser.parse_args()
    
    success = seed_ai_components(mode=args.mode)
    sys.exit(0 if success else 1)


#!/usr/bin/env python3
"""
Migration: Delete Product, IT, and Finance templates with wrong content.
Keep only templates whose filenames match the correct files from upload folder.
"""

from models import Template, db

def run_migration():
    """Delete Product/IT/Finance templates that are NOT in the correct list"""
    
    # List of CORRECT template filenames (from upload folder)
    correct_filenames = {
        # Finance (24 files - but some are duplicates with different extensions)
        'Finance_Action_Item_Log.xlsx',
        'Finance_Business_Case.docx',
        'Finance_Change_Management_Plan.xlsx',
        'Finance_Communication_Plan.xlsx',
        'Finance_Comprehensive_Budget.xlsx',
        'Finance_Data_Readiness_Assessment.docx',
        'Finance_Fit_Gap_Assessment.docx',
        'Finance_KPI_Dashboard.xlsx',
        'Finance_Lessons_Learned.xlsx',
        'Finance_Procurement_Plan.xlsx',
        'Finance_Project_Charter.docx',
        'Finance_Project_Closure_Report.docx',
        'Finance_Project_Plan.xlsx',
        'Finance_Project_Proposal.docx',
        'Finance_RAID_Log.xlsx',
        'Finance_Requirements_Traceability_Matrix.xlsx',
        'Finance_Resource_Management_Plan.xlsx',
        'Finance_Resource_Plan_Staffing_Plan.xlsx',
        'Finance_Risk_Management_Plan.xlsx',
        'Finance_Stakeholder_Engagement_Plan.xlsx',
        'Finance_Stakeholder_Register.xlsx',
        'Finance_Training_Budget_Estimates.xlsx',
        'Finance_Training_Needs_Assessment.docx',
        'Finance_Training_Schedule.xlsx',
        
        # IT (17 files)
        'IT_Change_Management_Plan.xlsx',
        'IT_Communications_Management_Plan.xlsx',
        'IT_Comprehensive_Budget.xlsx',
        'IT_KPI_Dashboard.xlsx',
        'IT_Procurement_Management_Plan.xlsx',
        'IT_Project_Charter.docx',
        'IT_Project_Closure_Report.xlsx',
        'IT_Quality_Management_Plan.xlsx',
        'IT_RAID_Log.xlsx',
        'IT_Requirements_Traceability_Matrix.xlsx',
        'IT_Risk_Management_Plan.xlsx',
        'IT_Stakeholder_Engagement_Plan.xlsx',
        'IT_Stakeholder_Register_Analysis.xlsx',
        'IT_Training_Budget_Estimates.xlsx',
        'IT_Training_Needs_Assessment.xlsx',
        'IT_Training_Schedule.xlsx',
        'IT_WBS.xlsx',
        
        # Product (14 files - excluding duplicate)
        'Product_Change_Management_Plan.xlsx',
        'Product_Communication_Plan.xlsx',
        'Product_Comprehensive_Budget.xlsx',
        'Product_KPI_Dashboard.xlsx',
        'Product_Procurement_Plan.xlsx',
        'Product_Project_Charter.docx',
        'Product_RAID_Log.xlsx',
        'Product_Resource_Management_Plan.xlsx',
        'Product_Resource_Plan_Staffing_Plan.xlsx',
        'Product_Risk_Management_Plan.xlsx',
        'Product_Stakeholder_Engagement_Plan.xlsx',
        'Product_Stakeholder_Register.xlsx',
        'Product_Training_Budget_Estimates.xlsx',
        'Product_Training_Schedule.xlsx',
    }
    
    # Get all Product, IT, and Finance templates from database
    templates_to_check = Template.query.filter(
        Template.industry.in_(['Product', 'IT', 'Finance'])
    ).all()
    
    # Find templates that are NOT in the correct list
    templates_to_delete = []
    for template in templates_to_check:
        if template.file_path not in correct_filenames:
            templates_to_delete.append(template)
    
    if not templates_to_delete:
        print("✅ No templates to delete - all templates are correct")
        return True
    
    print(f"🗑️  Deleting {len(templates_to_delete)} templates with wrong content:")
    
    product_delete = [t for t in templates_to_delete if t.industry == 'Product']
    it_delete = [t for t in templates_to_delete if t.industry == 'IT']
    finance_delete = [t for t in templates_to_delete if t.industry == 'Finance']
    
    print(f"  Product: {len(product_delete)}")
    print(f"  IT: {len(it_delete)}")
    print(f"  Finance: {len(finance_delete)}")
    
    # Delete templates
    for template in templates_to_delete:
        db.session.delete(template)
    
    db.session.commit()
    
    print(f"✅ MIGRATION COMPLETE!")
    print(f"Deleted {len(templates_to_delete)} templates with wrong content")
    print(f"Remaining templates:")
    print(f"  Product: {Template.query.filter_by(industry='Product').count()}")
    print(f"  IT: {Template.query.filter_by(industry='IT').count()}")
    print(f"  Finance: {Template.query.filter_by(industry='Finance').count()}")
    print(f"  Total: {Template.query.count()}")
    
    return True


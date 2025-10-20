from flask import Blueprint, jsonify
from models import db, Template
import logging

logger = logging.getLogger(__name__)

run_category_fix_bp = Blueprint('run_category_fix', __name__)

@run_category_fix_bp.route('/api/run-category-fix', methods=['POST'])
def run_category_fix():
    """Run category name standardization on demand"""
    try:
        # Define category mappings
        mappings = {
            'Open Action Item Log': 'Action Item Log',
            'Development Open Action Item Log': 'Action Item Log',
            'Implementation Open Action Item Log': 'Action Item Log',
            'Comprehensive Budget': 'Budget',
            'Comprehensive Budget with Instructions': 'Budget',
            'Training Budget Estimates': 'Training Budget',
            'KPI Dashboard': 'KPI Report',
            'KPI Report Dashboard': 'KPI Report',
            'Development KPI Report Dashboard': 'KPI Report',
            'Implementation KPI Report Dashboard': 'KPI Report',
            'Development Lessons Learned': 'Lessons Learned',
            'Implementation Lessons Learned': 'Lessons Learned',
            'Development Project Proposal': 'Project Proposal',
            'Implementation Project Proposal': 'Project Proposal',
            'Comprehensive Project Proposal Essay': 'Project Proposal',
            'Executive RAID Log Complete': 'RAID Log',
            'KPI Dashboard with Instructions': 'KPI Dashboard'
        }
        
        total_updated = 0
        results = {}
        
        for old_name, new_name in mappings.items():
            templates = Template.query.filter_by(category=old_name).all()
            count = len(templates)
            
            if count > 0:
                for template in templates:
                    template.category = new_name
                
                results[old_name] = {
                    'count': count,
                    'new_name': new_name
                }
                total_updated += count
                logger.info(f"Updated {count} templates from '{old_name}' to '{new_name}'")
        
        db.session.commit()
        logger.info(f"Category standardization complete: {total_updated} templates updated")
        
        return jsonify({
            'status': 'success',
            'total_updated': total_updated,
            'details': results
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Category standardization failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


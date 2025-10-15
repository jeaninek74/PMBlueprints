"""
Route to fix template and industry names
"""
from flask import Blueprint, jsonify, request

fix_names_bp = Blueprint('fix_names', __name__)

# Industry name corrections
INDUSTRY_CORRECTIONS = {
    "Business": "Business Process Improvement",
    "Cloud": "Cloud Migration",
    "Customer": "Customer Experience",
    "Data": "Data Analytics",
    "Digital": "Digital Transformation",
    "Hardware": "Hardware Development",
    "Media": "Media & Entertainment",
    "Merger": "Merger & Acquisition",
    "Network": "Network Infrastructure",
    "Operational": "Operational Excellence",
    "Operations": "Operations Management",
    "Product": "Product Development",
    "Research": "Research & Development"
}

@fix_names_bp.route('/admin/fix-names', methods=['POST'])
def fix_names():
    """Fix industry and template names"""
    from app import db
    
    secret = request.headers.get('X-Fix-Secret')
    if secret != 'pmb-fix-2025':
        return jsonify({'error': 'Unauthorized'}), 401
    
    results = {
        'industries_updated': 0,
        'templates_checked': 0,
        'errors': []
    }
    
    try:
        # Fix industry names using raw SQL to avoid circular imports
        for old_name, new_name in INDUSTRY_CORRECTIONS.items():
            result = db.session.execute(
                db.text("UPDATE template SET industry = :new WHERE industry = :old"),
                {"new": new_name, "old": old_name}
            )
            count = result.rowcount
            if count > 0:
                results['industries_updated'] += count
                print(f"Updated {count} templates: '{old_name}' → '{new_name}'")
        
        db.session.commit()
        
        # Count templates
        result = db.session.execute(db.text("SELECT COUNT(*) FROM template"))
        results['templates_checked'] = result.scalar()
        
        return jsonify({
            'success': True,
            'message': 'Names fixed successfully',
            'results': results
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


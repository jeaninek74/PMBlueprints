"""
Route to fix template names based on filenames
"""
from flask import Blueprint, jsonify, request

fix_template_names_bp = Blueprint('fix_template_names', __name__)

@fix_template_names_bp.route('/admin/fix-template-names', methods=['POST'])
def fix_template_names():
    """Fix template names to match filenames"""
    
    # Security check
    secret = request.headers.get('X-Init-Secret')
    import os
    expected_secret = os.getenv('INIT_SECRET', 'pmb-init-2025')
    
    if secret != expected_secret:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from database import db
        
        # Get all templates
        result = db.session.execute(db.text("SELECT id, name, filename FROM template ORDER BY id"))
        templates = result.fetchall()
        
        results = {
            'total': len(templates),
            'updated': 0,
            'unchanged': 0,
            'changes': []
        }
        
        for template_id, current_name, filename in templates:
            # Extract proper name from filename
            # Remove extension and convert underscores to spaces
            filename_base = filename.rsplit('.', 1)[0]
            proper_name = filename_base.replace('_', ' ')
            
            # Update if different
            if proper_name != current_name:
                db.session.execute(
                    db.text("UPDATE template SET name = :name WHERE id = :id"),
                    {"name": proper_name, "id": template_id}
                )
                results['updated'] += 1
                
                # Store first 20 changes for display
                if len(results['changes']) < 20:
                    results['changes'].append({
                        'id': template_id,
                        'old': current_name,
                        'new': proper_name
                    })
            else:
                results['unchanged'] += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Updated {results["updated"]} template names',
            'results': results
        })
        
    except Exception as e:
        import traceback
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500




@fix_template_names_bp.route('/admin/fix-template-names-page', methods=['GET'])
def fix_template_names_page():
    """Admin page to fix template names"""
    from flask import render_template
    return render_template('admin/fix_template_names.html')


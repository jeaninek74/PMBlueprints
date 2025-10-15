"""
Comprehensive route to fix ALL template and industry issues
"""
from flask import Blueprint, jsonify, request
import os

fix_all_templates_bp = Blueprint('fix_all_templates', __name__)

@fix_all_templates_bp.route('/admin/fix-all-templates', methods=['POST'])
def fix_all_templates():
    """Fix all template names and industry names in database"""
    
    # Security check
    secret = request.headers.get('X-Init-Secret')
    expected_secret = os.getenv('INIT_SECRET', 'pmb-init-2025')
    
    if secret != expected_secret:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from app import db
        
        results = {
            'template_names_updated': 0,
            'industry_names_updated': 0,
            'changes': []
        }
        
        # FIX 1: Template Name Corrections
        # "Planning" → "Project Plan"
        # "Project Planning" → "Project Plan"
        template_name_fixes = {
            "Planning": "Project Plan",
            "Project Planning": "Project Plan",
            "WBS": "Project Plan"
        }
        
        for old_name, new_name in template_name_fixes.items():
            result = db.session.execute(
                db.text("UPDATE template SET name = :new WHERE name = :old"),
                {"new": new_name, "old": old_name}
            )
            count = result.rowcount
            if count > 0:
                results['template_names_updated'] += count
                results['changes'].append({
                    'type': 'template_name',
                    'from': old_name,
                    'to': new_name,
                    'count': count
                })
        
        # FIX 2: Industry Name Corrections
        industry_fixes = {
            "Hardware Development": "Hardware Implementation",
            "Operational Excellence": "Operational Improvement",
            "Operations Management": "Operational Improvement",
            "R&D": "Research & Development",
            "Business": "Business Process Improvement",
            "Cloud": "Cloud Migration",
            "Customer": "Customer Experience",
            "Data": "Data Analytics",
            "Digital": "Digital Transformation",
            "Hardware": "Hardware Implementation",
            "Media": "Media & Entertainment",
            "Merger": "Merger & Acquisition",
            "Network": "Network Infrastructure",
            "Operational": "Operational Improvement",
            "Operations": "Operational Improvement",
            "Product": "Product Development",
            "Research": "Research & Development"
        }
        
        for old_name, new_name in industry_fixes.items():
            result = db.session.execute(
                db.text("UPDATE template SET industry = :new WHERE industry = :old"),
                {"new": new_name, "old": old_name}
            )
            count = result.rowcount
            if count > 0:
                results['industry_names_updated'] += count
                results['changes'].append({
                    'type': 'industry_name',
                    'from': old_name,
                    'to': new_name,
                    'count': count
                })
        
        db.session.commit()
        
        # Get statistics
        result = db.session.execute(db.text("SELECT COUNT(*) FROM template"))
        total_templates = result.scalar()
        
        result = db.session.execute(db.text("SELECT COUNT(DISTINCT name) FROM template"))
        unique_names = result.scalar()
        
        result = db.session.execute(db.text("SELECT COUNT(DISTINCT industry) FROM template"))
        unique_industries = result.scalar()
        
        # Get current template names
        result = db.session.execute(db.text("SELECT DISTINCT name FROM template ORDER BY name"))
        template_names = [row[0] for row in result]
        
        # Get current industries
        result = db.session.execute(db.text("SELECT DISTINCT industry FROM template ORDER BY industry"))
        industries = [row[0] for row in result]
        
        return jsonify({
            'status': 'success',
            'message': f'Fixed {results["template_names_updated"]} template names and {results["industry_names_updated"]} industry names',
            'results': results,
            'statistics': {
                'total_templates': total_templates,
                'unique_names': unique_names,
                'unique_industries': unique_industries
            },
            'current_template_names': template_names,
            'current_industries': industries
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        if 'db' in locals():
            db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@fix_all_templates_bp.route('/admin/fix-all-templates-page')
def fix_all_templates_page():
    """Admin page to fix all template and industry issues"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fix All Templates - PMBlueprints Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-10">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h3 class="mb-0"><i class="fas fa-tools me-2"></i>Fix All Templates & Industries</h3>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info">
                            <h5><i class="fas fa-info-circle me-2"></i>What This Does:</h5>
                            <p class="mb-2">This tool will fix ALL template and industry name issues:</p>
                            <h6>Template Name Fixes:</h6>
                            <ul>
                                <li>"Planning" → "Project Plan"</li>
                                <li>"Project Planning" → "Project Plan"</li>
                                <li>"WBS" → "Project Plan"</li>
                            </ul>
                            <h6>Industry Name Fixes:</h6>
                            <ul class="mb-0">
                                <li>"Hardware Development" → "Hardware Implementation"</li>
                                <li>"Operational Excellence" → "Operational Improvement"</li>
                                <li>"Operations Management" → "Operational Improvement"</li>
                                <li>"R&D" → "Research & Development"</li>
                                <li>And all other incomplete industry names...</li>
                            </ul>
                        </div>

                        <div id="result" class="alert d-none"></div>

                        <div class="d-grid gap-2">
                            <button id="fixBtn" class="btn btn-primary btn-lg" onclick="fixAll()">
                                <i class="fas fa-magic me-2"></i>Fix All Issues Now
                            </button>
                        </div>

                        <div id="progress" class="mt-3 d-none">
                            <div class="progress">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 100%"></div>
                            </div>
                            <p class="text-center mt-2">Processing...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function fixAll() {
            const btn = document.getElementById('fixBtn');
            const result = document.getElementById('result');
            const progress = document.getElementById('progress');
            
            btn.disabled = true;
            result.classList.add('d-none');
            progress.classList.remove('d-none');
            
            try {
                const response = await fetch('/admin/fix-all-templates', {
                    method: 'POST',
                    headers: {
                        'X-Init-Secret': 'pmb-init-2025'
                    }
                });
                
                const data = await response.json();
                
                progress.classList.add('d-none');
                result.classList.remove('d-none');
                
                if (data.status === 'success') {
                    result.className = 'alert alert-success';
                    result.innerHTML = `
                        <h5><i class="fas fa-check-circle me-2"></i>Success!</h5>
                        <p><strong>Template Names:</strong> ${data.results.template_names_updated} updated</p>
                        <p><strong>Industry Names:</strong> ${data.results.industry_names_updated} updated</p>
                        ${data.results.changes.length > 0 ? `
                        <h6>Changes Made:</h6>
                        <ul>
                            ${data.results.changes.map(c => `<li>[${c.type}] ${c.from} → ${c.to} (${c.count} templates)</li>`).join('')}
                        </ul>
                        ` : '<p>No changes needed - everything is already correct!</p>'}
                        <h6>Database Statistics:</h6>
                        <ul>
                            <li>Total Templates: ${data.statistics.total_templates}</li>
                            <li>Unique Template Names: ${data.statistics.unique_names}</li>
                            <li>Unique Industries: ${data.statistics.unique_industries}</li>
                        </ul>
                    `;
                } else {
                    result.className = 'alert alert-danger';
                    result.innerHTML = `
                        <h5><i class="fas fa-exclamation-circle me-2"></i>Error</h5>
                        <p>${data.message}</p>
                    `;
                }
            } catch (error) {
                progress.classList.add('d-none');
                result.classList.remove('d-none');
                result.className = 'alert alert-danger';
                result.innerHTML = `
                    <h5><i class="fas fa-exclamation-circle me-2"></i>Error</h5>
                    <p>${error.message}</p>
                `;
            }
            
            btn.disabled = false;
        }
    </script>
</body>
</html>
    '''


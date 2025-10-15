"""
Route to fix ACTUAL incorrect industry names in production database
"""
from flask import Blueprint, jsonify, request
import os

fix_actual_industries_bp = Blueprint('fix_actual_industries', __name__)

# These are the ACTUAL incorrect names currently in the database
ACTUAL_CORRECTIONS = {
    "Hardware Development": "Hardware Implementation",
    "Operational Excellence": "Operational Improvement",
    "Operations Management": "Operational Improvement",
    "R&D": "Research & Development"
}

@fix_actual_industries_bp.route('/admin/fix-actual-industries', methods=['POST'])
def fix_actual_industries():
    """Fix the ACTUAL incorrect industry names in database"""
    
    # Security check
    secret = request.headers.get('X-Init-Secret')
    expected_secret = os.getenv('INIT_SECRET', 'pmb-init-2025')
    
    if secret != expected_secret:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from app import db
        
        results = {
            'industries_updated': 0,
            'changes': []
        }
        
        # Fix industry names using raw SQL
        for old_name, new_name in ACTUAL_CORRECTIONS.items():
            result = db.session.execute(
                db.text("UPDATE template SET industry = :new WHERE industry = :old"),
                {"new": new_name, "old": old_name}
            )
            count = result.rowcount
            if count > 0:
                results['industries_updated'] += count
                results['changes'].append({
                    'from': old_name,
                    'to': new_name,
                    'count': count
                })
        
        db.session.commit()
        
        # Get updated industry list
        result = db.session.execute(db.text("SELECT DISTINCT industry FROM template ORDER BY industry"))
        industries = [row[0] for row in result]
        
        return jsonify({
            'status': 'success',
            'message': f'Updated {results["industries_updated"]} templates',
            'results': results,
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


@fix_actual_industries_bp.route('/admin/fix-actual-industries-page')
def fix_actual_industries_page():
    """Admin page to fix actual incorrect industry names"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fix Actual Industry Names - PMBlueprints Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h3 class="mb-0"><i class="fas fa-tools me-2"></i>Fix Actual Industry Names</h3>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-warning">
                            <h5><i class="fas fa-exclamation-triangle me-2"></i>What This Does:</h5>
                            <p class="mb-2">This tool will fix the ACTUAL incorrect industry names currently in your database:</p>
                            <ul class="mb-0">
                                <li>"Hardware Development" → "Hardware Implementation"</li>
                                <li>"Operational Excellence" → "Operational Improvement"</li>
                                <li>"Operations Management" → "Operational Improvement"</li>
                                <li>"R&D" → "Research & Development"</li>
                            </ul>
                        </div>

                        <div id="result" class="alert d-none"></div>

                        <div class="d-grid gap-2">
                            <button id="fixBtn" class="btn btn-primary btn-lg" onclick="fixNames()">
                                <i class="fas fa-magic me-2"></i>Fix Industry Names Now
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
        async function fixNames() {
            const btn = document.getElementById('fixBtn');
            const result = document.getElementById('result');
            const progress = document.getElementById('progress');
            
            btn.disabled = true;
            result.classList.add('d-none');
            progress.classList.remove('d-none');
            
            try {
                const response = await fetch('/admin/fix-actual-industries', {
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
                        <p><strong>${data.results.industries_updated}</strong> templates updated</p>
                        ${data.results.changes.length > 0 ? `
                        <h6>Changes Made:</h6>
                        <ul>
                            ${data.results.changes.map(c => `<li>${c.from} → ${c.to} (${c.count} templates)</li>`).join('')}
                        </ul>
                        ` : '<p>No changes needed - all industry names are already correct!</p>'}
                        <h6>Current Industries (${data.current_industries.length}):</h6>
                        <ul>
                            ${data.current_industries.map(i => `<li>${i}</li>`).join('')}
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


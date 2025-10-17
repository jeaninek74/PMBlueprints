"""
Advanced AI Generator for PMBlueprints
Integrates PMI 2025 PMBOK and comprehensive methodology knowledge
Generates professional PM documents with preview/edit capability
"""

from flask import Blueprint, request, jsonify, send_file
from flask_login import current_user
import os
import logging
from datetime import datetime
import tempfile
import json

# Import knowledge bases
from pmbok_2025_knowledge import pmbok_knowledge
from methodology_knowledge import methodology_knowledge
from pm_document_intelligence import pm_intelligence as pm_doc_intelligence

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
ai_gen_bp = Blueprint('ai_generator', __name__, url_prefix='/api/ai-generator')

# Check if OpenAI API key is available
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
AI_ENABLED = OPENAI_API_KEY is not None

if AI_ENABLED:
    try:
        from openai import OpenAI
        # Initialize with minimal config to avoid proxy issues
        client = OpenAI(api_key=OPENAI_API_KEY, max_retries=3, timeout=30.0)
        logger.info("OpenAI client initialized for AI Generator")
    except Exception as e:
        logger.warning(f"OpenAI client initialization warning: {e}")
        # Try basic initialization
        try:
            client = OpenAI()
            logger.info("OpenAI client initialized with default config")
        except Exception as e2:
            logger.debug(f"OpenAI init attempt: {e2}")
            AI_ENABLED = False


@ai_gen_bp.route('/analyze-request', methods=['POST'])
def analyze_document_request():
    """
    Analyze user's document request and provide intelligent recommendations
    
    Request body:
    {
        "document_name": "string",
        "project_context": "string" (optional),
        "methodology": "string" (optional)
    }
    
    Returns document intelligence, format recommendation, and structure guidance
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('document_name'):
            return jsonify({
                'success': False,
                'error': 'Document name is required'
            }), 400
        
        document_name = data.get('document_name', '')
        project_context = data.get('project_context', '')
        methodology = data.get('methodology', '')
        
        # Get document intelligence
        doc_info = pm_doc_intelligence.analyze_document_request(document_name)
        
        # Infer methodology if not provided
        if not methodology:
            methodology = methodology_knowledge.get_methodology_for_document(
                document_name, 
                project_context
            )
        
        # Get methodology details
        method_info = methodology_knowledge.get_methodology(methodology)
        
        # Adapt document to methodology
        adaptation = methodology_knowledge.adapt_document_to_methodology(
            doc_info['category'],
            methodology
        )
        
        # Get PMBOK mapping
        pmbok_area = pmbok_knowledge.get_knowledge_area_for_document(document_name)
        
        return jsonify({
            'success': True,
            'document_intelligence': {
                'name': document_name,
                'category': doc_info['category'],
                'recommended_format': doc_info['format'],
                'purpose': doc_info.get('content_guidance', 'Professional project management document'),
                'key_sections': doc_info['structure'],
                'pmbok_knowledge_area': pmbok_area if pmbok_area else 'Project Integration Management',
                'pmbok_process_group': 'Planning'
            },
            'methodology': {
                'name': method_info['name'] if method_info else methodology,
                'type': method_info['type'] if method_info else 'Unknown',
                'formality': adaptation['formality'],
                'detail_level': adaptation['detail_level'],
                'terminology': adaptation['terminology']
            },
            'recommendations': {
                'format': doc_info['format'],
                'methodology': methodology,
                'structure_guidance': adaptation['structure_guidance']
            }
        })
    
    except Exception as e:
        logger.error(f"Error analyzing document request: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_gen_bp.route('/generate-structure', methods=['POST'])
def generate_document_structure():
    """
    Generate document structure based on PM intelligence
    
    Request body:
    {
        "document_name": "string",
        "format": "word|excel|powerpoint|visio",
        "methodology": "string",
        "project_context": "string"
    }
    
    Returns detailed document structure ready for content generation
    """
    try:
        data = request.get_json()
        
        document_name = data.get('document_name', '')
        format_type = data.get('format', 'word')
        methodology = data.get('methodology', 'waterfall')
        
        # Handle methodology as either string or dict
        if isinstance(methodology, dict):
            methodology = methodology.get('name', 'waterfall')
        
        project_context = data.get('project_context', '')
        
        if not document_name:
            return jsonify({
                'success': False,
                'error': 'Document name is required'
            }), 400
        
        # Get document intelligence
        doc_info = pm_doc_intelligence.analyze_document_request(document_name)
        
        # Get methodology adaptation
        adaptation = methodology_knowledge.adapt_document_to_methodology(
            doc_info['category'],
            methodology
        )
        
        # Generate structure based on format
        if format_type == 'excel':
            structure = _generate_excel_structure(doc_info, adaptation, project_context)
        elif format_type == 'word':
            structure = _generate_word_structure(doc_info, adaptation, project_context)
        elif format_type == 'powerpoint':
            structure = _generate_powerpoint_structure(doc_info, adaptation, project_context)
        elif format_type == 'visio':
            structure = _generate_visio_structure(doc_info, adaptation, project_context)
        else:
            structure = _generate_word_structure(doc_info, adaptation, project_context)
        
        return jsonify({
            'success': True,
            'structure': structure,
            'metadata': {
                'document_name': document_name,
                'format': format_type,
                'methodology': methodology,
                'generated_at': datetime.utcnow().isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error generating structure: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_gen_bp.route('/generate-content', methods=['POST'])
def generate_document_content():
    """
    Generate full document content using AI with PM intelligence
    
    Request body:
    {
        "document_name": "string",
        "format": "word|excel|powerpoint|visio",
        "methodology": "string",
        "project_context": "string",
        "structure": {} (from generate-structure)
    }
    
    Returns generated content ready for preview/edit
    """
    try:
        # Check AI generation limit
        limit_check = check_ai_generation_limit(current_user if current_user.is_authenticated else None)
        if not limit_check['allowed']:
            return jsonify({
                'success': False,
                'error': limit_check['error'],
                'upgrade_required': limit_check.get('upgrade_required', False),
                'current_plan': limit_check.get('current_plan'),
                'usage': limit_check.get('usage'),
                'limit': limit_check.get('limit')
            }), 403
        
        if not AI_ENABLED:
            return jsonify({
                'success': False,
                'error': 'AI generation is not available'
            }), 503
        
        data = request.get_json()
        
        document_name = data.get('document_name', '')
        format_type = data.get('format', 'word')
        methodology = data.get('methodology', 'waterfall')
        
        # Handle methodology as either string or dict
        if isinstance(methodology, dict):
            methodology = methodology.get('name', 'waterfall')
        
        project_context = data.get('project_context', '')
        structure = data.get('structure', {})
        
        if not document_name or not project_context:
            return jsonify({
                'success': False,
                'error': 'Document name and project context are required'
            }), 400
        
        # Get PM intelligence
        doc_info = pm_doc_intelligence.analyze_document_request(document_name)
        method_info = methodology_knowledge.get_methodology(methodology)
        pmbok_info = pmbok_knowledge.get_knowledge_area_for_document(document_name)
        
        # Build comprehensive prompt with PM intelligence
        prompt = _build_generation_prompt(
            document_name=document_name,
            format_type=format_type,
            methodology=methodology,
            project_context=project_context,
            doc_info=doc_info,
            method_info=method_info,
            pmbok_info=pmbok_info,
            structure=structure
        )
        
        # Generate content with OpenAI
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert Project Management consultant with deep knowledge of PMI 2025 PMBOK standards and all major PM methodologies. 
                    
You generate professional, comprehensive, and methodology-appropriate project management documents. 

Your documents:
- Follow PMI 2025 PMBOK standards
- Adapt to the specified methodology (Scrum, Waterfall, SAFe, etc.)
- Use methodology-appropriate terminology
- Include realistic, contextual content
- Are immediately usable by project managers
- Follow professional formatting standards

Generate complete, professional content that project managers can use directly."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=3000,
            temperature=0.7
        )
        
        generated_content = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'content': generated_content,
            'metadata': {
                'document_name': document_name,
                'format': format_type,
                'methodology': methodology,
                'pmbok_knowledge_area': pmbok_info['knowledge_area'],
                'generated_at': datetime.utcnow().isoformat(),
                'tokens_used': response.usage.total_tokens
            }
        })
    
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_gen_bp.route('/preview', methods=['POST'])
def preview_document():
    """
    Generate preview of document for editing before download
    
    Request body:
    {
        "content": "string",
        "format": "word|excel|powerpoint|visio",
        "document_name": "string"
    }
    
    Returns formatted preview HTML
    """
    try:
        data = request.get_json()
        
        content = data.get('content', '')
        format_type = data.get('format', 'word')
        document_name = data.get('document_name', 'document')
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        # Format content for preview based on document type
        preview_html = _format_preview(content, format_type, document_name)
        
        return jsonify({
            'success': True,
            'preview_html': preview_html,
            'editable': True
        })
    
    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ========== HELPER FUNCTIONS ==========

def _generate_excel_structure(doc_info, adaptation, context):
    """Generate Excel spreadsheet structure"""
    # Handle structure as list or dict
    structure = doc_info.get('structure', [])
    if isinstance(structure, list):
        columns = structure if structure else ['ID', 'Description', 'Owner', 'Status', 'Priority', 'Notes']
    else:
        columns = structure.get('columns', ['ID', 'Description', 'Owner', 'Status', 'Priority', 'Notes'])
    
    return {
        'type': 'excel',
        'sheets': [
            {
                'name': doc_info['category'].title(),
                'columns': columns,
                'formatting': {
                    'header_style': 'bold',
                    'freeze_panes': 'A2',
                    'auto_filter': True
                }
            }
        ],
        'formulas': [],
        'data_validation': []
    }


def _generate_word_structure(doc_info, adaptation, context):
    """Generate Word document structure"""
    # Handle structure as list or dict
    structure = doc_info.get('structure', [])
    if isinstance(structure, list):
        sections = structure if structure else ['Executive Summary', 'Introduction', 'Objectives', 'Scope', 'Deliverables', 'Timeline', 'Resources', 'Risks', 'Conclusion']
    else:
        sections = structure.get('sections', ['Executive Summary', 'Introduction', 'Objectives', 'Scope', 'Deliverables', 'Timeline', 'Resources', 'Risks', 'Conclusion'])
    
    return {
        'type': 'word',
        'sections': sections,
        'formatting': {
            'heading_1': 'Title',
            'heading_2': 'Section',
            'heading_3': 'Subsection',
            'body': 'Normal'
        },
        'page_setup': {
            'margins': '1 inch',
            'orientation': 'portrait'
        }
    }


def _generate_powerpoint_structure(doc_info, adaptation, context):
    """Generate PowerPoint presentation structure"""
    return {
        'type': 'powerpoint',
        'slides': doc_info['structure'].get('slides', [
            {'title': 'Title Slide', 'layout': 'title'},
            {'title': 'Agenda', 'layout': 'content'},
            {'title': 'Overview', 'layout': 'content'},
            {'title': 'Key Points', 'layout': 'bullets'},
            {'title': 'Next Steps', 'layout': 'bullets'},
            {'title': 'Questions', 'layout': 'title'}
        ]),
        'theme': 'professional',
        'master_slide': 'default'
    }


def _generate_visio_structure(doc_info, adaptation, context):
    """Generate Visio diagram structure"""
    return {
        'type': 'visio',
        'diagram_type': doc_info['structure'].get('diagram_type', 'flowchart'),
        'elements': doc_info['structure'].get('elements', [
            'Start', 'Process', 'Decision', 'End'
        ]),
        'layout': 'hierarchical',
        'connectors': 'arrows'
    }


def _build_generation_prompt(document_name, format_type, methodology, project_context, 
                             doc_info, method_info, pmbok_info, structure):
    """Build comprehensive prompt with all PM intelligence"""
    
    prompt = f"""Generate a professional {document_name} for the following project:

**Project Context:**
{project_context}

**Document Requirements:**
- Format: {format_type.upper()}
- Methodology: {methodology} ({method_info['type'] if method_info else 'Traditional'})
- PMI 2025 PMBOK Knowledge Area: {pmbok_info['knowledge_area']}
- PMI 2025 PMBOK Process Group: {pmbok_info['process_group']}

**Document Purpose:**
{doc_info['purpose']}

**Methodology Characteristics:**
- Formality Level: {method_info['document_characteristics']['formality'] if method_info else 'High'}
- Detail Level: {method_info['document_characteristics']['detail_level'] if method_info else 'Comprehensive'}
- Documentation Volume: {method_info['document_characteristics']['documentation_volume'] if method_info else 'Moderate'}

**Required Structure:**
{json.dumps(structure, indent=2)}

**Instructions:**
1. Use {methodology}-appropriate terminology and language
2. Follow PMI 2025 PMBOK standards for {pmbok_info['knowledge_area']}
3. Include realistic, contextual content based on the project description
4. Make the document immediately usable by a project manager
5. Follow professional formatting standards for {format_type}
6. Include all standard sections for a {document_name}
7. Be specific, actionable, and comprehensive

Generate the complete {document_name} now:"""
    
    return prompt


def _format_preview(content, format_type, document_name):
    """Format content for HTML preview"""
    
    # Basic HTML formatting
    html = f"""
    <div class="document-preview">
        <div class="document-header">
            <h2>{document_name}</h2>
            <p class="document-meta">Format: {format_type.upper()} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        <div class="document-content">
            <pre style="white-space: pre-wrap; font-family: Arial, sans-serif;">{content}</pre>
        </div>
    </div>
    """
    
    return html


def register_ai_generator_routes(app):
    """Register AI Generator routes with Flask app"""
    app.register_blueprint(ai_gen_bp)
    logger.info("Advanced AI Generator routes registered")



@ai_gen_bp.route('/download', methods=['POST'])
def download_document():
    """
    Generate and download final document file
    """
    try:
        from document_generator import document_generator
        
        data = request.get_json()
        
        content = data.get('content', '')
        document_name = data.get('document_name', 'PM_Document')
        format_type = data.get('format', 'word')
        structure = data.get('structure', {})
        metadata = data.get('metadata', {})
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        # Add user info
        metadata['generated_by'] = current_user.email
        metadata['user_id'] = current_user.id
        
        # Generate document
        if format_type == 'word':
            filepath = document_generator.generate_word_document(content, document_name, structure, metadata)
        elif format_type == 'excel':
            filepath = document_generator.generate_excel_document(content, document_name, structure, metadata)
        elif format_type == 'powerpoint':
            filepath = document_generator.generate_powerpoint_document(content, document_name, structure, metadata)
        else:
            return jsonify({'success': False, 'error': f'Unsupported format: {format_type}'}), 400
        
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        
    except Exception as e:
        logger.error(f"Error downloading document: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

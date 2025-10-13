/**
 * AI Generator - Simplified Interface
 * Handles template generation workflow with preview
 */

let generatedTemplateData = null;

// Initialize AI Generator
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('aiGeneratorForm');
    if (form) {
        form.addEventListener('submit', handleGenerateTemplate);
    }
    
    // Download button
    const downloadBtn = document.getElementById('downloadGeneratedBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', handleDownloadTemplate);
    }
    
    // Generate new button
    const generateNewBtn = document.getElementById('generateNewBtn');
    if (generateNewBtn) {
        generateNewBtn.addEventListener('click', resetForm);
    }
    
    // Retry button
    const retryBtn = document.getElementById('retryBtn');
    if (retryBtn) {
        retryBtn.addEventListener('click', resetForm);
    }
});

/**
 * Handle template generation
 */
async function handleGenerateTemplate(e) {
    e.preventDefault();
    
    const documentName = document.getElementById('aiDocumentName').value.trim();
    const projectContext = document.getElementById('aiProjectContext').value.trim();
    const format = document.getElementById('aiDocumentFormat').value;
    
    if (!documentName) {
        showError('Please enter a template name');
        return;
    }
    
    // Hide form, show progress
    document.getElementById('aiGeneratorForm').style.display = 'none';
    document.getElementById('aiGenerationProgress').style.display = 'block';
    document.getElementById('aiPreview').style.display = 'none';
    document.getElementById('aiError').style.display = 'none';
    
    try {
        // Step 1: Analyze request
        updateProgress(20, 'Analyzing your request...', 'Understanding document requirements...');
        const analysis = await analyzeRequest(documentName, projectContext);
        
        // Step 2: Generate structure
        updateProgress(40, 'Creating document structure...', 'Building template framework...');
        const structure = await generateStructure(documentName, projectContext, analysis);
        
        // Step 3: Generate content
        updateProgress(60, 'Generating content...', 'Creating professional content based on PMI standards...');
        const content = await generateContent(documentName, projectContext, structure);
        
        // Step 4: Create document
        updateProgress(80, 'Creating document...', 'Formatting and finalizing your template...');
        const document = await createDocument(documentName, projectContext, structure, content, format);
        
        // Step 5: Show preview
        updateProgress(100, 'Complete!', 'Your template is ready');
        
        // Store generated data
        generatedTemplateData = document;
        
        // Show preview
        setTimeout(() => {
            showPreview(document);
        }, 500);
        
    } catch (error) {
        console.error('Generation error:', error);
        showError(error.message || 'Failed to generate template. Please try again.');
    }
}

/**
 * Step 1: Analyze document request
 */
async function analyzeRequest(documentName, projectContext) {
    const response = await fetch('/api/ai-generator/analyze-request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            document_name: documentName,
            project_context: projectContext
        })
    });
    
    if (!response.ok) {
        throw new Error('Failed to analyze request');
    }
    
    return await response.json();
}

/**
 * Step 2: Generate document structure
 */
async function generateStructure(documentName, projectContext, analysis) {
    const response = await fetch('/api/ai-generator/generate-structure', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            document_name: documentName,
            project_context: projectContext,
            analysis: analysis
        })
    });
    
    if (!response.ok) {
        throw new Error('Failed to generate structure');
    }
    
    return await response.json();
}

/**
 * Step 3: Generate content
 */
async function generateContent(documentName, projectContext, structure) {
    const response = await fetch('/api/ai-generator/generate-content', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            document_name: documentName,
            project_context: projectContext,
            structure: structure
        })
    });
    
    if (!response.ok) {
        throw new Error('Failed to generate content');
    }
    
    return await response.json();
}

/**
 * Step 4: Create document
 */
async function createDocument(documentName, projectContext, structure, content, format) {
    const response = await fetch('/api/ai-generator/preview', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            document_name: documentName,
            project_context: projectContext,
            structure: structure,
            content: content,
            format: format
        })
    });
    
    if (!response.ok) {
        throw new Error('Failed to create document');
    }
    
    return await response.json();
}

/**
 * Show preview of generated template
 */
function showPreview(data) {
    document.getElementById('aiGenerationProgress').style.display = 'none';
    document.getElementById('aiPreview').style.display = 'block';
    
    // Populate preview
    document.getElementById('previewDocName').textContent = data.document_name || 'Generated Template';
    document.getElementById('previewFormat').textContent = data.format ? data.format.toUpperCase() : 'DOCX';
    
    // Show structure
    const structureDiv = document.getElementById('previewStructure');
    if (data.structure && data.structure.sections) {
        structureDiv.innerHTML = '<ul class="mb-0">' + 
            data.structure.sections.map(section => `<li>${section}</li>`).join('') + 
            '</ul>';
    } else {
        structureDiv.textContent = 'Professional document structure';
    }
    
    // Show content preview
    const contentDiv = document.getElementById('previewContent');
    if (data.content_preview) {
        contentDiv.innerHTML = '<pre class="mb-0" style="white-space: pre-wrap;">' + 
            escapeHtml(data.content_preview) + 
            '</pre>';
    } else {
        contentDiv.textContent = 'Content generated successfully. Download to view full template.';
    }
}

/**
 * Handle template download
 */
async function handleDownloadTemplate() {
    if (!generatedTemplateData) {
        showError('No template data available');
        return;
    }
    
    try {
        const response = await fetch('/api/ai-generator/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(generatedTemplateData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to download template');
        }
        
        // Get filename from response headers
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'template.docx';
        if (contentDisposition) {
            const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
            if (matches && matches[1]) {
                filename = matches[1].replace(/['"]/g, '');
            }
        }
        
        // Download file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Show success message
        alert('Template downloaded successfully!');
        
    } catch (error) {
        console.error('Download error:', error);
        showError('Failed to download template. Please try again.');
    }
}

/**
 * Update progress bar
 */
function updateProgress(percent, status, message) {
    const progressBar = document.getElementById('progressBar');
    const progressStatus = document.getElementById('progressStatus');
    const progressMessage = document.getElementById('progressMessage');
    
    if (progressBar) {
        progressBar.style.width = percent + '%';
        progressBar.textContent = percent + '%';
    }
    
    if (progressStatus) {
        progressStatus.textContent = status;
    }
    
    if (progressMessage) {
        progressMessage.textContent = message;
    }
}

/**
 * Show error message
 */
function showError(message) {
    document.getElementById('aiGeneratorForm').style.display = 'block';
    document.getElementById('aiGenerationProgress').style.display = 'none';
    document.getElementById('aiPreview').style.display = 'none';
    document.getElementById('aiError').style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
}

/**
 * Reset form
 */
function resetForm() {
    document.getElementById('aiGeneratorForm').style.display = 'block';
    document.getElementById('aiGenerationProgress').style.display = 'none';
    document.getElementById('aiPreview').style.display = 'none';
    document.getElementById('aiError').style.display = 'none';
    document.getElementById('aiGeneratorForm').reset();
    generatedTemplateData = null;
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


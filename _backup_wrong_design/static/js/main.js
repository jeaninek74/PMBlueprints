/**
 * PMBlueprints Main JavaScript
 * Handles all form interactions, dropdowns, and dynamic functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('PMBlueprints JavaScript loaded');
    
    // Initialize all functionality
    initializeDropdowns();
    initializeAIGenerator();
    initializeTemplateFiltering();
    initializeForms();
});

/**
 * Initialize dropdown functionality
 */
function initializeDropdowns() {
    const industrySelect = document.getElementById('industrySelect');
    const templateTypeSelect = document.getElementById('templateTypeSelect');
    
    if (industrySelect) {
        industrySelect.addEventListener('change', function() {
            const selectedIndustry = this.value;
            console.log('Industry selected:', selectedIndustry);
            
            if (selectedIndustry) {
                // Filter templates by industry
                filterTemplatesByIndustry(selectedIndustry);
            }
        });
    }
    
    if (templateTypeSelect) {
        templateTypeSelect.addEventListener('change', function() {
            const selectedType = this.value;
            console.log('Template type selected:', selectedType);
            
            if (selectedType) {
                // Filter templates by type
                filterTemplatesByType(selectedType);
            }
        });
    }
}

/**
 * Initialize AI Generator functionality
 */
function initializeAIGenerator() {
    const aiGeneratorBtn = document.getElementById('aiGeneratorBtn');
    
    if (aiGeneratorBtn) {
        aiGeneratorBtn.addEventListener('click', function() {
            console.log('AI Generator clicked');
            showAIGeneratorModal();
        });
    }
}

/**
 * Show AI Generator Modal
 */
function showAIGeneratorModal() {
    // Create modal HTML
    const modalHTML = `
        <div class="modal fade" id="aiGeneratorModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">AI Template Generator</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="aiGeneratorForm">
                            <div class="mb-3">
                                <label for="aiPrompt" class="form-label">Describe your project needs:</label>
                                <textarea class="form-control" id="aiPrompt" rows="4" 
                                    placeholder="Example: Create a project charter for a software development project with 5 team members, 6-month timeline, and $100k budget"></textarea>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <label for="aiIndustry" class="form-label">Industry:</label>
                                    <select class="form-select" id="aiIndustry">
                                        <option value="">Select Industry</option>
                                        <option value="Technology">Technology</option>
                                        <option value="Healthcare">Healthcare</option>
                                        <option value="Construction">Construction</option>
                                        <option value="Finance">Finance</option>
                                        <option value="Manufacturing">Manufacturing</option>
                                        <option value="Education">Education</option>
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label for="aiProjectType" class="form-label">Project Type:</label>
                                    <select class="form-select" id="aiProjectType">
                                        <option value="">Select Project Type</option>
                                        <option value="Project Planning">Project Planning</option>
                                        <option value="Risk Management">Risk Management</option>
                                        <option value="Quality Assurance">Quality Assurance</option>
                                        <option value="Resource Management">Resource Management</option>
                                        <option value="Communication">Communication</option>
                                    </select>
                                </div>
                            </div>
                        </form>
                        <div id="aiResult" class="mt-3" style="display: none;">
                            <h6>Generated Template:</h6>
                            <div id="aiResultContent" class="border p-3 bg-light"></div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" id="generateTemplateBtn">Generate Template</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('aiGeneratorModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Initialize modal
    const modal = new bootstrap.Modal(document.getElementById('aiGeneratorModal'));
    modal.show();
    
    // Add generate button functionality
    document.getElementById('generateTemplateBtn').addEventListener('click', generateAITemplate);
}

/**
 * Generate AI Template
 */
async function generateAITemplate() {
    const prompt = document.getElementById('aiPrompt').value;
    const industry = document.getElementById('aiIndustry').value;
    const projectType = document.getElementById('aiProjectType').value;
    
    if (!prompt.trim()) {
        alert('Please describe your project needs');
        return;
    }
    
    const generateBtn = document.getElementById('generateTemplateBtn');
    const originalText = generateBtn.textContent;
    generateBtn.textContent = 'Generating...';
    generateBtn.disabled = true;
    
    try {
        const response = await fetch('/api/ai/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt,
                industry: industry,
                project_type: projectType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show result
            const resultDiv = document.getElementById('aiResult');
            const resultContent = document.getElementById('aiResultContent');
            
            resultContent.innerHTML = `
                <h6>${data.result.name}</h6>
                <p><strong>Description:</strong> ${data.result.description}</p>
                <p><strong>Sections:</strong></p>
                <ul>
                    ${data.result.sections.map(section => `<li>${section}</li>`).join('')}
                </ul>
                <p><strong>Content:</strong> ${data.result.content}</p>
                <button class="btn btn-success btn-sm" onclick="downloadGeneratedTemplate()">Download Template</button>
            `;
            
            resultDiv.style.display = 'block';
        } else {
            alert('Failed to generate template: ' + data.error);
        }
    } catch (error) {
        console.error('AI Generation error:', error);
        alert('Failed to generate template. Please try again.');
    } finally {
        generateBtn.textContent = originalText;
        generateBtn.disabled = false;
    }
}

/**
 * Filter templates by industry
 */
function filterTemplatesByIndustry(industry) {
    // Redirect to templates page with industry filter
    window.location.href = `/templates/?industry=${encodeURIComponent(industry)}`;
}

/**
 * Filter templates by type
 */
function filterTemplatesByType(type) {
    // Redirect to templates page with type filter
    window.location.href = `/templates/?category=${encodeURIComponent(type)}`;
}

/**
 * Initialize template filtering on templates page
 */
function initializeTemplateFiltering() {
    // Load popular templates if on homepage
    if (window.location.pathname === '/') {
        loadPopularTemplates();
        loadPlatformStats();
    }
    
    // Initialize search suggestions
    initializeSearchSuggestions();
}

/**
 * Initialize search suggestions functionality
 */
function initializeSearchSuggestions() {
    const searchInput = document.getElementById('search');
    if (!searchInput) return;
    
    let searchTimeout;
    
    // Add search container wrapper
    const searchContainer = document.createElement('div');
    searchContainer.className = 'search-container position-relative';
    searchInput.parentNode.insertBefore(searchContainer, searchInput);
    searchContainer.appendChild(searchInput);
    
    // Real-time search with debouncing
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const query = this.value.trim();
            if (query.length >= 2) {
                showSearchSuggestions(query);
            } else {
                hideSearchSuggestions();
            }
        }, 300);
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-container')) {
            hideSearchSuggestions();
        }
    });
}

/**
 * Show search suggestions
 */
async function showSearchSuggestions(query) {
    try {
        const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success && data.suggestions.length > 0) {
            displaySearchSuggestions(data.suggestions);
        } else {
            hideSearchSuggestions();
        }
    } catch (error) {
        console.error('Search suggestions error:', error);
        hideSearchSuggestions();
    }
}

/**
 * Display search suggestions
 */
function displaySearchSuggestions(suggestions) {
    let suggestionsContainer = document.getElementById('searchSuggestions');
    
    if (!suggestionsContainer) {
        suggestionsContainer = document.createElement('div');
        suggestionsContainer.id = 'searchSuggestions';
        suggestionsContainer.className = 'search-suggestions';
        document.querySelector('.search-container').appendChild(suggestionsContainer);
    }
    
    const suggestionsHTML = suggestions.map(suggestion => `
        <div class="suggestion-item" onclick="selectSuggestion('${suggestion.name}')">
            <div class="suggestion-name">${suggestion.name}</div>
            <div class="suggestion-meta">
                <span class="badge bg-light text-dark">${suggestion.industry}</span>
                <span class="badge bg-light text-dark">${suggestion.category}</span>
            </div>
        </div>
    `).join('');
    
    suggestionsContainer.innerHTML = suggestionsHTML;
    suggestionsContainer.style.display = 'block';
}

/**
 * Hide search suggestions
 */
function hideSearchSuggestions() {
    const suggestionsContainer = document.getElementById('searchSuggestions');
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
    }
}

/**
 * Select a search suggestion
 */
function selectSuggestion(name) {
    document.getElementById('search').value = name;
    hideSearchSuggestions();
    document.getElementById('filterForm').submit();
}

/**
 * Load popular templates
 */
async function loadPopularTemplates() {
    try {
        const response = await fetch('/api/templates/popular');
        const data = await response.json();
        
        if (data.success && data.popular_templates) {
            displayPopularTemplates(data.popular_templates);
        }
    } catch (error) {
        console.error('Failed to load popular templates:', error);
    }
}

/**
 * Load platform statistics
 */
async function loadPlatformStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success && data.stats) {
            updateStatsDisplay(data.stats);
        }
    } catch (error) {
        console.error('Failed to load platform stats:', error);
    }
}

/**
 * Display popular templates
 */
function displayPopularTemplates(templates) {
    const container = document.getElementById('popularTemplatesContainer');
    if (!container) return;
    
    const templatesHTML = templates.map(template => `
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <h6 class="card-title">${template.name}</h6>
                    <p class="card-text text-muted">${template.description}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">${template.industry}</small>
                        <span class="badge bg-primary">${template.downloads} downloads</span>
                    </div>
                </div>
                <div class="card-footer">
                    <button class="btn btn-primary btn-sm" onclick="downloadTemplate(${template.id})">
                        Download
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = templatesHTML;
}

/**
 * Update stats display
 */
function updateStatsDisplay(stats) {
    // Update template count
    const templateCountEl = document.querySelector('[data-stat="templates"]');
    if (templateCountEl) {
        templateCountEl.textContent = stats.total_templates + '+';
    }
    
    // Update other stats if elements exist
    const userCountEl = document.querySelector('[data-stat="users"]');
    if (userCountEl) {
        userCountEl.textContent = stats.total_users + '+';
    }
}

/**
 * Download template
 */
async function downloadTemplate(templateId) {
    try {
        window.location.href = `/templates/download/${templateId}`;
    } catch (error) {
        console.error('Download failed:', error);
        alert('Download failed. Please try again.');
    }
}

/**
 * Initialize all forms
 */
function initializeForms() {
    // Initialize login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Initialize registration form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegistration);
    }
}

/**
 * Handle login form submission
 */
async function handleLogin(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const email = formData.get('email');
    const password = formData.get('password');
    
    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            const data = await response.json();
            alert(data.error || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Login failed. Please try again.');
    }
}

/**
 * Handle registration form submission
 */
async function handleRegistration(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const email = formData.get('email');
    const password = formData.get('password');
    const name = formData.get('name');
    
    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password, name })
        });
        
        if (response.ok) {
            alert('Registration successful! Please log in.');
            window.location.href = '/auth/login';
        } else {
            const data = await response.json();
            alert(data.error || 'Registration failed');
        }
    } catch (error) {
        console.error('Registration error:', error);
        alert('Registration failed. Please try again.');
    }
}

/**
 * Download generated template
 */
async function downloadGeneratedTemplate() {
    try {
        // Get the generated template data from the page
        const templateName = document.querySelector('.generated-template h3')?.textContent || 'AI_Generated_Template';
        const description = document.querySelector('.generated-template p')?.textContent || '';
        
        // Show loading state
        const downloadBtn = document.querySelector('.download-template-btn');
        if (downloadBtn) {
            downloadBtn.disabled = true;
            downloadBtn.textContent = 'Generating...';
        }
        
        // Call the AI generation API to create the actual file
        const response = await fetch('/api/ai/download-generated', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                template_name: templateName,
                description: description,
                sections: Array.from(document.querySelectorAll('.generated-template li')).map(li => li.textContent)
            })
        });
        
        if (response.ok) {
            // Get the file blob
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${templateName.replace(/[^a-z0-9]/gi, '_')}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Reset button
            if (downloadBtn) {
                downloadBtn.disabled = false;
                downloadBtn.textContent = 'Download Template';
            }
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to generate template. Please try again.');
            
            // Reset button
            if (downloadBtn) {
                downloadBtn.disabled = false;
                downloadBtn.textContent = 'Download Template';
            }
        }
    } catch (error) {
        console.error('Download error:', error);
        alert('Failed to download template. Please try again.');
        
        // Reset button
        const downloadBtn = document.querySelector('.download-template-btn');
        if (downloadBtn) {
            downloadBtn.disabled = false;
            downloadBtn.textContent = 'Download Template';
        }
    }
}

/**
 * Interactive Demo Banner JavaScript
 * Handles step navigation and content switching
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get all step buttons
    const stepButtons = document.querySelectorAll('.demo-step-btn');
    const stepContents = document.querySelectorAll('.demo-step-content');
    
    // Add click event listeners to step buttons
    stepButtons.forEach(button => {
        button.addEventListener('click', function() {
            const stepNumber = this.getAttribute('data-step');
            switchToStep(stepNumber);
        });
    });
    
    /**
     * Switch to a specific step
     * @param {string} stepNumber - The step number to switch to
     */
    function switchToStep(stepNumber) {
        // Remove active class from all buttons
        stepButtons.forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Hide all step contents
        stepContents.forEach(content => {
            content.classList.remove('active');
        });
        
        // Add active class to clicked button
        const activeButton = document.querySelector(`.demo-step-btn[data-step="${stepNumber}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
        
        // Show corresponding step content
        const activeContent = document.getElementById(`demo-step-${stepNumber}`);
        if (activeContent) {
            activeContent.classList.add('active');
        }
    }
    
    // Optional: Auto-cycle through steps (disabled by default to avoid animations)
    // Uncomment below to enable auto-cycling every 5 seconds
    /*
    let currentStep = 1;
    const totalSteps = 3;
    
    setInterval(() => {
        currentStep = (currentStep % totalSteps) + 1;
        switchToStep(currentStep.toString());
    }, 5000);
    */
});


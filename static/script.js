// --- START OF FILE script.js ---

// static/script.js
document.addEventListener('DOMContentLoaded', (event) => {
    const form = document.getElementById('qa-form');
    const submitButton = document.getElementById('submit-button');
    const loadingIndicator = document.getElementById('loading');
    const questionInput = form.querySelector('input[name="question"]');
    const fileInput = form.querySelector('input[name="pdf_file"]');

    if (form) {
        form.addEventListener('submit', function() {
            // Show loading indicator if EITHER a question is asked OR a file is selected
            const questionValue = questionInput ? questionInput.value.trim() : '';
            const fileSelected = fileInput && fileInput.files.length > 0;

            if (questionValue !== '' || fileSelected) {
                if (loadingIndicator) {
                    loadingIndicator.style.display = 'block';
                }
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.textContent = '処理中...'; // More general text
                }
            }
            // Form submission continues naturally.
        });
    }
});
// --- END OF FILE script.js ---
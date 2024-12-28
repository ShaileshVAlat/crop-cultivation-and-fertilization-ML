// static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    // Autofocus the first input field in the form
    const firstInput = document.querySelector('input[type="number"]');
    if (firstInput) {
        firstInput.focus();
    }

    // Add dynamic effects for input fields
    const inputs = document.querySelectorAll('input[type="number"]');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.querySelector('i').style.color = '#18bc9c';
        });

        input.addEventListener('blur', () => {
            input.parentElement.querySelector('i').style.color = '#95a5a6';
        });
    });
});

// Registration form client-side validation
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form[action="/register"]');

    if (form) {
        form.addEventListener('submit', function(e) {
            const name = form.querySelector('input[name="name"]').value.trim();
            const email = form.querySelector('input[name="email"]').value.trim();
            const password = form.querySelector('input[name="password"]').value;
            const passwordConfirm = form.querySelector('input[name="password_confirm"]').value;

            let errors = [];

            // Validate name
            if (!name) {
                errors.push('Name is required.');
            }

            // Validate email format
            if (!email) {
                errors.push('Email is required.');
            } else if (!isValidEmail(email)) {
                errors.push('Invalid email format.');
            }

            // Validate password
            if (!password) {
                errors.push('Password is required.');
            } else if (password.length < 6) {
                errors.push('Password must be at least 6 characters.');
            }

            // Validate password confirmation
            if (!passwordConfirm) {
                errors.push('Password confirmation is required.');
            } else if (password !== passwordConfirm) {
                errors.push('Passwords do not match.');
            }

            // If there are errors, prevent form submission and show alert
            if (errors.length > 0) {
                e.preventDefault();
                alert(errors.join('\n'));
            }
        });
    }
});

/**
 * Basic email validation using a simple regex pattern.
 * @param {string} email - The email to validate
 * @returns {boolean} - True if email is valid, false otherwise
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

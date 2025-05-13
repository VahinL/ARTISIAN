document.addEventListener('DOMContentLoaded', function() {
    // Password visibility toggler
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            }
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('.auth-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const password1 = this.querySelector('[name="password1"]');
            const password2 = this.querySelector('[name="password2"]');
            
            if (password1 && password2 && password1.value !== password2.value) {
                e.preventDefault();
                alert('Passwords do not match!');
            }
        });
    });
});
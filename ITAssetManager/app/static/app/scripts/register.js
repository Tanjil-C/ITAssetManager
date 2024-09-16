// register.js

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registerForm');
    form.addEventListener('submit', async function (event) {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        try {
            const response = await fetch('/register/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                window.location.href = '/'; // Redirect on successful registration
            } else {
                displayErrors(result.errors); // Display errors
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
});

function displayErrors(errors) {
    const errorDiv = document.getElementById('formErrors');
    errorDiv.innerHTML = ''; // Clear previous errors

    if (errors) {
        for (const [field, errorList] of Object.entries(errors)) {
            errorList.forEach(error => {
                const errorItem = document.createElement('div');
                if (field === '__all__') {
                    errorItem.textContent = error.message; // Handle non-field errors
                } else {
                    const inputField = document.querySelector(`#${field}`);
                    if (inputField) {
                        errorItem.textContent = `${inputField.previousElementSibling.textContent} ${error.message}`;
                    }
                }
                errorDiv.appendChild(errorItem);
            });
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registerForm');
    const successModal = document.getElementById('successModal');
    const closeModalButton = document.getElementById('closeModal');

    // Handle form submission
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
                // Show success pop-up
                successModal.style.display = 'block';

                // Redirect after 3 seconds
                setTimeout(function () {
                    window.location.href = '/login';
                }, 6000);
            } else {
                displayErrors(result.errors); // Display errors
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Close the modal manually if the user clicks on the close button
    closeModalButton.addEventListener('click', function () {
        successModal.style.display = 'none';
    });
});

// Function to display form errors
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

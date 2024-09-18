document.addEventListener('DOMContentLoaded', function () {
    // Get the Django messages from the data attribute
    const messagesElement = document.getElementById('django-messages');
    if (messagesElement) {
        const messages = JSON.parse(messagesElement.getAttribute('data-messages'));

        // Loop through each message and display it using SweetAlert 
        messages.forEach(message => {
            Swal.fire({
                icon: message.tags.includes('error') ? 'error' : 'success',
                text: message.text
            });
        });
    }
});

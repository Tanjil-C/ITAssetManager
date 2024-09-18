document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed');
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

    const toggleButton = document.getElementById('navbar-toggle');
    const menu = document.getElementById('navbar-menu');

    toggleButton.addEventListener('click', function () {
        menu.classList.toggle('active');
        console.log(menu);
    });
});

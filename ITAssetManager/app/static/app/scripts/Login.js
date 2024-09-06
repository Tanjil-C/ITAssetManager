document.getElementById('login-btn').addEventListener('click', function (event) {
    event.preventDefault();  // Prevent the default form submission behavior

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/api/token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.access) {
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                document.getElementById('login-message').innerText = 'Login successful!';
                console.log("data.access ===", localStorage.getItem('access_token'))
                console.log("data.refresh ===", localStorage.getItem('refresh_token'))
                // Redirect to the home page after 2 seconds
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
            } else {
                document.getElementById('login-message').innerText = 'Invalid credentials';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('login-message').innerText = 'An error occurred';
        });
});

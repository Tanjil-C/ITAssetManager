// Check local storage for JWT on page load
if (localStorage.getItem('access_token') === null) {
    window.location.href = '/login/';
}

// Check local storage for JWT every 5 minutes
setInterval(function() {
  if (localStorage.getItem('access_token') === null) {
      window.location.href = '/login/';
  }
}, 300000); // 5 minutes in milliseconds
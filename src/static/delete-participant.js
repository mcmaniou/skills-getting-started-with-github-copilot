<script>
  document.addEventListener('click', function(event) {
    if (event.target.classList.contains('delete-btn')) {
      const email = event.target.getAttribute('data-email');
      // Call API to unregister participant
      fetch(`/unregister?email=${encodeURIComponent(email)}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Remove participant from the list
            event.target.closest('li').remove();
          } else {
            alert('Failed to unregister participant.');
          }
        });
    }
  });
</script>
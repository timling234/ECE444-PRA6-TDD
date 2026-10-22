for (const form of document.querySelectorAll('.delete-entry')) {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = form.querySelector('button');
    button.disabled = true;
    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: {Accept: 'application/json'},
        credentials: 'same-origin'
      });
      const result = await response.json();
      if (!response.ok || result.status !== 1) {
        throw new Error(result.message || 'Could not delete the post.');
      }
      location.reload();
    } catch (error) {
      alert(error.message || 'Could not delete the post. Please try again.');
      button.disabled = false;
    }
  });
}

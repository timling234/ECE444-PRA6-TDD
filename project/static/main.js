for (const entry of document.querySelectorAll('.entry')) {
  entry.addEventListener('click', async () => {
    const id = entry.querySelector('h2').id;
    try {
      const response = await fetch(`/delete/${id}`);
      const result = await response.json();
      if (response.ok && result.status === 1) entry.remove();
      else alert(result.message);
      location.reload();
    } catch (error) { console.error(error); }
  });
}

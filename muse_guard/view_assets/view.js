for (const button of document.querySelectorAll('[data-winner]')) {
  button.addEventListener('click', async () => {
    const status = document.getElementById('decision-status');
    for (const choice of document.querySelectorAll('[data-winner]')) choice.disabled = true;
    status.textContent = 'Submitting your decision. Muse will repair, then independent checks will run…';
    try {
      const response = await fetch('/decision', {
        method: 'POST', headers: {'Content-Type': 'application/json', 'X-Decision-Token': document.body.dataset.decisionToken},
        body: JSON.stringify({winner: button.dataset.winner})
      });
      if (!response.ok) throw new Error('Decision refused. Reload to inspect the current record.');
      window.location.reload();
    } catch (error) { status.textContent = error.message; }
  });
}

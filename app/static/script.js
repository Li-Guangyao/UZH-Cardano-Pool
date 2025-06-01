let currentPage = 1;

function loadPools(page = 1) {
  fetch(`/api/pools?page=${page}&count=10`)
    .then(response => response.json())
    .then(data => {
      const output = document.getElementById('pool-list');
      if (!data.pools || data.pools.length === 0) {
        output.textContent = 'No data found';
        return;
      }

      output.innerHTML = data.pools.map(pool => `
        <pre>${JSON.stringify(pool, null, 2)}</pre>
        <hr/>
      `).join('');
    });
}

document.getElementById('prev').addEventListener('click', () => {
  if (currentPage > 1) {
    currentPage--;
    loadPools(currentPage);
  }
});

document.getElementById('next').addEventListener('click', () => {
  currentPage++;
  loadPools(currentPage);
});

loadPools(currentPage);

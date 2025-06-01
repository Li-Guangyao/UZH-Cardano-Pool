let currentPage = 1;
let isCurrentPageValid = true;

function loadPools(page = 1) {
  fetch(`/api/pools?page=${page}&count=20`)
    .then(response => response.json())
    .then(data => {
      const output = document.getElementById('pool-list');
      if (!data.pools || data.pools.length === 0) {
        output.textContent = 'No data found';
        isCurrentPageValid = false;
        return;
      }

      isCurrentPageValid = data.pools.length> 0;

      output.innerHTML = `
        <table style="border-collapse: collapse; width: 100%;">
          <thead>
        <tr style="background-color:rgb(246, 246, 246);">
          <th style="border: 1px solid #ddd; padding: 8px;">Pool ID</th>
          <th style="border: 1px solid #ddd; padding: 8px;">Margin Cost</th>
          <th style="border: 1px solid #ddd; padding: 8px;">Fixed Cost</th>
          <th style="border: 1px solid #ddd; padding: 8px;">Declared Pledge</th>
          <th style="border: 1px solid #ddd; padding: 8px;">Live Delegators</th>
          <th style="border: 1px solid #ddd; padding: 8px;">Live Size</th>
          <th style="border: 1px solid #ddd; padding: 8px;">Live Stake</th>
        </tr>
          </thead>
          <tbody>
        ${data.pools.map(pool => `
          <tr>
            <td style="border: 1px solid #ddd; padding: 8px;">${pool.pool_id}</td>
            <td style="border: 1px solid #ddd; padding: 8px;">${pool.margin_cost}</td>
            <td style="border: 1px solid #ddd; padding: 8px;">${pool.fixed_cost}</td>
            <td style="border: 1px solid #ddd; padding: 8px;">${pool.declared_pledge}</td>
            <td style="border: 1px solid #ddd; padding: 8px;">${pool.live_delegators}</td>
            <td style="border: 1px solid #ddd; padding: 8px;">${pool.live_size}</td>
            <td style="border: 1px solid #ddd; padding: 8px;">${pool.live_stake}</td>
          </tr>
        `).join('')}
          </tbody>
        </table>
      `;

    }).catch(err => {
      console.err("Fetch error:", err)
    });
}

document.getElementById('prev').addEventListener('click', () => {
  if (currentPage > 1) {
    currentPage--;
    loadPools(currentPage);
  }
});

document.getElementById('next').addEventListener('click', () => {
  if (!isCurrentPageValid) {
    console.warn("No more data, cannot go to next page.");
    return;
  }
  currentPage++;
  loadPools(currentPage);
});

loadPools(currentPage);
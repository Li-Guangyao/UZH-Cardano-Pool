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

      isCurrentPageValid = data.pools.length > 0;

      // Show the epoch of the first pool at the top center
      let epochInfo = '';
      if (data.pools && data.pools.length > 0 && data.pools[0].reward_latest && typeof data.pools[0].reward_latest.epoch !== 'undefined') {
        epochInfo = `
          <div style="text-align: center; font-size: 1.3em; font-weight: 500; margin-bottom: 18px;">
        Current Epoch: ${data.pools[0].reward_latest.epoch +1 }
          </div>
        `;
      }

      output.innerHTML = `
        ${epochInfo}
        <div style="display: flex; flex-direction: column; gap: 24px; align-items: center;">
          ${data.pools.map(pool => `
        <div style="
          width: 95%;
          background: #fff;
          border-radius: 18px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.08);
          padding: 24px 28px;
          box-sizing: border-box;
          display: flex;
          flex-direction: column;
          gap: 12px;
        ">
          <!-- 1st line -->
          <div style="display: flex; align-items: center; gap: 18px; font-size: 1.1em; font-weight: bold;">
            <span style="color: #333;">${pool.pool_id}</span>
            <span style="color: #888; margin-left: 30px;">${pool.metadata_name? pool.metadata_name: ''}</span>
          </div>
          <!-- 2nd line-->
          <div style="display: flex; flex-wrap: wrap; gap: 18px; color: #444; font-size: 0.98em;">
            <span>Margin Cost: <b>${pool.margin_cost}</b></span>
            <span>Fixed Cost: <b>${formatNumber(pool.fixed_cost / 1e6)} UZH ₳</b></span>
            <span>Declared Pledge: <b>${formatNumber(pool.declared_pledge / 1e6)} UZH ₳</b></span>
            <span>Live Delegators: <b>${pool.live_delegators}</b></span>
            <span>Live Size: <b>${formatNumber(pool.live_size, 6)}</b></span>
            <span>Live Stake: <b>${formatNumber(pool.live_stake / 1e6)} UZH ₳</b></span>
            <span>Reward: <b> ${formatNumber(pool.reward_latest.rewards / 1e6)} UZH ₳</b></span>
          </div>
          <!-- 3rd line -->
          <div style="display: flex; flex-wrap: wrap; gap: 18px; color: #666; font-size: 0.95em;">
            <span>Description: ${pool.metadata_description || ''}</span>
            <span>Ticker: ${pool.metadata_ticker || ''}</span>
            <span>
          Homepage: 
          ${pool.metadata_homepage ? `<a href="${pool.metadata_homepage}" target="_blank" style="color:#1976d2;text-decoration:underline;">${pool.metadata_homepage}</a>` : ''}
            </span>
          </div>
        </div>
          `).join('')}
        </div>
      `;

      function formatNumber(value, decimalPlaces = 2) {
        const parts = value.toFixed(decimalPlaces).split('.');
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, "'");
        return parts.join('.');
      }

    }).catch(err => {
      console.error("Fetch error:", err)
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
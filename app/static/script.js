let currentPage = 1;
let isCurrentPageValid = true;

function loadPools(page = 1) {
  fetch(`/api/pools?page=${page}&count=100`)
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
      if (data.pools && data.current_epoch) {
        const epochData = data.current_epoch;
        const totalPools = data.total_pools;
        const totalDelegators = data.total_delegators;
        const totalStakes = data.total_stakes;

        epochInfo = `
          <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 24px;
        border: 2px solid #0028A5;
        border-radius: 14px;
        padding: 14px 0 14px 0;
        margin-top: 18px;
        margin-bottom: 18px;
        font-size: 1.08em;
        background: #f8faff;
        width: 95%;
        margin-left: auto;
        margin-right: auto;
          ">
        ${epochData.epoch !== undefined ? `<span><b>Current Epoch:</b> ${epochData.epoch}</span>` : ''}
        ${epochData.block_count !== undefined ? `<span><b>Blocks:</b> ${epochData.block_count}</span>` : ''}
        ${epochData.tx_count !== undefined ? `<span><b>Transactions:</b> ${epochData.tx_count}</span>` : ''}
        ${totalPools !== undefined ? `<span><b>Total Pools:</b> ${totalPools}</span>` : ''}
        ${totalDelegators !== undefined ? `<span><b>Total Delegators:</b> ${totalDelegators}</span>` : ''}
        ${totalStakes !== undefined ? `<span><b>Total Stakes:</b> ${formatNumber(totalStakes / 1e6)} UZH ₳</span>` : ''}
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
        ${pool.metadata_name ? `<span style="color: #888; margin-left: 30px;">${pool.metadata_name}</span>` : ''}
          </div>
          <!-- 2nd line-->
          <div style="display: flex; flex-wrap: wrap; gap: 18px; color: #444; font-size: 0.98em;">
        ${pool.margin_cost !== undefined ? `<span>Margin Cost: <b>${pool.margin_cost}</b></span>` : ''}
        ${pool.fixed_cost !== undefined ? `<span>Fixed Cost: <b>${formatNumber(pool.fixed_cost / 1e6)} UZH ₳</b></span>` : ''}
        ${pool.declared_pledge !== undefined ? `<span>Declared Pledge: <b>${formatNumber(pool.declared_pledge / 1e6)} UZH ₳</b></span>` : ''}
        ${pool.live_delegators !== undefined ? `<span>Live Delegators: <b>${pool.live_delegators}</b></span>` : ''}
        ${pool.live_size !== undefined ? `<span>Live Size: <b>${formatNumber(pool.live_size, 6)}</b></span>` : ''}
        ${pool.live_stake !== undefined ? `<span>Live Stake: <b>${formatNumber(pool.live_stake / 1e6)} UZH ₳</b></span>` : ''}
        ${pool.reward_latest && pool.reward_latest.rewards !== undefined ? `<span>Reward: <b> ${formatNumber(pool.reward_latest.rewards / 1e6)} UZH ₳</b></span>` : ''}
          </div>
          <!-- 3rd line -->
          <div style="display: flex; flex-wrap: wrap; gap: 18px; color: #666; font-size: 0.95em;">
        ${pool.metadata_description ? `<span>Description: ${pool.metadata_description}</span>` : ''}
        ${pool.metadata_ticker ? `<span>Ticker: ${pool.metadata_ticker}</span>` : ''}
        ${pool.metadata_homepage ? `<span>Homepage: <a href="${pool.metadata_homepage}" target="_blank" style="color:#1976d2;text-decoration:underline;">${pool.metadata_homepage}</a></span>` : ''}
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
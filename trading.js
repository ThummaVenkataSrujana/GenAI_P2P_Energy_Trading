// P2P Energy Trading Interactive Logic
document.addEventListener('DOMContentLoaded', function() {
  const sellerSelect = document.getElementById('sellerSelect');
  const quantityInput = document.getElementById('quantityInput');
  const quantitySlider = document.getElementById('quantitySlider');
  const priceDisplay = document.getElementById('priceDisplay');
  const totalDisplay = document.getElementById('totalDisplay');
  const maxAvailableDisplay = document.getElementById('maxAvailableDisplay');
  const carbonOffsetDisplay = document.getElementById('carbonOffsetDisplay');
  const confirmBtn = document.getElementById('confirmPurchaseBtn');
  const tradeForm = document.getElementById('tradeForm');
  const successModal = document.getElementById('successModal');
  const modalCloseBtn = document.getElementById('modalCloseBtn');

  if (!sellerSelect || !quantityInput) return;

  function updateCalculations() {
    const selectedOption = sellerSelect.options[sellerSelect.selectedIndex];
    if (!selectedOption || !selectedOption.value) return;

    const price = parseFloat(selectedOption.dataset.price || 10);
    const available = parseFloat(selectedOption.dataset.available || 0);

    maxAvailableDisplay.textContent = `${available} kWh`;
    priceDisplay.textContent = `₹${price.toFixed(2)}/kWh`;

    // Cap quantity to available
    let qty = parseFloat(quantityInput.value) || 1;
    if (qty > available) {
      qty = available;
      quantityInput.value = qty;
    }
    if (qty < 1) {
      qty = 1;
      quantityInput.value = qty;
    }
    
    if (quantitySlider) {
      quantitySlider.max = available;
      quantitySlider.value = qty;
    }

    const total = qty * price;
    totalDisplay.textContent = `₹${total.toFixed(2)}`;

    // Calculate CO2 offset (0.85 kg per solar kWh)
    const offset = (qty * 0.85).toFixed(2);
    if (carbonOffsetDisplay) {
      carbonOffsetDisplay.textContent = `${offset} kg CO₂`;
    }
  }

  sellerSelect.addEventListener('change', updateCalculations);
  quantityInput.addEventListener('input', updateCalculations);
  if (quantitySlider) {
    quantitySlider.addEventListener('input', function() {
      quantityInput.value = this.value;
      updateCalculations();
    });
  }

  // Initial calculation
  updateCalculations();

  // Submit Purchase API Call
  if (tradeForm) {
    tradeForm.addEventListener('submit', async function(e) {
      e.preventDefault();

      const seller = sellerSelect.value;
      const quantity = parseFloat(quantityInput.value);

      if (!seller || quantity <= 0) {
        alert('Please select a valid seller and quantity.');
        return;
      }

      confirmBtn.disabled = true;
      confirmBtn.innerHTML = 'Processing Trade...';

      try {
        const response = await fetch('/api/buy', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ seller, quantity })
        });

        const resData = await response.json();

        if (resData.success) {
          // Update Modal Details
          document.getElementById('modalTxnId').textContent = resData.transaction.id;
          document.getElementById('modalSeller').textContent = resData.transaction.seller;
          document.getElementById('modalEnergy').textContent = `${resData.transaction.energy} kWh`;
          document.getElementById('modalTotal').textContent = `₹${resData.transaction.total}`;

          // Show Modal
          if (successModal) {
            successModal.classList.add('active');
          }

          // Update header wallet if present
          const headerWallet = document.querySelector('.wallet-badge strong');
          if (headerWallet) {
            headerWallet.textContent = `₹${resData.newWalletBalance.toFixed(2)}`;
          }

          // Refresh calculations
          updateCalculations();
        } else {
          alert(`Trade Failed: ${resData.message}`);
        }
      } catch (err) {
        console.error(err);
        alert('An error occurred while processing transaction.');
      } finally {
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = `
          <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" fill="none" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
          Confirm P2P Energy Purchase
        `;
      }
    });
  }

  if (modalCloseBtn && successModal) {
    modalCloseBtn.addEventListener('click', function() {
      successModal.classList.remove('active');
      window.location.reload();
    });
  }
});

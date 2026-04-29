// Cart functions
function addToCart(productId, quantity) {
    fetch('/cart/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({product_id: productId, quantity: quantity})
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            updateCartBadge();
            showToast('Added to cart!');
        }
    });
}

function updateCartBadge() {
    fetch('/cart/count')
    .then(r => r.json())
    .then(data => {
        const badge = document.getElementById('cart-badge');
        if (badge) {
            badge.textContent = data.count;
            badge.style.display = data.count > 0 ? 'inline' : 'none';
        }
    });
}

function removeFromCart(productId) {
    fetch('/cart/remove', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({product_id: productId})
    })
    .then(r => r.json())
    .then(data => { if (data.success) location.reload(); });
}

function updateQuantity(productId, qty) {
    fetch('/cart/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({product_id: productId, quantity: parseInt(qty)})
    })
    .then(r => r.json())
    .then(data => { if (data.success) location.reload(); });
}

// Invoice builder
function addInvoiceRow() {
    const tbody = document.getElementById('invoice-items');
    const row = document.createElement('tr');
    row.innerHTML = `
        <td><input type="text" name="item_description[]" class="form-control form-control-sm" required></td>
        <td><input type="number" name="item_quantity[]" class="form-control form-control-sm" min="1" value="1" oninput="calculateTotals()"></td>
        <td><input type="number" name="item_unit_price[]" class="form-control form-control-sm" min="0" step="0.01" value="0" oninput="calculateTotals()"></td>
        <td class="item-subtotal">0.00</td>
        <td><button type="button" class="btn btn-sm btn-danger" onclick="removeRow(this)"><i class="bi bi-trash"></i></button></td>
    `;
    tbody.appendChild(row);
    calculateTotals();
}

function removeRow(btn) {
    btn.closest('tr').remove();
    calculateTotals();
}

function calculateTotals() {
    const rows = document.querySelectorAll('#invoice-items tr');
    let subtotal = 0;
    rows.forEach(row => {
        const qty = parseFloat(row.querySelector('[name="item_quantity[]"]')?.value || 0);
        const price = parseFloat(row.querySelector('[name="item_unit_price[]"]')?.value || 0);
        const sub = qty * price;
        const cell = row.querySelector('.item-subtotal');
        if (cell) cell.textContent = sub.toFixed(2);
        subtotal += sub;
    });
    const taxRate = parseFloat(document.getElementById('tax-rate')?.value || 12) / 100;
    const tax = subtotal * taxRate;
    const total = subtotal + tax;
    const el = (id, val) => { const e = document.getElementById(id); if(e) e.textContent = val.toFixed(2); };
    el('inv-subtotal', subtotal);
    el('inv-tax', tax);
    el('inv-total', total);
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'position-fixed bottom-0 end-0 p-3';
    toast.style.zIndex = '11';
    toast.innerHTML = `<div class="toast show align-items-center text-white bg-success border-0" role="alert">
        <div class="d-flex"><div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" onclick="this.closest('.position-fixed').remove()"></button></div></div>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

document.addEventListener('DOMContentLoaded', function() {
    updateCartBadge();
});

const API_BASE = window.location.origin;

// === 1. PRODUKTE LADEN & RENDERN ===
async function loadProducts() {
  const container = document.getElementById('products-list');
  if (!container) return;

  try {
    const res = await fetch(`${API_BASE}/products/`);
    if (!res.ok) throw new Error('API nicht erreichbar');
    const products = await res.json();

    container.innerHTML = products.map(p => `
      <article class="product-card">
        <img src="${p.image_url || '/static/images/baskets_001.png'}" alt="${p.name}">
        <div class="content">
          <h3>${p.name}</h3>
          <p>${p.description.substring(0, 100)}...</p>
          <p class="price">€${p.price.toFixed(2)}</p>
          <div class="card-actions">
            <a href="/shop/product?id=${p.id}" class="btn-secondary">Details</a>
            <button class="btn-primary add-to-cart-btn" data-product-id="${p.id}">🛒 In den Warenkorb</button>
          </div>
        </div>
      </article>
    `).join('');
  } catch (err) {
    container.innerHTML = `<p class="small-note">Produkte konnten nicht geladen werden.</p>`;
    console.error(err);
  }
}

// === 2. WARENKORB-MANAGER ===
class CartManager {
  constructor() {
    this.apiBase = API_BASE;
    this.userId = this._resolveUserId();
    this.cart = null;
  }

  _resolveUserId() {
    // Fallback auf Demo-User (ID 2 aus init.py), falls nicht eingeloggt
    return localStorage.getItem('access_token') 
      ? JSON.parse(atob(localStorage.getItem('access_token').split('.')[1])).user_id 
      : (localStorage.getItem('demo_user_id') || 2);
  }

  async loadCart() {
    try {
      const res = await fetch(`${this.apiBase}/cart/${this.userId}`);
      this.cart = res.ok ? await res.json() : { items: [] };
      return this.cart;
    } catch { return { items: [] }; }
  }

  async addToCart(productId, qty = 1) {
    const res = await fetch(`${this.apiBase}/cart/${this.userId}/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: parseInt(productId), quantity: qty })
    });
    if (!res.ok) throw new Error('Fehler beim Hinzufügen');
    await this.loadCart();
    this.updateUI();
    this.toast('✅ Zum Warenkorb hinzugefügt', 'success');
  }

  async changeQty(itemId, delta) {
    const item = this.cart.items.find(i => i.id == itemId);
    if (!item) return;
    const newQty = item.quantity + delta;
    if (newQty <= 0) return this.removeItem(itemId);

    const res = await fetch(`${this.apiBase}/cart/${this.userId}/items/${itemId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: 0, quantity: newQty })
    });
    if (!res.ok) throw new Error('Fehler beim Aktualisieren');
    await this.loadCart();
    this.updateUI();
  }

  async removeItem(itemId) {
    const res = await fetch(`${this.apiBase}/cart/${this.userId}/items/${itemId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Fehler beim Entfernen');
    await this.loadCart();
    this.updateUI();
    this.toast('🗑️ Artikel entfernt', 'info');
  }

  updateUI() {
    this.renderCartItems();
    this.calculateTotals();
    this.updateBadge();
  }

  renderCartItems() {
    const container = document.getElementById('cart-items');
    if (!container) return;

    if (!this.cart.items?.length) {
      container.innerHTML = `<p class="empty-cart">🛒 Dein Warenkorb ist leer.<br><a href="/shop/products" class="btn-secondary">Weiter einkaufen</a></p>`;
      return;
    }

    container.innerHTML = this.cart.items.map(item => `
      <div class="cart-item" data-item-id="${item.id}">
        <img src="${item.product.image_url || '/static/images/baskets_001.png'}" alt="${item.product.name}" class="cart-item-image">
        <div class="cart-item-details">
          <h4>${item.product.name}</h4>
          <p class="price">€${item.product.price.toFixed(2)}</p>
          <div class="quantity-controls">
            <button class="qty-btn minus" data-item-id="${item.id}">−</button>
            <span class="qty-value">${item.quantity}</span>
            <button class="qty-btn plus" data-item-id="${item.id}">+</button>
          </div>
        </div>
        <button class="remove-btn" data-item-id="${item.id}" title="Entfernen">✕</button>
      </div>
    `).join('');

    // Listener binden
    container.querySelectorAll('.qty-btn.minus').forEach(b => b.onclick = () => this.changeQty(b.dataset.itemId, -1));
    container.querySelectorAll('.qty-btn.plus').forEach(b => b.onclick = () => this.changeQty(b.dataset.itemId, 1));
    container.querySelectorAll('.remove-btn').forEach(b => b.onclick = () => this.removeItem(b.dataset.itemId));
  }

  calculateTotals() {
    const subtotalEl = document.querySelector('.summary-panel .subtotal');
    const totalEl = document.querySelector('.summary-panel .total');
    const shippingEl = document.querySelector('.summary-panel .shipping');
    if (!subtotalEl || !this.cart.items?.length) return;

    const subtotal = this.cart.items.reduce((sum, i) => sum + i.product.price * i.quantity, 0);
    const shipping = subtotal >= 50 ? 0 : 4.99;
    const total = subtotal + shipping;

    subtotalEl.textContent = `€${subtotal.toFixed(2)}`;
    totalEl.textContent = `€${total.toFixed(2)}`;
    shippingEl.textContent = shipping === 0 ? 'Kostenlos 🎉' : `€${shipping.toFixed(2)}`;
  }

  updateBadge() {
    const badge = document.querySelector('.cart-icon .badge');
    if (!badge) return;
    const count = this.cart.items?.reduce((sum, i) => sum + i.quantity, 0) || 0;
    badge.textContent = count;
    badge.style.display = count > 0 ? 'flex' : 'none';
  }

  toast(msg, type = 'info') {
    const t = document.createElement('div');
    t.textContent = msg;
    t.style.cssText = `position:fixed;bottom:2rem;right:2rem;background:${type==='success'?'#4caf50':type==='error'?'#f44336':'#2196f3'};color:#fff;padding:1rem 1.5rem;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.15);z-index:1000;font-family:var(--font-body);animation:slideIn 0.3s ease;`;
    document.body.appendChild(t);
    setTimeout(() => { t.style.animation = 'slideOut 0.3s ease'; setTimeout(() => t.remove(), 300); }, 2500);
  }
}

const cart = new CartManager();

// === 3. INITIALISIERUNG ===
document.addEventListener('DOMContentLoaded', async () => {
  // Produkte laden
  if (document.getElementById('products-list')) loadProducts();

  // Warenkorb-Seite initialisieren
  if (document.getElementById('cart-items')) {
    await cart.loadCart();
    cart.updateUI();
  }

  // "In den Warenkorb"-Buttons (delegiert)
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.add-to-cart-btn');
    if (!btn) return;
    e.preventDefault();
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = '⏳ Hinzufügen...';
    try { await cart.addToCart(btn.dataset.productId); } 
    finally { btn.disabled = false; btn.textContent = originalText; }
  });

  // Checkout-Button
  const checkout = document.getElementById('checkout');
  if (checkout) {
    checkout.onclick = () => {
      if (!cart.cart.items?.length) return cart.toast('⚠️ Warenkorb ist leer', 'warning');
      cart.toast('🚀 Weiter zur Kasse...', 'success');
      // Später: window.location.href = '/shop/checkout';
    };
  }

  // Badge beim Laden setzen
  await cart.loadCart();
  cart.updateBadge();
});
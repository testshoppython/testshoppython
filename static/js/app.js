const API_BASE = window.location.origin;

// === 1. AUTHENTICIERUNGS-MANAGER ===
class AuthManager {
  constructor() {
    this.apiBase = API_BASE;
    this.user = this._loadUser();
  }

  _loadUser() {
    const token = localStorage.getItem('access_token');
    if (!token) return null;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload; 
    } catch (e) {
      this.logout();
      return null;
    }
  }

  isLoggedIn() { return !!this.user; }
  getUserId() { return this.user ? this.user.user_id : (localStorage.getItem('demo_user_id') || 2); }

  async login(username, password) {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    const res = await fetch(`${this.apiBase}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params
    });
    if (!res.ok) throw new Error('Login fehlgeschlagen');
    const data = await res.json();
    localStorage.setItem('access_token', data.access_token);
    this.user = this._loadUser();
    return data;
  }

  async register(userData) {
    const res = await fetch(`${this.apiBase}/users/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    if (!res.ok) throw new Error('Registrierung fehlgeschlagen');
    return await res.json();
  }

  logout() {
    localStorage.removeItem('access_token');
    this.user = null;
    window.location.href = '/';
  }

  updateUI() {
    const loginLinks = document.querySelectorAll('.auth-link');
    const accountButtons = document.querySelectorAll('.btn-ghost[title="Mein Konto"], .top-bar a[href="/shop/login"]');
    const userOnly = document.querySelectorAll('.user-only');
    const adminOnly = document.querySelectorAll('.admin-only');
    
    if (this.isLoggedIn()) {
      userOnly.forEach(el => el.style.display = 'block');
      if (this.user.is_admin) adminOnly.forEach(el => el.style.display = 'block');
      
      loginLinks.forEach(link => { 
        link.textContent = 'Logout'; 
        link.onclick = (e) => { e.preventDefault(); this.logout(); }; 
      });
      
      accountButtons.forEach(btn => {
        if (btn.tagName === 'A') { 
          btn.textContent = `Logout (${this.user.username})`; 
          btn.onclick = (e) => { e.preventDefault(); this.logout(); }; 
        } else { 
          btn.innerHTML = `👤 <span style="font-size:0.75rem; font-weight:600; vertical-align:middle;">${this.user.username}</span>`; 
        }
      });
    } else {
      userOnly.forEach(el => el.style.display = 'none');
      adminOnly.forEach(el => el.style.display = 'none');
    }
  }

  toast(msg, type = 'info') {
    const t = document.createElement('div');
    t.textContent = msg;
    t.style.cssText = `position:fixed;bottom:2rem;right:2rem;background:${type==='success'?'#4caf50':type==='error'?'#f44336':'#2196f3'};color:#fff;padding:1rem 1.5rem;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.15);z-index:1000;font-family:var(--font-body);animation:slideIn 0.3s ease;`;
    document.body.appendChild(t);
    setTimeout(() => { t.style.animation = 'slideOut 0.3s ease'; setTimeout(() => t.remove(), 300); }, 2500);
  }
}

const auth = new AuthManager();

// === 2. WARENKORB-MANAGER ===
class CartManager {
  constructor() {
    this.apiBase = API_BASE;
    this.userId = auth.getUserId();
    this.cart = null;
  }

  async loadCart() {
    this.userId = auth.getUserId();
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
    auth.toast('✅ Zum Warenkorb hinzugefügt', 'success');
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
    if (res.ok) { await this.loadCart(); this.updateUI(); }
  }

  async removeItem(itemId) {
    const res = await fetch(`${this.apiBase}/cart/${this.userId}/items/${itemId}`, { method: 'DELETE' });
    if (res.ok) { await this.loadCart(); this.updateUI(); auth.toast('🗑️ Entfernt', 'info'); }
  }

  async placeOrder() {
    if (!auth.isLoggedIn()) { auth.toast('⚠️ Bitte einloggen', 'warning'); return; }
    await this.loadCart();
    if (!this.cart?.items.length) return;
    try {
      const res = await fetch(`${this.apiBase}/orders/?user_id=${this.userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payment_method: 'Credit Card', shipping_address_id: null })
      });
      if (!res.ok) throw new Error('Bestellung fehlgeschlagen');
      await this.loadCart();
      this.updateUI();
      auth.toast('🎉 Bestellung erfolgreich!', 'success');
      setTimeout(() => window.location.href = '/shop/orders', 1500);
    } catch (err) { auth.toast('Fehler', 'error'); }
  }

  updateUI() {
    this.updateBadge();
    const container = document.getElementById('cart-items');
    if (!container) return;
    if (!this.cart?.items.length) {
      container.innerHTML = `<p class="empty-cart">🛒 Dein Warenkorb ist leer.<br><a href="/shop/products" class="btn-secondary">Weiter einkaufen</a></p>`;
      return;
    }
    container.innerHTML = this.cart.items.map(item => `
      <div class="cart-item">
        <img src="${item.product.image_url || '/static/images/baskets_001.png'}" alt="${item.product.name}" class="cart-item-image">
        <div class="cart-item-details">
          <h4>${item.product.name}</h4>
          <p class="price">€${item.product.price.toFixed(2)}</p>
          <div class="quantity-controls">
            <button class="qty-btn" onclick="cart.changeQty(${item.id}, -1)">−</button>
            <span class="qty-value">${item.quantity}</span>
            <button class="qty-btn" onclick="cart.changeQty(${item.id}, 1)">+</button>
          </div>
        </div>
        <button class="remove-btn" onclick="cart.removeItem(${item.id})">✕</button>
      </div>
    `).join('');
    this.calculateTotals();
  }

  calculateTotals() {
    const subtotalEl = document.querySelector('.summary-panel .subtotal');
    const totalEl = document.querySelector('.summary-panel .total');
    if (!subtotalEl || !this.cart?.items.length) return;
    const subtotal = this.cart.items.reduce((sum, i) => sum + i.product.price * i.quantity, 0);
    subtotalEl.textContent = `€${subtotal.toFixed(2)}`;
    totalEl.textContent = `€${(subtotal + (subtotal >= 50 ? 0 : 4.99)).toFixed(2)}`;
  }

  updateBadge() {
    const badge = document.querySelector('.cart-icon .badge');
    if (!badge) return;
    const count = this.cart?.items.reduce((sum, i) => sum + i.quantity, 0) || 0;
    badge.textContent = count;
    badge.style.display = count > 0 ? 'flex' : 'none';
  }
}

const cart = new CartManager();
window.cart = cart;

// === 3. PRODUKT-MANAGER ===
class ProductManager {
  constructor() {
    this.allProducts = [];
    this.currentCategory = 'all';
  }

  async load() {
    const container = document.getElementById('products-list');
    if (!container) return;
    
    // Check for search query in URL
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('search') || urlParams.get('q');
    
    try {
      const endpoint = searchQuery 
        ? `${API_BASE}/products/?search=${encodeURIComponent(searchQuery)}`
        : `${API_BASE}/products/`;
      
      const res = await fetch(endpoint);
      this.allProducts = await res.json();
      this.render();
      this.initFilters();
      
      if (searchQuery) {
        const titleEl = document.querySelector('.hero-content h1');
        if (titleEl) titleEl.textContent = `Suchergebnisse für "${searchQuery}"`;
      }
    } catch (e) { container.innerHTML = '<p class="small-note">Produkte konnten nicht geladen werden.</p>'; }
  }

  render(list = this.allProducts) {
    const container = document.getElementById('products-list');
    if (!container) return;
    if (!list.length) { container.innerHTML = '<p class="small-note">Keine Produkte gefunden.</p>'; return; }
    container.innerHTML = list.map(p => `
      <article class="product-card">
        <div class="image-wrapper">
          <img src="${p.image_url || '/static/images/baskets_001.png'}" alt="${p.name}">
        </div>
        <div class="content">
          <h3>${p.name}</h3>
          <p>${p.description ? p.description.substring(0, 100) + '...' : ''}</p>
          <p class="price">€${p.price.toFixed(2)}</p>
          <div class="card-actions">
            <button class="btn-primary add-to-cart-btn" data-product-id="${p.id}">🛒 In den Warenkorb</button>
            <a href="/shop/product?id=${p.id}" class="btn-secondary">Details</a>
          </div>
        </div>
      </article>
    `).join('');
  }

  initFilters() {
    const cards = document.querySelectorAll('.category-card');
    cards.forEach(card => {
      card.onclick = () => {
        const cat = card.dataset.category;
        cards.forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        this.filter(cat);
      };
    });
  }

  filter(categoryId) {
    const filtered = categoryId === 'all' ? this.allProducts : this.allProducts.filter(p => p.category_id == categoryId);
    this.render(filtered);
    const descriptions = {
      'all': 'Stilvolle Aufbewahrung für ein schönes Zuhause im Freien.',
      '1': 'Flexible, natürliche Aufbewahrungslösungen für jeden Raum.',
      '2': 'Stauraum im modernen Outdoor-Look - praktisch und stilvoll.',
      '3': 'Praktische Helfer für Balkon und Garten.',
      '4': 'Schöne Details for das perfekte Outdoor-Ambiente.'
    };
    const desc = document.getElementById('category-description');
    if (desc) desc.textContent = descriptions[categoryId] || descriptions['all'];
    document.getElementById('products')?.scrollIntoView({ behavior: 'smooth' });
  }
}

const products = new ProductManager();

// === 4. ADMIN-MANAGER ===
class AdminManager {
  constructor() { this.apiBase = API_BASE; }

  async loadStats() {
    const stats = document.getElementById('admin-stats');
    if (!stats) return;
    try {
      const res = await fetch(`${this.apiBase}/init/check-data`);
      const d = await res.json();
      stats.innerHTML = `<p>Produkte: ${d.products} | Bestellungen: ${d.orders} | Nutzer: ${d.users}</p>`;
    } catch (e) { stats.innerHTML = 'Fehler'; }
  }

  async loadAllProducts() {
    const list = document.getElementById('admin-products-list');
    if (!list) return;
    try {
      const res = await fetch(`${this.apiBase}/products/`);
      const pList = await res.json();
      list.innerHTML = pList.map(p => `
        <div class="admin-item" style="display:flex; justify-content:space-between; margin-bottom:0.5rem; padding:0.5rem; background:#f9f9f9; border-radius:8px;">
          <span>${p.name} - €${p.price.toFixed(2)}</span>
          <button onclick="admin.deleteProduct(${p.id})" style="background:none; border:none; cursor:pointer;">🗑️</button>
        </div>
      `).join('');
    } catch (e) { list.innerHTML = 'Fehler'; }
  }

  async loadAllOrders() {
    const list = document.getElementById('admin-orders-list');
    if (!list) return;
    try {
      const res = await fetch(`${this.apiBase}/orders/`);
      const oList = await res.json();
      list.innerHTML = oList.map(o => `
        <div class="admin-item" style="padding:0.5rem; background:#f9f9f9; border-radius:8px; margin-bottom:0.5rem;">
          <strong>#${o.order_number}</strong> (${o.status}) - €${o.total_price.toFixed(2)}
        </div>
      `).join('');
    } catch (e) { list.innerHTML = 'Fehler'; }
  }

  async deleteProduct(id) {
    if (!confirm('Löschen?')) return;
    const res = await fetch(`${this.apiBase}/products/${id}`, { method: 'DELETE' });
    if (res.ok) { auth.toast('Gelöscht', 'info'); this.loadAllProducts(); }
  }

  async addProduct(data) {
    const res = await fetch(`${this.apiBase}/products/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Fehler');
    return await res.json();
  }
}

// === 4. SEARCH-MANAGER ===
class SearchManager {
  constructor() {
    this.overlay = document.getElementById('search-overlay');
    this.input = document.getElementById('search-input');
    this.btn = document.querySelector('.search-btn');
    this.closeBtn = document.getElementById('close-search');
    this.debounceTimer = null;
    this.init();
  }

  init() {
    if (!this.overlay || !this.btn) return;
    
    this.btn.onclick = (e) => { e.preventDefault(); this.toggle(true); };
    this.closeBtn.onclick = () => this.toggle(false);
    
    this.input.oninput = (e) => {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => this.handleSearch(e.target.value), 300);
    };

    this.input.onkeydown = (e) => {
      if (e.key === 'Enter') {
        const val = this.input.value.trim();
        if (val) window.location.href = `/shop/products?search=${encodeURIComponent(val)}`;
      }
    };
  }

  toggle(show) {
    this.overlay.classList.toggle('active', show);
    if (show) {
        this.input.focus();
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
  }

  async handleSearch(query) {
    if (!query.trim()) {
        document.getElementById('quick-results').innerHTML = '';
        return;
    }

    if (window.location.pathname.includes('/shop/products')) {
        // Live filter if on products page
        const filtered = products.allProducts.filter(p => 
            p.name.toLowerCase().includes(query.toLowerCase()) || 
            p.description.toLowerCase().includes(query.toLowerCase())
        );
        products.render(filtered);
    } else {
        // Show quick results if elsewhere
        try {
            const res = await fetch(`${API_BASE}/products/?search=${encodeURIComponent(query)}&limit=5`);
            const data = await res.json();
            this.renderQuickResults(data);
        } catch (e) {}
    }
  }

  renderQuickResults(items) {
    const container = document.getElementById('quick-results');
    if (!items.length) {
        container.innerHTML = '<p style="padding:1rem;color:var(--text-muted);">Keine Treffer</p>';
        return;
    }
    container.innerHTML = `
      <div style="font-size:0.85rem; color:var(--text-muted); padding:0.5rem 0.75rem;">Schnellansicht:</div>
      ${items.map(p => `
        <a href="/shop/product?id=${p.id}" class="quick-result-item">
            <img src="${p.image_url || '/static/images/baskets_001.png'}" alt="${p.name}">
            <div>
                <div style="font-weight:600;color:var(--text-primary);">${p.name}</div>
                <div style="font-size:0.85rem;color:var(--accent);">€${p.price.toFixed(2)}</div>
            </div>
        </a>
      `).join('')}
    `;
  }
}

const searchManager = new SearchManager();

const admin = new AdminManager();
window.admin = admin;

// === 5. INITIALISIERUNG ===
document.addEventListener('DOMContentLoaded', async () => {
  auth.updateUI();
  products.load();

  if (document.getElementById('orders-list')) {
    try {
      const res = await fetch(`${API_BASE}/orders/user/${auth.getUserId()}`);
      const oList = await res.json();
      document.getElementById('orders-list').innerHTML = oList.length 
        ? oList.map(o => `<div class="order-card" style="padding:1rem; border:1px solid #eee; border-radius:12px; margin-bottom:1rem;"><strong>#${o.order_number}</strong> - ${o.status} - €${o.total_price.toFixed(2)}</div>`).join('')
        : '<p>Noch keine Bestellungen.</p>';
    } catch (e) { }
  }

  // Home Page Specific Logic: Limit to 4 products
  const isHomePage = window.location.pathname === '/' || window.location.pathname === '/index.html' || window.location.pathname === '';
  if (isHomePage) {
    setTimeout(() => {
        if (products.allProducts && products.allProducts.length > 0) {
            console.log('Home Page: Limiting to 4 products');
            products.render(products.allProducts.slice(0, 4));
        }
    }, 500);
  }

  if (document.getElementById('admin-products-list')) {
    if (!auth.user?.is_admin) { window.location.href = '/'; return; }
    admin.loadStats(); admin.loadAllProducts(); admin.loadAllOrders();
    const form = document.getElementById('admin-product-form');
    if (form) form.onsubmit = async (e) => {
      e.preventDefault();
      try {
        await admin.addProduct({
          name: document.getElementById('product-name').value,
          description: document.getElementById('product-description').value,
          price: parseFloat(document.getElementById('product-price').value),
          stock: parseInt(document.getElementById('product-stock').value),
          category_id: parseInt(document.getElementById('product-category').value)
        });
        auth.toast('✅ Produkt erstellt', 'success'); form.reset(); admin.loadAllProducts(); admin.loadStats();
      } catch (e) { auth.toast('Fehler', 'error'); }
    };
  }

  const loginForm = document.getElementById('login-form');
  if (loginForm) loginForm.onsubmit = async (e) => {
    e.preventDefault();
    const u = document.getElementById('username_or_email').value;
    const p = document.getElementById('password').value;
    console.log(`Versuche Login für: ${u}`);
    try {
      await auth.login(u, p);
      auth.toast('🚀 Erfolgreich angemeldet!', 'success');
      setTimeout(() => window.location.href = '/', 1000);
    } catch (err) {
      console.error('Login Fehler:', err);
      auth.toast(`❌ Login fehlgeschlagen: ${err.message}`, 'error');
    }
  };

  const registerForm = document.getElementById('register-form');
  if (registerForm) registerForm.onsubmit = async (e) => {
    e.preventDefault();
    try {
      await auth.register({
        firstname: document.getElementById('firstname').value,
        lastname: document.getElementById('lastname').value,
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
      });
      auth.toast('✨ Konto erstellt!', 'success'); setTimeout(() => window.location.href = '/shop/login', 1500);
    } catch (e) { auth.toast('Registrierung fehlgeschlagen', 'error'); }
  };

  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.add-to-cart-btn');
    if (btn) { e.preventDefault(); await cart.addToCart(btn.dataset.productId); }
  });

  const checkoutBtn = document.getElementById('checkout');
  if (checkoutBtn) checkoutBtn.onclick = () => cart.placeOrder();

  await cart.loadCart(); cart.updateUI();
});
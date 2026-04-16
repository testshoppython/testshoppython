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
    this.userId = auth.getUserId(); // Immer aktuelle ID holen
    const item = this.cart.items.find(i => i.id == itemId);
    if (!item) {
        console.error(`Item mit id ${itemId} nicht im lokalen Warenkorb gefunden`);
        return;
    }
    
    const newQty = item.quantity + delta;
    if (newQty <= 0) return this.removeItem(itemId);
    
    try {
        const res = await fetch(`${this.apiBase}/cart/${this.userId}/items/${itemId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_id: item.product_id, quantity: newQty })
        });
        
        if (res.ok) { 
            await this.loadCart(); 
            this.updateUI(); 
        } else {
            const errData = await res.json();
            auth.toast(`Fehler: ${errData.detail || 'Konnte Menge nicht ändern'}`, 'error');
        }
    } catch (e) {
        console.error(e);
        auth.toast('Netzwerkfehler beim Aktualisieren', 'error');
    }
  }

  async removeItem(itemId) {
    const res = await fetch(`${this.apiBase}/cart/${this.userId}/items/${itemId}`, { method: 'DELETE' });
    if (res.ok) { await this.loadCart(); this.updateUI(); auth.toast('🗑️ Entfernt', 'info'); }
  }

  async placeOrder() {
    if (!auth.isLoggedIn()) { auth.toast('⚠️ Bitte einloggen', 'warning'); return; }
    await this.loadCart();
    if (!this.cart?.items.length) return;
    
    // Check selected payment method from UI if we are on cart page
    let pm = 'Credit Card';
    const checkedPm = document.querySelector('input[name="payment_method"]:checked');
    if (checkedPm) { pm = checkedPm.value; }

    const btn = document.getElementById('checkout');
    if(btn) { btn.textContent = 'Lädt...'; btn.disabled = true; }

    try {
      // 1. Try Stripe Checkout
      const stripeRes = await fetch(`${this.apiBase}/payment/create-checkout-session?user_id=${this.userId}`, { method: 'POST' });
      if (stripeRes.ok) {
         const data = await stripeRes.json();
         if (data.checkout_url) {
             window.location.href = data.checkout_url;
             return;
         }
      }
      
      // 2. Fallback to direct order if Stripe is not configured
      const res = await fetch(`${this.apiBase}/orders/?user_id=${this.userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payment_method: pm, shipping_address_id: null })
      });
      if (!res.ok) throw new Error('Bestellung fehlgeschlagen');
      
      await this.loadCart();
      this.updateUI();
      auth.toast('🎉 Bestellung (Test) erfolgreich!', 'success');
      setTimeout(() => window.location.href = '/shop/profile', 1500);
    } catch (err) { 
      auth.toast('Fehler beim Bezahlen', 'error'); 
      if(btn) { btn.textContent = 'Sicher bezahlen'; btn.disabled = false; }
    }
  }

  updateUI() {
    this.updateBadge();
    const container = document.getElementById('cart-items');
    if (!container) return;
    if (!this.cart?.items.length) {
      container.innerHTML = `<p class="empty-cart">🛒 Ihr Warenkorb ist leer.<br><a href="/shop/products" class="btn-secondary">Weiter einkaufen</a></p>`;
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
    const shippingEl = document.querySelector('.summary-panel .shipping');
    
    if (!subtotalEl || !this.cart?.items.length) return;
    
    const subtotal = this.cart.items.reduce((sum, i) => sum + i.product.price * i.quantity, 0);
    const shipping = subtotal >= 50 ? 0 : 4.99;
    
    subtotalEl.textContent = `€${subtotal.toFixed(2)}`;
    if (shippingEl) shippingEl.textContent = shipping === 0 ? 'kostenlos' : `€${shipping.toFixed(2)}`;
    if (totalEl) totalEl.textContent = `€${(subtotal + shipping).toFixed(2)}`;
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
            <a href="/shop/product?id=${p.id}" class="btn-secondary">Details</a>
            <button class="btn-primary add-to-cart-btn" data-product-id="${p.id}">
              <span class="material-icons" style="font-size: 1.1rem; vertical-align: middle; margin-right: 4px;">shopping_cart</span> In den Warenkorb
            </button>
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
      const res = await fetch(`${this.apiBase}/admin/stats`);
      const d = await res.json();
      stats.innerHTML = `
        <div class="admin-stats-grid">
            <div class="stat-card"><h4>Produkte</h4><div class="value">${d.total_products}</div></div>
            <div class="stat-card"><h4>Nutzer</h4><div class="value">${d.total_users}</div></div>
            <div class="stat-card"><h4>Bestellungen</h4><div class="value">${d.total_orders}</div></div>
            <div class="stat-card"><h4>Umsatz</h4><div class="value">€${d.total_revenue.toFixed(2)}</div></div>
        </div>
      `;
    } catch (e) { stats.innerHTML = 'Fehler beim Laden der Statistiken'; }
  }

  async loadAllProducts() {
    const list = document.getElementById('admin-products-list');
    if (!list) return;
    try {
      const res = await fetch(`${this.apiBase}/admin/products`);
      const pList = await res.json();
      list.innerHTML = pList.map(p => `
        <div class="admin-item">
          <span>${p.name} - <span style="color:var(--accent);">€${p.price.toFixed(2)}</span> (Lager: ${p.stock})</span>
          <button onclick="admin.deleteProduct(${p.id})" class="delete-btn" title="Löschen">🗑️</button>
        </div>
      `).join('');
    } catch (e) { list.innerHTML = 'Fehler beim Laden der Produkte'; }
  }

  async loadAllOrders() {
    const list = document.getElementById('admin-orders-list');
    if (!list) return;
    try {
      const res = await fetch(`${this.apiBase}/admin/orders/revenue`);
      const data = await res.json();
      list.innerHTML = `
        <div class="stat-card" style="margin-bottom:1rem;">
            <h4>Gesamtumsatz (Bezahlt)</h4>
            <div class="value">€${data.total_revenue.toFixed(2)}</div>
            <p class="small-note">${data.total_orders} Bestellungen gesamt</p>
        </div>
      `;
    } catch (e) { list.innerHTML = 'Fehler beim Laden der Bestellungen'; }
  }

  async deleteProduct(id) {
    if (!confirm('Produkt wirklich löschen?')) return;
    const res = await fetch(`${this.apiBase}/admin/products/${id}`, { 
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    });
    if (res.ok) { auth.toast('🗑️ Produkt gelöscht', 'info'); this.loadAllProducts(); this.loadStats(); }
  }

  async addProduct(formData) {
    const res = await fetch(`${this.apiBase}/admin/products`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: formData
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Fehler beim Erstellen');
    }
    return await res.json();
  }

  async loadCategoriesDropdown() {
    const select = document.getElementById('product-category');
    if (!select) return;
    try {
      const res = await fetch(`${this.apiBase}/products/categories/`);
      const cats = await res.json();
      select.innerHTML = '<option value="" disabled selected>Kategorie wählen...</option>' + 
        cats.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    } catch (e) { console.error('Kategorien konnten nicht geladen werden', e); }
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
    const container = document.getElementById('search-results-container');
    if (!query.trim()) {
        if (container) container.style.display = 'none';
        return;
    }

    if (window.location.pathname.includes('/shop/products')) {
        // Live filter if on products page
        const filtered = products.allProducts.filter(p => 
            p.name.toLowerCase().includes(query.toLowerCase()) || 
            p.description.toLowerCase().includes(query.toLowerCase())
        );
        products.render(filtered);
    }
    
    // Show quick results (even on products page for the overlay)
    try {
        const res = await fetch(`${API_BASE}/products/?search=${encodeURIComponent(query)}&limit=10`);
        const data = await res.json();
        this.renderQuickResults(query, data);
    } catch (e) {}
  }

  renderQuickResults(query, items) {
    const container = document.getElementById('search-results-container');
    const suggContainer = document.getElementById('search-suggestions');
    const catContainer = document.getElementById('search-categories');
    const prodContainer = document.getElementById('search-products-grid');

    if (!container) return;

    if (!items.length) {
        container.style.display = 'block';
        suggContainer.innerHTML = '<p class="search-muted">Keine Vorschläge</p>';
        catContainer.innerHTML = '<p class="search-muted">Keine Kategorien</p>';
        prodContainer.innerHTML = '<p class="search-muted" style="grid-column: 1/-1;">Konnte nichts für "' + query + '" finden.</p>';
        return;
    }

    container.style.display = 'block';

    const lowerQuery = query.toLowerCase();
    
    // Highlight helper
    const highlight = (text) => {
        const idx = text.toLowerCase().indexOf(lowerQuery);
        if (idx === -1) return text;
        return text.substring(0, idx) + '<strong>' + text.substring(idx, idx + lowerQuery.length) + '</strong>' + text.substring(idx + lowerQuery.length);
    };

    // 1. Suggestions: Extract distinct names and highlight
    const uniqueNames = [...new Set(items.map(p => p.name))].slice(0, 5);
    suggContainer.innerHTML = uniqueNames.map(name => `
        <a href="/shop/products?search=${encodeURIComponent(name)}" class="search-item">
            ${highlight(name.toLowerCase())}
        </a>
    `).join('');

    // 2. Categories: Extract distinct categories
    const categories = [];
    items.forEach(p => {
        if (p.category && p.category.name && !categories.some(c => c.id === p.category.id)) {
            categories.push(p.category);
        }
    });

    if (categories.length) {
        catContainer.innerHTML = categories.slice(0, 4).map(c => `
            <a href="/shop/products?category=${c.id}" class="search-item">
                ${c.name.toLowerCase().includes(lowerQuery) ? highlight(c.name.toLowerCase()) : c.name.toLowerCase()}
            </a>
        `).join('');
    } else {
        catContainer.innerHTML = '<p class="search-muted">Keine zugehörigen Kategorien</p>';
    }

    // 3. Products: Render minimal grid
    prodContainer.innerHTML = items.slice(0, 8).map(p => `
        <a href="/shop/product?id=${p.id}" class="search-product-card">
            <img src="${p.image_url || '/static/images/baskets_001.png'}" alt="${p.name}" class="search-product-image">
        </a>
    `).join('');
  }
}

const searchManager = new SearchManager();

const admin = new AdminManager();
window.admin = admin;

// === 5. INITIALISIERUNG ===
document.addEventListener('DOMContentLoaded', async () => {
  auth.updateUI();
  products.load();

  // Profile Page Logic
  if (document.getElementById('profile-orders-list')) {
      if (!auth.isLoggedIn()) {
          window.location.href = '/shop/login';
          return;
      }
      
      const params = new URLSearchParams(window.location.search);
      if (params.get('success') === 'true') {
          auth.toast('🎉 Zahlung erfolgreich! Ihre Bestellung wird bearbeitet.', 'success');
          window.history.replaceState({}, document.title, "/shop/profile");
      }
      
      const greeting = document.getElementById('profile-greeting');
      if(greeting && auth.user) greeting.textContent = `${auth.user.firstname || auth.user.username}, verwalten Sie hier Ihre Daten.`;

      // Tabs Logic
      const tabs = document.querySelectorAll('.profile-tab');
      const tabsContent = document.querySelectorAll('.profile-tab-content');
      tabs.forEach(tab => {
          tab.onclick = () => {
              tabs.forEach(t => t.classList.remove('active'));
              tabsContent.forEach(tc => tc.classList.remove('active'));
              tab.classList.add('active');
              document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
          };
      });

      // Load Orders
      try {
        const res = await fetch(`${API_BASE}/orders/user/${auth.getUserId()}`);
        const oList = await res.json();
        document.getElementById('profile-orders-list').innerHTML = oList.length 
          ? oList.map(o => `
            <div class="order-card" style="padding:1.5rem; background:#fff; border:1px solid var(--border); border-radius:12px; margin-bottom:1rem; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong style="font-size:1.1rem;">#${o.order_number}</strong>
                    <div style="color:var(--text-muted); font-size:0.9rem; margin-top:0.25rem;">
                        Status: <span style="color:var(--accent-dark); font-weight:500;">${o.status.toUpperCase()}</span> | Total: €${o.total_price.toFixed(2)}
                    </div>
                </div>
                <a href="${API_BASE}/orders/${o.id}/invoice" target="_blank" class="btn-secondary" style="font-size:0.8rem; padding:0.5rem 1rem;">📄 PDF Rechnung</a>
            </div>`).join('')
          : '<p>Noch keine Bestellungen.</p>';
      } catch (e) { }
      
      // Password Change Logic
      const pwForm = document.getElementById('password-change-form');
      if (pwForm) {
          pwForm.onsubmit = async (e) => {
              e.preventDefault();
              const current = document.getElementById('pw-current').value;
              const newPw = document.getElementById('pw-new').value;
              const confirmPw = document.getElementById('pw-new-confirm').value;
              
              if (newPw !== confirmPw) {
                  auth.toast('Passwörter stimmen nicht überein.', 'warning');
                  return;
              }
              
              try {
                  const res = await fetch(`${API_BASE}/users/profile/${auth.getUserId()}/password`, {
                      method: 'PUT',
                      headers: {'Content-Type': 'application/json'},
                      body: JSON.stringify({ current_password: current, new_password: newPw })
                  });
                  if (res.ok) {
                      auth.toast('✅ Passwort geändert!', 'success');
                      pwForm.reset();
                  } else {
                      const err = await res.json();
                      auth.toast(`❌ Fehler: ${err.detail}`, 'error');
                  }
              } catch(err) { auth.toast('Netzwerkfehler', 'error'); }
          };
      }
  }

  // Home Page Specific Logic: Limit to 4 products
  const isHomePage = window.location.pathname === '/' || window.location.pathname === '/index.html';
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
    admin.loadStats(); admin.loadAllProducts(); admin.loadAllOrders(); admin.loadCategoriesDropdown();
    const form = document.getElementById('admin-product-form');
    if (form) form.onsubmit = async (e) => {
      e.preventDefault();
      try {
        const formData = new FormData();
        formData.append('name', document.getElementById('product-name').value);
        formData.append('description', document.getElementById('product-description').value);
        formData.append('price', document.getElementById('product-price').value);
        formData.append('stock', document.getElementById('product-stock').value);
        formData.append('category_id', document.getElementById('product-category').value);
        
        const imageFile = document.getElementById('product-image').files[0];
        if (imageFile) {
            formData.append('file', imageFile);
        }

        await admin.addProduct(formData);
        auth.toast('✅ Produkt erfolgreich erstellt', 'success'); 
        form.reset(); 
        admin.loadAllProducts(); 
        admin.loadStats();
      } catch (err) { 
        auth.toast(`Error: ${err.message}`, 'error'); 
      }
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

  // Mobile Menu Logic
  const mobileToggle = document.getElementById('mobile-menu-toggle');
  const navLinks = document.querySelector('.nav-links-block');
  const menuIconPath = document.getElementById('menu-icon-path');

  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      const isActive = navLinks.classList.toggle('mobile-active');
      
      // Toggle Icon between Hamburger and Close (X)
      if (isActive) {
        menuIconPath.setAttribute('d', 'M6 18L18 6M6 6l12 12');
        document.body.style.overflow = 'hidden'; // Prevent scrolling when menu is open
      } else {
        menuIconPath.setAttribute('d', 'M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5');
        document.body.style.overflow = '';
      }
    });

    // Close menu when clicking on a link
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('mobile-active');
        menuIconPath.setAttribute('d', 'M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5');
        document.body.style.overflow = '';
      });
    });
  }

  // Newsletter Logic
  const newsletterForm = document.getElementById('newsletter-form');
  if (newsletterForm) {
    newsletterForm.onsubmit = async (e) => {
      e.preventDefault();
      const email = document.getElementById('newsletter-email').value;
      const checkboxes = newsletterForm.querySelectorAll('input[name="interest"]:checked');
      const interests = Array.from(checkboxes).map(cb => cb.value);
      
      const btn = newsletterForm.querySelector('.newsletter-submit-btn');
      const originalText = btn.textContent;
      btn.textContent = 'Wird gesendet...';
      btn.disabled = true;

      try {
        const res = await fetch(`${API_BASE}/newsletter/subscribe`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, interests })
        });
        
        if (res.ok) {
          auth.toast('✨ Erfolgreich angemeldet! Bitte checken Sie Ihre E-Mails.', 'success');
          newsletterForm.reset();
        } else {
          const err = await res.json();
          auth.toast(`❌ Fehler: ${err.detail || 'Newsletter-Anmeldung fehlgeschlagen'}`, 'error');
        }
      } catch (err) {
        auth.toast('❌ Netzwerkfehler bei der Anmeldung.', 'error');
      } finally {
        btn.textContent = originalText;
        btn.disabled = false;
      }
    };
  }

  await cart.loadCart(); cart.updateUI();
});
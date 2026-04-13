const API_BASE = window.location.origin;

function getStoredUser() {
    try {
        return JSON.parse(localStorage.getItem('owre_user') || 'null');
    } catch (error) {
        return null;
    }
}

function getAuthHeaders() {
    const token = localStorage.getItem('owre_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
}

function getCurrentUserId() {
    const user = getStoredUser();
    return user?.id || null;
}

function changeLanguage(lang) {
    const url = new URL(window.location);
    url.searchParams.set('lang', lang);
    window.location.href = url.toString();
}

function updateAuthLinks() {
    const user = getStoredUser();
    const loginLink = document.getElementById('login-link');
    const registerLink = document.getElementById('register-link');
    const logoutLink = document.getElementById('logout-link');
    const ordersLink = document.getElementById('orders-link');
    const adminLink = document.getElementById('admin-link');

    if (user) {
        loginLink?.classList.add('hidden');
        registerLink?.classList.add('hidden');
        logoutLink?.classList.remove('hidden');
        ordersLink?.classList.remove('hidden');
        if (user.is_admin) {
            adminLink?.classList.remove('hidden');
        } else {
            adminLink?.classList.add('hidden');
        }
    } else {
        loginLink?.classList.remove('hidden');
        registerLink?.classList.remove('hidden');
        logoutLink?.classList.add('hidden');
        ordersLink?.classList.add('hidden');
        adminLink?.classList.add('hidden');
    }
}

function logoutUser() {
    localStorage.removeItem('owre_token');
    localStorage.removeItem('owre_user');
    updateAuthLinks();
    window.location.href = '/';
}

async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE}/products/`);
        const products = await response.json();
        const container = document.getElementById('products-list');
        if (!container) return;
        container.innerHTML = products.map(product => `
            <article class="product-card">
                <a href="/shop/product?id=${product.id}">
                    <img src="${product.image_url || '/static/images/baskets_001.png'}" alt="${product.name}" class="product-image">
                    <div class="product-card-body">
                        <h3>${product.name}</h3>
                        <p>${product.description}</p>
                        <div class="product-meta">
                            <span class="product-price">€${product.price.toFixed(2)}</span>
                            <span>${product.stock} Stück</span>
                        </div>
                    </div>
                </a>
                <button class="btn-primary" onclick="addToCart(${product.id})">In den Warenkorb</button>
            </article>
        `).join('');
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

async function loadProductDetail(productId) {
    try {
        const response = await fetch(`${API_BASE}/products/${productId}`);
        if (!response.ok) {
            throw new Error('Produkt nicht gefunden');
        }
        const product = await response.json();
        const container = document.getElementById('product-detail');
        if (!container) return;
        container.innerHTML = `
            <div class="detail-image">
                <img src="${product.image_url || '/static/images/baskets_001.png'}" alt="${product.name}">
            </div>
            <div class="detail-content">
                <h2>${product.name}</h2>
                <p>${product.description}</p>
                <p><strong>Preis:</strong> €${product.price.toFixed(2)}</p>
                <p><strong>Lagerbestand:</strong> ${product.stock}</p>
                <p><strong>Kategorie:</strong> ${product.category?.name || '–'}</p>
            </div>
        `;
        const button = document.getElementById('add-to-cart');
        if (button) {
            button.onclick = () => addToCart(product.id);
        }
    } catch (error) {
        console.error('Error loading product:', error);
    }
}

async function addToCart(productId, quantity = 1) {
    const userId = getCurrentUserId();
    if (!userId) {
        alert('Bitte zuerst einloggen, um den Warenkorb zu nutzen.');
        window.location.href = '/user/login';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/cart/${userId}/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders()
            },
            body: JSON.stringify({ product_id: productId, quantity })
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Fehler beim Hinzufügen zum Warenkorb');
        }
        alert('Produkt wurde dem Warenkorb hinzugefügt.');
        if (document.getElementById('cart-items')) {
            loadCart();
        }
    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}

async function loadCart() {
    const userId = getCurrentUserId();
    const container = document.getElementById('cart-items');
    const summary = document.getElementById('cart-summary');
    if (!container || !summary) return;
    if (!userId) {
        container.innerHTML = `<p class="small-note">Bitte melden Sie sich an, um Ihren Warenkorb anzuzeigen.</p>`;
        summary.innerHTML = `<p>${'Bitte einloggen'}</p>`;
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/cart/${userId}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) {
            throw new Error('Warenkorb konnte nicht geladen werden.');
        }
        const cart = await response.json();
        if (!cart.items.length) {
            container.innerHTML = `<p class="small-note">Dein Warenkorb ist leer.</p>`;
            summary.innerHTML = `<p>${'Zwischensumme:'} <strong>€0.00</strong></p><button class="btn-primary" onclick="window.location.href='/shop/products'">Weiter einkaufen</button>`;
            return;
        }

        container.innerHTML = cart.items.map(item => `
            <div class="cart-item">
                <img src="${item.product.image_url || '/static/images/baskets_001.png'}" alt="${item.product.name}">
                <div class="cart-item-details">
                    <h3>${item.product.name}</h3>
                    <p>${item.product.description}</p>
                    <div class="cart-item-meta">
                        <span>${item.quantity} x €${item.product.price.toFixed(2)}</span>
                        <button class="btn-secondary" onclick="removeCartItem(${userId}, ${item.id})">Entfernen</button>
                    </div>
                </div>
            </div>
        `).join('');

        const total = cart.items.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
        summary.innerHTML = `
            <p>${'Zwischensumme:'} <strong>€${total.toFixed(2)}</strong></p>
            <button class="btn-primary" id="checkout">Zur Kasse</button>
        `;
        document.getElementById('checkout').onclick = () => createOrder(userId);
    } catch (error) {
        console.error(error);
        container.innerHTML = `<p class="small-note">Fehler beim Laden des Warenkorbs.</p>`;
        summary.innerHTML = '';
    }
}

async function removeCartItem(userId, itemId) {
    try {
        const response = await fetch(`${API_BASE}/cart/${userId}/items/${itemId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        if (!response.ok) {
            throw new Error('Fehler beim Entfernen des Artikels');
        }
        loadCart();
    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}

async function createOrder(userId) {
    try {
        const response = await fetch(`${API_BASE}/orders/?user_id=${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders()
            },
            body: JSON.stringify({ payment_method: 'card' })
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Fehler beim Bestellen');
        }
        const order = await response.json();
        alert(`Bestellung ${order.order_number} erfolgreich aufgegeben!`);
        window.location.href = '/user/orders';
    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}

async function handleLoginSubmit(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: form.toString()
        });
        if (!response.ok) {
            throw new Error('Login fehlgeschlagen');
        }
        const data = await response.json();
        localStorage.setItem('owre_token', data.access_token);
        localStorage.setItem('owre_user', JSON.stringify(data.user));
        alert('Login erfolgreich!');
        window.location.href = '/';
    } catch (error) {
        console.error(error);
        alert('Login fehlgeschlagen. Bitte überprüfe deine Zugangsdaten.');
    }
}

async function handleRegisterSubmit(event) {
    event.preventDefault();
    const firstname = document.getElementById('firstname').value;
    const lastname = document.getElementById('lastname').value;
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_BASE}/users/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ firstname, lastname, username, email, password })
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Registrierung fehlgeschlagen');
        }
        alert('Registrierung erfolgreich! Bitte melde dich an.');
        window.location.href = '/user/login';
    } catch (error) {
        console.error(error);
        alert('Registrierung fehlgeschlagen. Bitte überprüfe deine Angaben.');
    }
}

async function loadOrders() {
    const userId = getCurrentUserId();
    const container = document.getElementById('orders-list');
    if (!container) return;
    if (!userId) {
        container.innerHTML = `<p class="small-note">Bitte logge dich ein, um deine Bestellungen zu sehen.</p>`;
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/orders/user/${userId}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) {
            throw new Error('Bestellungen konnten nicht geladen werden.');
        }
        const orders = await response.json();
        if (!orders.length) {
            container.innerHTML = `<p class="small-note">Keine Bestellungen gefunden.</p>`;
            return;
        }
        container.innerHTML = orders.map(order => `
            <article class="order-card">
                <h3>${order.order_number}</h3>
                <p>${order.status}</p>
                <p>€${order.total_price.toFixed(2)}</p>
                <p>${new Date(order.created_at).toLocaleDateString()}</p>
            </article>
        `).join('');
    } catch (error) {
        console.error(error);
        container.innerHTML = `<p class="small-note">Fehler beim Laden der Bestellungen.</p>`;
    }
}

async function loadAdminStats() {
    try {
        const response = await fetch(`${API_BASE}/admin/stats`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) {
            throw new Error('Admin-Statistiken konnten nicht geladen werden.');
        }
        const stats = await response.json();
        const container = document.getElementById('admin-stats');
        if (!container) return;
        container.innerHTML = `
            <p>${stats.total_users} Benutzer</p>
            <p>${stats.total_products} Produkte</p>
            <p>${stats.total_orders} Bestellungen</p>
            <p>Umsatz: €${stats.total_revenue.toFixed(2)}</p>
        `;
    } catch (error) {
        console.error(error);
    }
}

async function loadAdminProducts() {
    const list = document.getElementById('products-admin-list');
    if (!list) return;
    try {
        const response = await fetch(`${API_BASE}/admin/products`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) {
            throw new Error('Produkte konnten nicht geladen werden.');
        }
        const products = await response.json();
        list.innerHTML = products.map(product => `
            <div class="admin-product-item">
                <strong>${product.name}</strong> - €${product.price.toFixed(2)} - Lager: ${product.stock}
            </div>
        `).join('');
    } catch (error) {
        console.error(error);
        list.innerHTML = `<p class="small-note">Fehler beim Laden der Produktliste.</p>`;
    }
}

async function handleAdminProductForm(e) {
    e.preventDefault();
    const name = document.getElementById('product-name').value;
    const description = document.getElementById('product-description').value;
    const price = Number(document.getElementById('product-price').value);
    const stock = Number(document.getElementById('product-stock').value);
    const category_id = Number(document.getElementById('product-category').value);
    const file = document.getElementById('product-image').files[0];

    const formData = new FormData();
    formData.append('name', name);
    formData.append('description', description);
    formData.append('price', price);
    formData.append('stock', stock);
    formData.append('category_id', category_id);
    if (file) {
        formData.append('file', file);
    }

    try {
        const response = await fetch(`${API_BASE}/admin/products`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: formData
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Produkt konnte nicht hinzugefügt werden.');
        }
        alert('Produkt erfolgreich hinzugefügt.');
        loadAdminProducts();
    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('products-list')) {
        loadProducts();
    }
    if (document.getElementById('cart-items')) {
        loadCart();
    }
    if (document.getElementById('product-detail')) {
        const urlParams = new URLSearchParams(window.location.search);
        const productId = urlParams.get('id');
        if (productId) loadProductDetail(productId);
    }
    if (document.getElementById('orders-list')) {
        loadOrders();
    }
    updateAuthLinks();
    if (document.getElementById('admin-stats')) {
        loadAdminStats();
        loadAdminProducts();
    }
    document.getElementById('logout-link')?.addEventListener('click', (event) => {
        event.preventDefault();
        logoutUser();
    });
    document.getElementById('login-form')?.addEventListener('submit', handleLoginSubmit);
    document.getElementById('register-form')?.addEventListener('submit', handleRegisterSubmit);
    document.getElementById('admin-product-form')?.addEventListener('submit', handleAdminProductForm);
});
const API_BASE = window.location.origin;

// Load products with links to details
async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE}/products/`);
        const products = await response.json();
        const container = document.getElementById('products-list');
        container.innerHTML = products.map(product => `
            <div class="product">
                <h3><a href="/product?id=${product.id}">${product.name}</a></h3>
                <p>${product.description}</p>
                <p>Preis: €${product.price}</p>
                <button onclick="addToCart(${product.id})">In den Warenkorb</button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

// Load product detail
async function loadProductDetail(productId) {
    try {
        const response = await fetch(`${API_BASE}/products/${productId}`);
        const product = await response.json();
        const container = document.getElementById('product-detail');
        container.innerHTML = `
            <h2>${product.name}</h2>
            <p>${product.description}</p>
            <p>Preis: €${product.price}</p>
            <p>Kategorie: ${product.category.name}</p>
        `;
        document.getElementById('add-to-cart').onclick = () => addToCart(productId);
    } catch (error) {
        console.error('Error loading product:', error);
    }
}

// Add to cart
async function addToCart(productId) {
    // Implement cart logic here
    alert('Produkt zum Warenkorb hinzugefügt!');
}

// Load cart
async function loadCart() {
    // Implement cart loading
}

// Login
document.getElementById('login-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        alert('Login erfolgreich!');
        window.location.href = '/';
    } catch (error) {
        alert('Login fehlgeschlagen!');
    }
});

// Register
document.getElementById('register-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    try {
        await fetch(`${API_BASE}/users/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        alert('Registrierung erfolgreich!');
        window.location.href = '/login';
    } catch (error) {
        alert('Registrierung fehlgeschlagen!');
    }
});

// Load orders
async function loadOrders() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`${API_BASE}/orders/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const orders = await response.json();
        const container = document.getElementById('orders-list');
        container.innerHTML = orders.map(order => `
            <div class="order">
                <h4>Bestellung #${order.id}</h4>
                <p>Status: ${order.status}</p>
                <p>Gesamt: €${order.total}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading orders:', error);
    }
}

// Load admin stats
async function loadAdminStats() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`${API_BASE}/admin/stats`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const stats = await response.json();
        const container = document.getElementById('admin-stats');
        container.innerHTML = `
            <p>Benutzer: ${stats.users}</p>
            <p>Produkte: ${stats.products}</p>
            <p>Bestellungen: ${stats.orders}</p>
        `;
    } catch (error) {
        console.error('Error loading admin stats:', error);
    }
}

// Initialize
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
    if (document.getElementById('admin-stats')) {
        loadAdminStats();
    }
});
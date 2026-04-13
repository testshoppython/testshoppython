const API_BASE = window.location.origin;

const sampleProducts = [
    {
        id: 1,
        name: "OWRE Aufbewahrungskorb",
        description: "Großer Stoffkorb für Wohnzimmer und Schlafzimmer.",
        price: 29.90,
        image: "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&w=800&q=80"
    },
    {
        id: 2,
        name: "OWRE Box mit Deckel",
        description: "Praktische Aufbewahrungsbox für Regale und Schränke.",
        price: 24.90,
        image: "https://images.unsplash.com/photo-1505692794403-196b8e6f7d22?auto=format&fit=crop&w=800&q=80"
    },
    {
        id: 3,
        name: "OWRE Organizer",
        description: "Eleganter Organizer für Schreibtisch und Büro.",
        price: 18.50,
        image: "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=800&q=80"
    }
];

function renderProducts(products) {
    const container = document.getElementById('products-list');
    if (!container) return;

    container.innerHTML = products.map(product => `
        <article class="product-card">
            <img src="${product.image}" alt="${product.name}">
            <div class="content">
                <h3>${product.name}</h3>
                <p>${product.description}</p>
                <p class="price">€${product.price.toFixed(2)}</p>
                <a href="/shop/product?id=${product.id}" class="btn-primary">Details</a>
            </div>
        </article>
    `).join('');
}

function renderProductDetail(product) {
    const container = document.getElementById('product-detail');
    if (!container) return;

    container.innerHTML = `
        <div class="product-detail-card">
            <img src="${product.image}" alt="${product.name}">
            <div class="content">
                <h2>${product.name}</h2>
                <p>${product.description}</p>
                <p class="price">€${product.price.toFixed(2)}</p>
                <button class="btn-primary" onclick="addToCart(${product.id})">In den Warenkorb</button>
            </div>
        </div>
    `;
}

async function loadProducts() {
    let products = [];
    try {
        const response = await fetch(`${API_BASE}/products/`);
        if (response.ok) {
            products = await response.json();
        }
    } catch (error) {
        console.warn("Produkt-API nicht erreichbar, Fallback verwenden.", error);
    }

    if (!products || !products.length) {
        products = sampleProducts;
    }
    renderProducts(products);
}

async function loadProductDetail(productId) {
    let product = null;

    try {
        const response = await fetch(`${API_BASE}/products/${productId}`);
        if (response.ok) {
            product = await response.json();
        }
    } catch (error) {
        console.warn("Produkt-API nicht erreichbar, Fallback verwenden.", error);
    }

    if (!product) {
        product = sampleProducts.find(item => item.id === Number(productId));
    }

    if (product) {
        renderProductDetail(product);
    } else {
        const container = document.getElementById('product-detail');
        if (container) {
            container.innerHTML = `<p class="small-note">Produkt nicht gefunden.</p>`;
        }
    }
}

function addToCart(productId) {
    alert(`Produkt ${productId} wurde dem Warenkorb hinzugefügt.`);
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('products-list')) {
        loadProducts();
    }

    if (document.getElementById('product-detail')) {
        const urlParams = new URLSearchParams(window.location.search);
        const productId = urlParams.get('id');
        if (productId) {
            loadProductDetail(productId);
        } else {
            document.getElementById('product-detail').innerHTML = '<p class="small-note">Kein Produkt gewählt.</p>';
        }
    }
});
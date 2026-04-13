const API_BASE = window.location.origin;

// Load products
async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE}/products/`);
        const products = await response.json();
        const container = document.getElementById('products-list');
        container.innerHTML = products.map(product => `
            <div class="product">
                <h3>${product.name}</h3>
                <p>${product.description}</p>
                <p>Preis: €${product.price}</p>
                <button onclick="addToCart(${product.id})">In den Warenkorb</button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading products:', error);
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

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('products-list')) {
        loadProducts();
    }
    if (document.getElementById('cart-items')) {
        loadCart();
    }
});
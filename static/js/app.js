const API_BASE = window.location.origin;

const sampleProducts = [
    {
        id: 1,
        name: "OWRE Outdoor Aufbewahrungskorb",
        description: "Großer, atmungsaktiver Stoffkorb für Garten und Terrasse.",
        price: 29.90,
        image: "https://images.unsplash.com/photo-1560185127-6acf6f5f5d3e?auto=format&fit=crop&w=900&q=80"
    },
    {
        id: 2,
        name: "OWRE Deckelbox",
        description: "Stabile Aufbewahrungsbox für Kissen, Decken und Gartendeko.",
        price: 34.90,
        image: "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80"
    },
    {
        id: 3,
        name: "OWRE Outdoor Organizer",
        description: "Praktischer Organizer für Balkon und Home-Office.",
        price: 18.50,
        image: "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&w=900&q=80"
    },
    {
        id: 4,
        name: "OWRE Korb-Set",
        description: "Set aus zwei geflochtenen Körben für stilvolle Ordnung.",
        price: 39.90,
        image: "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=900&q=80"
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

async function loadProducts() {
    let products = [];
    try {
        const response = await fetch(`${API_BASE}/products/`);
        if (response.ok) {
            products = await response.json();
        }
    } catch (error) {
        console.warn("Produkt-API nicht erreichbar:", error);
    }

    if (!products || !products.length) {
        products = sampleProducts;
    }
    renderProducts(products);
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('products-list')) {
        loadProducts();
    }
});
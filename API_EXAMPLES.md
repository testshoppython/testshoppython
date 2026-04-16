# API Beispiele und Workflows

## Schnellstart für lokale Entwicklung

### 1. Testdaten laden
```bash
curl -X POST http://localhost:8000/init/seed-data
```

### 2. Benutzer registrieren
```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "kunde@example.de",
    "username": "kunde123",
    "firstname": "Max",
    "lastname": "Mustermann",
    "phone": "+49 123 456789",
    "password": "sicheres_passwort"
  }'
```

### 3. Produkte abrufen
```bash
curl http://localhost:8000/products/
```

### 4. Produkt nach Kategorie filtern
```bash
curl http://localhost:8000/products/?category_id=1
```

### 5. Produkt zum Warenkorb hinzufügen
```bash
curl -X POST http://localhost:8000/cart/1/items \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

### 6. Warenkorb anschauen
```bash
curl http://localhost:8000/cart/1
```

### 7. Warenkorbsumme berechnen
```bash
curl http://localhost:8000/cart/1/total
```

### 8. Bestellung erstellen
```bash
curl -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "payment_method": "credit_card",
    "shipping_address_id": 1
  }'
```

### 9. Benutzerprofil abrufen
```bash
curl http://localhost:8000/users/profile/1
```

### 10. Admin Statistiken
```bash
curl http://localhost:8000/admin/stats
```

### 11. Newsletter abonnieren (Brevo)
```bash
curl -X POST http://localhost:8000/newsletter/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "kunde@example.de",
    "interests": ["living", "news"]
  }'
```

### 12. Stripe Checkout Session erstellen
```bash
curl -X POST "http://localhost:8000/payment/create-checkout-session?user_id=1"
```

### 13. PDF Rechnung herunterladen
```bash
curl -O -J http://localhost:8000/orders/1/invoice
```

### 14. Benutzer-Passwort ändern (Profil)
```bash
curl -X PUT http://localhost:8000/users/profile/1/password \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "sicheres_passwort",
    "new_password": "neues_sicheres_passwort"
  }'
```

## Shop Workflow Beispiel

### Kunde kauft Produkt

```bash
# 1. Registrierung
RESPONSE=$(curl -s -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hans@example.de",
    "username": "hans",
    "firstname": "Hans",
    "lastname": "Meyer",
    "password": "passwort123"
  }')
USER_ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')

# 2. Adresse hinzufügen
curl -X POST "http://localhost:8000/users/addresses?user_id=$USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "street": "Hauptstrasse 123",
    "city": "Berlin",
    "postal_code": "10115",
    "country": "Deutschland",
    "is_default": true
  }'

# 3. Produkte zum Warenkorb hinzufügen
curl -X POST "http://localhost:8000/cart/$USER_ID/items" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'

# 4. Bestellung erstellen
curl -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": $USER_ID,
    \"payment_method\": \"credit_card\",
    \"shipping_address_id\": 1,
    \"items\": [
      {\"product_id\": 1, \"quantity\": 2}
    ]
  }"

# 5. Benutzer bestellungen abrufen
curl "http://localhost:8000/orders/user/$USER_ID"
```

## Admin Operationen

### Neues Produkt erstellen
```bash
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Neues Produkt",
    "description": "Produktbeschreibung",
    "price": 99.99,
    "stock": 100,
    "category_id": 1,
    "image_url": "https://example.com/image.jpg"
  }'
```

### Produkt aktualisieren
```bash
curl -X PUT http://localhost:8000/products/1 \
  -H "Content-Type: application/json" \
  -d '{
    "price": 89.99,
    "stock": 50
  }'
```

### Bestellstatus aktualisieren
```bash
curl -X PUT http://localhost:8000/orders/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "shipped"
  }'
```

### Top-Verkäufer Produkte
```bash
curl http://localhost:8000/admin/products/popular?limit=10
```

### Produkte mit niedriger Lagerbestand
```bash
curl http://localhost:8000/admin/products/low-stock?threshold=5
```

### Umsatzberichte
```bash
curl http://localhost:8000/admin/orders/revenue
```

## Produktsuche
```bash
curl "http://localhost:8000/products/search/?query=python"
```

## Docker Commands für lokale Entwicklung

```bash
# Container starten
docker-compose up -d

# Container lokal testen
docker-compose exec web bash

# Logs anschauen
docker-compose logs -f web

# Container stoppen
docker-compose down

# Datenbank zurücksetzen
docker-compose down -v
docker-compose up -d
```

## Deployment Checkliste für Render.com

- [ ] `.env` Datei mit `SECRET_KEY` erstellt
- [ ] GitHub Repository ist public
- [ ] `render.yaml` ist im Repository
- [ ] PostgreSQL Datenbank auf Render erstellt
- [ ] Environment Variablen auf Render gesetzt
- [ ] Domain konfiguriert (optional)
- [ ] CORS Origins eingestellt (nicht `["*"]`)
- [ ] SSL/HTTPS aktiviert
- [ ] Health Check funktioniert
- [ ] Testdaten initialisieren nach Deployment

## Performance Tipps

- Paginierung nutzen: `?skip=0&limit=10`
- Kategorien filtern für schnellere Abfragen
- Indizes auf häufig gefilterte Spalten
- Connection Pooling ist bereits konfiguriert

## Häufige Fehler

### 1. "Database not initialized"
```bash
curl -X POST http://localhost:8000/init/seed-data
```

### 2. "User already exists"
Andere Email/Username verwenden

### 3. "Cart not found"
Benutzer muss registriert sein (erstellt automatisch Warenkorb)

### 4. "Product not found"
Produkt ID existiert nicht, Testdaten laden

### 5. "Connection refused" (Render)
- PostgreSQL Service ist nicht verbunden
- DATABASE_URL ist falsch
- Connection Timeout

# OWRE - Premium Storage Solutions

Ein vollständiger Online-Shop für OWRE-Aufbewahrungslösungen, gebaut mit **FastAPI**, **SQLAlchemy** und **SQLite**. Das Projekt ist für lokale Entwicklung und Render.com Deployment vorbereitet.

## Features 🎯

✅ **Produkt Management**
- Kategorien und Produkte
- Produktbilder aus dem Ordner `static/images`
- Produkt hinzufügen per Admin-API
- OWRE-Design und mehrsprachige Texte

✅ **Benutzer Management**
- Benutzerregistrierung
- Benutzerprofil
- Adressverwaltung
- Admin-Funktionen

✅ **Shopping Cart**
- Artikel hinzufügen/entfernen
- Mengen anpassen
- Warenkorb leeren
- Warenkorbsumme berechnen

✅ **Bestellungen**
- Bestellerstellung
- Bestellverfolgung
- Bestellverlauf
- Bestellstatus Management

✅ **Admin-Dashboard**
- Shop-Statistiken
- Umsatzberichte
- Bestellmanagement
- Benutzeranalytics

✅ **Rechtliche Seiten**
- Impressum
- Datenschutzerklärung
- Allgemeine Geschäftsbedingungen
- Versandinformationen

## Anforderungen 📋

- Python 3.11+
- PostgreSQL (für Render.com)
- pip/venv

## Installation & Setup 🚀

### 1. Lokale Installation

```bash
# Repository klonen
git clone <repository-url>
cd testshoppython

# Virtual Environment erstellen
python -m venv venv

# Virtual Environment aktivieren
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Datenbank initialisieren
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 2. Umgebungsvariablen

```bash
# .env Datei erstellen
cp .env.example .env

# .env bearbeiten (optional für lokale Entwicklung)
```

### 3. Anwendung starten

```bash
uvicorn app.main:app --reload
```

Die API ist dann verfügbar unter: `http://localhost:8000`

#### Zugang zur API Dokumentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints 📚

### Initialisierung
```
POST   /init/seed-data          # Testdaten laden
GET    /init/check-data         # Daten-Status prüfen
```

### Produkte
```
GET    /products/               # Alle Produkte abrufen
POST   /products/               # Neues Produkt erstellen
GET    /products/{id}           # Produkt abrufen
PUT    /products/{id}           # Produkt aktualisieren
DELETE /products/{id}           # Produkt löschen
GET    /products/search/        # Produkte suchen
GET    /products/categories/    # Kategorien abrufen
POST   /products/categories/    # Kategorie erstellen
```

### Benutzer
```
POST   /users/register          # Neuen Benutzer registrieren
GET    /users/profile/{id}      # Benutzerprofil abrufen
PUT    /users/profile/{id}      # Profil aktualisieren
POST   /users/addresses         # Adresse hinzufügen
GET    /users/addresses/{id}    # Benutzadressen abrufen
DELETE /users/addresses/{id}    # Adresse löschen
```

### Einkaufswagen
```
GET    /cart/{user_id}          # Warenkorb abrufen
POST   /cart/{user_id}/items    # Artikel hinzufügen
PUT    /cart/{user_id}/items/{id}  # Artikel aktualisieren
DELETE /cart/{user_id}/items/{id}  # Artikel entfernen
DELETE /cart/{user_id}/clear    # Warenkorb leeren
GET    /cart/{user_id}/total    # Warenkorbsumme
```

### Bestellungen
```
GET    /orders/                 # Alle Bestellungen
GET    /orders/{id}             # Bestellung abrufen
GET    /orders/user/{id}        # Benutzerbestellungen
POST   /orders/                 # Neue Bestellung
PUT    /orders/{id}             # Bestellstatus aktualisieren
DELETE /orders/{id}             # Bestellung stornieren
GET    /orders/by-number/{num}  # Nach Bestellnr. suchen
```

### Admin
```
GET    /admin/stats             # Shop-Statistiken
GET    /admin/orders/pending    # Ausstehende Bestellungen
GET    /admin/orders/revenue    # Umsatzinfo
GET    /admin/products/low-stock # Produkte mit niedrigem Bestand
GET    /admin/users/most-active # Aktivste Benutzer
GET    /admin/products/popular  # Beliebte Produkte
```

### Rechtliches
```
GET    /info/impressum          # Impressum
GET    /info/terms              # Allgemeine Geschäftsbedingungen
GET    /info/privacy            # Datenschutzerklärung
GET    /info/shipping           # Versandinformation
GET    /info/contact            # Kontaktinformation
```

## Testdaten 🧪

Nach dem Start an `/init/seed-data` aufrufen (POST), um die Datenbank mit Testdaten zu füllen:

```bash
curl -X POST http://localhost:8000/init/seed-data
```

**Testkonto - Administrator:**
- Email: `admin@owre.shop`
- Passwort: `admin123`

**Testkonto - Demo-Benutzer:**
- Email: `demo@owre.shop`
- Passwort: `demo123`

## Deployment auf Render.com 🌐

### Schritt 1: GitHub Repository

1. Code auf GitHub hochladen:
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### Schritt 2: Render.com Setup

1. [Render.com](https://render.com) Konto erstellen
2. Neuen "Web Service" anlegen
3. GitHub Repository verbinden
4. Folgende Settings einstellen:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

**Environment Variables:**
- `DATABASE_URL`: PostgreSQL connection string (Render generiert diese automatisch)
- `SECRET_KEY`: Einen sicheren Schlüssel setzen
- `ENVIRONMENT`: `production`

### Schritt 3: PostgreSQL Database

1. Im Render Dashboard eine neue PostgreSQL Datenbank erstellen
2. Diese mit dem Web Service verbinden
3. Die Umgebungsvariablen werden automatisch gesetzt

## Datenbank Schema 🗄️

```
Categories
├── Products (mit kategorie_id FK)
│   ├── OrderItems (produkt_id FK)
│   └── CartItems (produkt_id FK)
│
Users
├── Carts (user_id FK 1:1)
│   └── CartItems (cart_id FK)
├── Orders (user_id FK)
│   └── OrderItems (order_id FK)
└── Addresses (user_id FK)
```

## Entwicklung 👨‍💻

### Projektstruktur

```
app/
├── main.py              # FastAPI App
├── database.py          # DB Connection
├── models.py            # SQLAlchemy Modelle
├── schemas.py           # Pydantic Schemas
├── config.py            # Konfiguration
└── routers/
    ├── products.py      # Produkte API
    ├── users.py         # Benutzer API
    ├── cart.py          # Warenkorb API
    ├── orders.py        # Bestellungen API
    ├── admin.py         # Admin API
    ├── init.py          # Initialisierung
    └── legal.py         # Rechtliche Seiten
```

### Code Quality

```bash
# Type Checking (optional)
pip install mypy
mypy app/

# Linting (optional)
pip install flake8
flake8 app/
```

## Sicherheit 🔒

⚠️ **Wichtig für Production:**

1. **`SECRET_KEY` ändern** - einen langen, zufälligen Schlüssel verwenden
2. **CORS Origins** einschränken - nicht `["*"]` verwenden
3. **HTTPS forcieren** - in Production erforderlich
4. **Environment separieren** - `.env` Datei nicht committen
5. **Passwörter** - bcrypt-Hashing ist implementiert

## Troubleshooting 🔧

### Database Fehler
```bash
# DB reset
rm owre.db
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Dependencies Fehler
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Port bereits in Gebrauch
```bash
# Anderen Port verwenden
uvicorn app.main:app --port 8001
```

## Performance Tipps 📈

- Datenbankindizes auf häufig gefilterten Spaltne verwenden
- Paginierung für große Datenmengen implementiert
- Connection Pooling für PostgreSQL aktiviert
- CORS Middleware nur für Development auf `["*"]` setzen

## Lizenz 📄

MIT License - Frei verwendbar

## Support 📞

Bei Fragen oder Problemen:
- Render.com Dokumentation: https://render.com/docs
- FastAPI Dokumentation: https://fastapi.tiangolo.com
- SQLAlchemy Dokumentation: https://docs.sqlalchemy.org

---

**Viel Erfolg mit deinem Shop! 🚀**

- 🤔 I’m looking for help with ...
- 💬 Ask me about ...
- 📫 How to reach me: ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...
-->

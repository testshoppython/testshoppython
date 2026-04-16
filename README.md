# OWRE - Mediterranean-Scandinavian Lifestyle Shop

OWRE ist eine Premium-E-Commerce-Plattform für handgefertigte Aufbewahrungslösungen aus natürlichen Materialien. Das Projekt vereint mediterrane Wärme mit skandinavischer Schlichtheit durch ein starkes Storytelling-Konzept.

Technisch basiert der Shop auf **FastAPI**, **SQLAlchemy** und **SQLite**, mit einem modernen Frontend aus **Vanilla JS** und **CSS**.

## 🌟 Brand Philosophy: "Dein Zuhause, dein Rückzugsort"

OWRE steht für Ästhetik, Funktionalität und Wertschätzung des Handwerks. Der Shop wurde transformiert von einer reinen Verkaufsplattform zu einer Lifestyle-Marke:
*   **Storytelling:** Integration von Brand-Stories ("Vom Handwerk in dein Wohnzimmer").
*   **Materialfokus:** Hervorhebung natürlicher Materialien wie Seegras, Rattan und Baumwolle.
*   **Lifestyle-Sektionen:** "OWRE-Gefühl" und Inspirations-Blöcke auf allen Seiten.

## ✨ Haupt-Features

### 🏠 Storefront & Experience
*   **Dynamische Startseite:** Hero-Section, Brand-Story, Material-Highlights und Newsletter.
*   **"Über uns" Seite:** Detaillierte Mission und Hintergrundgeschichte der Marke.
*   **Premium Shopping Cart:** Mit Vertrauens-Elementen ("Wusstest du schon?") und Up-Selling-Vorschlägen.
*   **Inspirations-Fokus:** Storytelling-Blöcke direkt im Produkt-Grid und auf Detailseiten.
*   **Mobile Optimierung:** Vollständig responsives Premium-Design, optimiert für Touch-Bedienung.

### 🛍️ Checkout & Kunden-Dashboard
*   **Stripe Integration:** Sichere Abwicklung von Bezahlvorgängen (Kreditkarte, Apple Pay, Klarna etc.) über Stripe Checkout Sessions.
*   **Kunden-Profil (`/shop/profile`):** Übersichtliches Dashboard zur Verwaltung von Bestellungen und Sicherheitseinstellungen (Passwortänderung).
*   **PDF Rechnungen:** Vollautomatische on-the-fly Generierung stilvoller und DSGVO-konformer PDF-Rechnungen (über `fpdf2`).
*   **Brevo Newsletter:** Nahtlose API-Anbindung an Brevo, um Kunden-Abonnements asynchron im Hintergrund zu synchronisieren.

### 🛠️ Admin-Funktionen (`/shop/admin`)
*   **Produkt-Management 2.0:** Vollständiger Bild-Upload vom Computer direkt auf den Server.
*   **Dynamische Kategorien:** Automatische Auswahl aus der Datenbank statt manueller IDs.
*   **Live-Dashboard:** Statistiken zu Umsatz, Bestellungen und Nutzerzahlen in Echtzeit.
*   **Bestellverwaltung:** Übersicht über alle getätigten Käufe.

### 🔌 API & Dokumentation
*   **Swagger UI (`/docs`):** Vollständig interaktive API-Dokumentation.
*   **ReDoc (`/redoc`):** Optimierte Lese-Dokumentation (OAS 3.0.3 kompatibel).
*   **Init-API:** Schnelle Datenbank-Initialisierung mit Premium-Seed-Daten.

## 🚀 Installation & Start

### 1. Umgebung einrichten
```bash
# Repository klonen & Ordner öffnen
git clone <repository-url>
cd testshoppython

# Venv erstellen & aktivieren
python -m venv venv
# Windows:
venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt
```

### 2. Datenbank initialisieren
Bevor du startest, lege die Tabellen an und lade die OWRE-Daten:
```bash
# Tabellen erstellen
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Seed-Daten laden (nach dem Serverstart)
curl -X POST http://localhost:8000/init/seed-data
```

### 3. Anwendung starten
```bash
uvicorn app.main:app --reload
```
Der Shop ist erreichbar unter: `http://localhost:8000`

## 🔐 Zugangsdaten (Test-Modus)

*   **Administrator:** `admin@owre.shop` / `admin123`
*   **Demo-Kunde:** `demo@owre.shop` / `demo123`

## 📁 Projektstruktur

```text
app/
├── main.py              # App-Initialisierung & Doc-Routing
├── config.py            # Pfade und Umgebungsvariablen
├── models.py            # Datenbank-Modelle (SQLAlchemy)
├── schemas.py           # Datenvalidierung (Pydantic)
├── routers/             # API-Endpunkte nach Modulen (Admin, Orders, Users etc.)
static/
├── css/                 # Premium Design-System (style.css)
├── js/                  # App-Logik (app.js)
├── images/              # Statische Asset-Bilder
└── uploads/             # Hochgeladene Produktbilder
templates/               # Jinja2 Layouts (Mediterranean Theme)
```

## 🛠 Entwurf & Technik
*   **Backend:** FastAPI (Python 3.11+)
*   **Datenbank:** SQLite (Lokal) / PostgreSQL (Production)
*   **ORM:** SQLAlchemy 2.0
*   **Frontend:** Vanilla Javascript, Jinja2 Templates, Custom Modern CSS
*   **Optimierung:** ReDoc fixiert auf OAS 3.0.3 für maximale Stabilität.

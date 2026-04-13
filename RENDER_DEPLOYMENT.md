# Deployment auf Render.com - Schritt-für-Schritt Anleitung

## Vorbereitung

### 1. GitHub Repository vorbereiten
```bash
# Git initialisieren (falls nicht bereits geschehen)
git init
git add .
git commit -m "TestShopPython - Complete e-commerce API"
git branch -M main

# Remote Repository hinzufügen
git remote add origin https://github.com/YOUR_USERNAME/testshop-python.git
git push -u origin main
```

### 2. `.env` Datei vorbereiten (lokal!)
**NICHT auf GitHub committen!**

```bash
# Nur lokal: .env erstellen (ist in .gitignore)
cp .env.example .env

# In .env ändern:
SECRET_KEY=your-super-secret-key-here-min-32-characters
ENVIRONMENT=development
```

## Deployment auf Render.com

### Step 1: Render.com Account

1. Gehe zu https://render.com
2. Registriere dich oder logge dich ein
3. Verbinde deinen GitHub Account

### Step 2: Web Service erstellen

1. Dashboard → "New +" → "Web Service"
2. GitHub Repository wählen
3. Folgende Einstellungen:

**Service Details:**
- **Name**: testshop-python
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
- **Plan**: (Free für Testing, Paid für Production)

### Step 3: PostgreSQL Datenbank

1. Dashboard → "New +" → "PostgreSQL"
2. Folgende Einstellungen:
   - **Name**: testshop-db
   - **Database**: testshop
   - **User**: testshop_user
   - **Plan**: Free für Testing
3. Erstellen und **Internal URL** kopieren

### Step 4: Web Service verbinden

1. Zurück zum Web Service
2. "Environment" Tab öffnen
3. Environment Variablen hinzufügen:

```
DATABASE_URL: postgresql://testshop_user:PASSWORD@HOSTNAME:5432/testshop
ENVIRONMENT: production
SECRET_KEY: your-secret-key-min-32-chars
DEBUG: false
```

**Wichtig**: Copy-paste die `Database URL` von der PostgreSQL Service Seite!

### Step 5: Deploy konfigurieren

1. Im Web Service
2. "Redirects/Rewrites" (optional):
   ```
   Source: /docs
   Destination: /docs
   ```

3. Health Check (optional):
   ```
   Path: /health
   Check Interval: 30 seconds
   ```

4. "Create Web Service" drücken → Deployment startet!

## Nach dem Deployment

### 1. Testdaten laden

```bash
# Produktions-URL:
curl -X POST https://YOUR_SERVICE_NAME.onrender.com/init/seed-data

# Antworte sollte sein:
{
  "detail": "Database initialized successfully",
  "categories_created": 5,
  "products_created": 11,
  "admin_user": "admin@testshop.de (Password: admin123)",
  "demo_user": "demo@testshop.de (Password: demo123)"
}
```

### 2. API testen

```bash
# Health Check
curl https://YOUR_SERVICE_NAME.onrender.com/health

# API Dokumentation im Browser:
https://YOUR_SERVICE_NAME.onrender.com/docs
```

### 3. Benutzer registrieren

```bash
curl -X POST https://YOUR_SERVICE_NAME.onrender.com/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.de",
    "username": "testuser",
    "firstname": "Test",
    "lastname": "User",
    "password": "testpassword123"
  }'
```

## Umgebungs-Spezifische Konfiguration

### Datenbank-Backup

```bash
# PostgreSQL Backup erstellen
pg_dump -U testshop_user -h HOSTNAME testshop > backup.sql

# Backup zurückfahren
psql -U testshop_user -h HOSTNAME testshop < backup.sql
```

### Logs anschauen

1. Render Dashboard
2. Service auswählen
3. "Logs" Tab
4. Live Logs anschauen

### SSL/HTTPS

- Automatisch aktiviert auf *.onrender.com
- Custom Domain mit SSL möglich (siehe Render Docs)

## Troubleshooting

### Problem: "Build failed"
- Logs anschauen
- `requirements.txt` auf Fehler prüfen
- Python Version (3.11) ist korrekt?

```bash
# Lokal testen:
pip install -r requirements.txt
```

### Problem: "Internal Server Error"
- Logs auf Render anschauen
- DATABASE_URL korrekt?
- PostgreSQL Service ist mit Web Service verbunden?

```bash
# Datenbank Connection testen:
curl https://YOUR_SERVICE_NAME.onrender.com/init/check-data
```

### Problem: 502 Bad Gateway
- Service könnte abstürzen
- Logs anschauen: "CRITICAL" oder "ERROR"
- Restart versuchen

### Problem: Seed-Daten nicht verfügbar
```bash
# Seed Datei erneut aufrufen
curl -X POST https://YOUR_SERVICE_NAME.onrender.com/init/seed-data
```

## Performance & Scaling

### Memory Issues auf Free Plan?
- Free Plan: 0.5 GB RAM
- Bei Problemen auf "Pro" Plan updaten

```bash
# Speicherverbrauch im Log sichtbar
# Falls zu hoch: Render → Plan → Upgrade
```

### Datenbank Optimierung

```sql
-- Wichtige Indizes (Render PostgreSQL UI):
CREATE INDEX idx_product_category ON products(category_id);
CREATE INDEX idx_order_user ON orders(user_id);
CREATE INDEX idx_order_status ON orders(status);
CREATE INDEX idx_cart_user ON carts(user_id);
CREATE INDEX idx_cartitem_cart ON cart_items(cart_id);
```

### Auto-Restart konfigurieren

1. Service Dashboard
2. "Settings" Tab
3. "Cron Job" oder Auto-Restart aktivieren

## Domain & HTTPS

### Custom Domain (Optional)

1. Service Settings
2. "Custom Domain" hinzufügen
3. DNS Records bei Domain-Provider updaten
4. CNAME auf render.com zeigen lassen
5. Auto-SSL aktiviert sich automatisch

### HTTPS/SSL

- Standard *.onrender.com: ✅ Automatisch
- Custom Domain: ✅ Automatisch via Let's Encrypt

## Backup & Disaster Recovery

### PostgreSQL Datenbank exportieren

```bash
# Backup in Render Console:
pg_dump -U <user> -h <host> <database> > backup.sql
```

### Automatische Backups

1. Render PostgreSQL Service
2. "Backups" Tab
3. Automatische Backups sind bei Free Plan: 7 Tage Retention

## Monitoring & Alerts

### Render Monitoring

- Render Dashboard zeigt automatisch:
  - CPU Auslastung
  - Memory Usage
  - Response Times
  - Error Rates

### Custom Monitoring (Optional)

- Sentry für Error Tracking
- DataDog für detailiertes Monitoring
- Logtail für Log Aggregation

## Kosten

### Free Plan
- Web Service: Kostenlos (mit Timeout/Cold Starts)
- PostgreSQL: Kostenlos (512 MB)

### Pro Plan (Empfohlen für Production)
- Web Service: $7/Monat
- PostgreSQL: $15+/Monat
- Keine Cold Starts
- Email Support

## Checkliste vor Go-Live

- [ ] GitHub Repository erstellt und gepusht
- [ ] `.env.example` ist commitet, `.env` ist in .gitignore
- [ ] `render.yaml` ist korrekt konfiguriert
- [ ] PostgreSQL Datenbank erstellt
- [ ] Web Service erfolgreich deployed
- [ ] Environment Variablen gesetzt
- [ ] Seed-Daten geladen (`/init/seed-data`)
- [ ] Health Check funktioniert (`/health`)
- [ ] API Dokumentation erreichbar (`/docs`)
- [ ] Teste einen kompletten Kaufprozess
- [ ] Admin Stats funktioniert (`/admin/stats`)
- [ ] Logs werden korrekt angezeigt
- [ ] CORS konfiguriert (nicht `["*"]` in Production!)
- [ ] Backend URL in Frontend eingestellt
- [ ] SSL/HTTPS funktioniert

## Support & Ressourcen

- **Render Dokumentation**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

**Viel Erfolg beim Deployment! 🚀**

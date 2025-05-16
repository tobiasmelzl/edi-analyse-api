# EDI Analyse‑API

**Projektbeschreibung:**  
Diese API dient der Analyse und Auswertung von EDI/DFÜ-Transaktionen (z. B. DELFOR, DESADV, DELJIT). 
Sie stellt Metriken bereit, erlaubt die Verwaltung von Partnern, zeigt Fehlerraten, Transaktionen 
und vieles mehr – **vollständig asynchron mit FastAPI & MySQL**.

---

## Funktionen

- Authentifizierung per API-Key (oder optional JWT)
- Partnerverwaltung (Anlegen, Suchen)
- Transaktionsübersicht & Filter
- KPI-Auswertungen (Message Count, Fehler, Typen, Zeiträume)
- Statuscode-Verwaltung
- Fehlerlogging
- **Health-Check**

---

## Schnellstart (lokal)

### Voraussetzungen

- Python **3.11**
- MySQL/MariaDB mit Nutzer und leerer DB (z. B. `edi_analyzer`)
- Git

### Schritt-für-Schritt Anleitung

#### 1. Repository klonen

```bash
git clone https://github.com/tobiasmelzl/edi-analyse-api.git
cd edi-analyse-api/api
```

#### 2. Virtuelle Umgebung erstellen & aktivieren

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

#### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

#### 4. `.env` Datei erstellen

```bash
cp .env.example .env
```

> Öffne `.env` und passe die Datenbank-URL an:
>
> ```env
> DATABASE_URL=mysql+asyncmy://<nutzer>:<passwort>@localhost:3306/edi_analyzer
> API_KEY=supersecret
> JWT_SECRET=dein-geheimer-schlüssel
> ```

#### 5. Datenbankstruktur anlegen

```bash
alembic upgrade head
```

> Falls `alembic` nicht installiert ist:
> ```bash
> pip install alembic
> ```

#### 6. Server starten

```bash
uvicorn app.main:app --reload
```

API läuft unter: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Die interaktive Swagger-Dokumentation ist hier erreichbar:  
http://127.0.0.1:8000/docs

---

## Authentifizierung

### Variante 1: API Key

Sende den Header `X-API-Key` bei geschützten Routen:

```http
X-API-Key: supersecret
```

### Variante 2: JWT Token (optional)

1. Token holen:

```
POST /api/auth/token
Content-Type: application/x-www-form-urlencoded
Body:
  username=demo
  password=demo
```

2. Dann den `access_token` bei Requests mitgeben:

```http
Authorization: Bearer <dein-token>
```

---

## Tests ausführen

```bash
PYTHONPATH=./ pytest --cov=app --cov-report=term

```


---

## Beispielrouten

| Methode | Route | Beschreibung |
|--------|--------|--------------|
| GET    | `/api/health` | System-Check (ohne Auth) |
| GET    | `/api/partners?search=BMW` | Partner suchen |
| POST   | `/api/partners` | Neuen Partner anlegen |
| GET    | `/api/transactions` | Transaktionen filtern |
| GET    | `/api/kpi/partner` | KPI nach Partner-ID |
| GET    | `/api/kpi/error-rate` | Fehlerquote berechnen |

---

## Tech-Stack

| Technologie | Zweck |
|-------------|-------|
| **FastAPI** | Webframework (async, schnell) |
| **SQLAlchemy 2.0 async** | ORM für DB-Zugriffe |
| **MySQL / MariaDB** | Relationale Datenbank |
| **Pydantic** | Validierung & Serialisierung |
| **Alembic** | Datenbank-Migrationen |
| **Loguru** | Logging (inkl. Middleware) |
| **httpx + pytest** | Testing-Framework |
| **JWT (via jose)** | Authentifizierung (optional) |

---

## Tipps

- Willst du die DB direkt sehen? → Nutze z. B. **DBeaver** oder **MySQL Workbench**
- Willst du Logs sehen? → Schau in `api/logs/api.log`
- Willst du neue Daten? → Seed einfach weitere User oder Partner per POST.

---

## FAQ

**Ich bekomme beim Start einen Fehler zu `.env` oder `DATABASE_URL`.**  
→ Stelle sicher, dass `.env` existiert und korrekt konfiguriert ist.

**Was ist der Standardnutzer für JWT?**  
→ `username=demo`, `password=demo` (wird automatisch beim Start angelegt)

**Wie kann ich den API Key ändern?**  
→ In `.env` Datei ändern und Server neu starten.

**Wie mache ich einen Production-Start?**  
→ Statt `--reload` → mit Gunicorn/Uvicorn in Docker oder via `systemd` starten (siehe Deployment-Doku – nicht enthalten).

---

## Lizenz

MIT License – © 2025 Tobias Melzl

---

## Support

Hängst du irgendwo fest? Schreib mir unter:  
`tobi.melzl@gmail.com`

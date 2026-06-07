# Accessibility & Tone Rewriter

A web application that helps content teams rewrite text to target reading levels, check WCAG 2.2 AA accessibility compliance, generate image alt text, and export compliance reports.

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 + TypeScript + Vite |
| Backend | Python 3.12+ + FastAPI |
| Database | PostgreSQL 16 + SQLAlchemy 2.0 + Alembic |
| AI | Anthropic Claude |
| Readability | textstat (Flesch–Kincaid) |
| Accessibility | axe-core |
| Testing | Behave + Playwright + pytest |

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose (for PostgreSQL)

## Getting Started

### 1. Start the database

```bash
docker compose up -d
```

### 2. Set up the backend

```bash
cd server
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Start the backend server

```bash
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Set up and start the frontend

```bash
cd client
npm install
npm run dev
```

### 7. Open the app

Visit [http://localhost:5173](http://localhost:5173) in your browser.

## Running Tests

### Unit tests
```bash
pytest tests/unit
```

### Integration tests
```bash
pytest tests/integration
```

### Acceptance tests
```bash
behave tests/acceptance/features
```

## Project Structure

```
accessibility-rewriter/
├── client/              # React frontend (Vite + TypeScript)
├── server/              # FastAPI backend (Python)
├── alembic/             # Database migrations
├── tests/               # All tests (acceptance, unit, integration)
├── docker-compose.yml   # PostgreSQL container
└── .env.example         # Environment variable template
```

## Use Cases

1. RewriteTextToReadingLevel
2. MeasureReadingLevel
3. GenerateImageAltText
4. CheckDocumentAccessibility
5. FixAccessibilityViolation
6. ExplainRewriteDecision
7. CompareDocumentVersions
8. FlagTranslationRisk
9. ConfigureAccessibilityRules
10. ExportComplianceReport

## Actors

- **ContentDesigner** — Writes and rewrites content
- **AccessibilityLead** — Manages compliance and configuration
- **Translator** — Prepares content for other languages

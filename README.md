<!-- pixeltable-example-app: 20260930-museum-loans -->
# Museum Loans API built with Pixeltable

[![Built with Pixeltable](https://img.shields.io/badge/built%20with-Pixeltable-5b4bff)](https://pixeltable.com)
[![PyPI - pixeltable](https://img.shields.io/pypi/v/pixeltable?label=pixeltable)](https://pypi.org/project/pixeltable/)
[![GitHub stars](https://img.shields.io/github/stars/pixeltable/pixeltable?style=social)](https://github.com/pixeltable/pixeltable)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

Track which collection objects are out on loan, to whom, and for how long. **Objects** carry an accession number, medium, year and gallery; **loans** record the borrower, venue, status and days out. Pixeltable computes a readable loan label, an overdue flag and an urgency band, and everything is browsable without writing code: the local **Pixeltable dashboard** and the `pxt` CLI (`ls`, `describe`, `rows`, `get`, `count`, `computed`) show tables, computed columns and rows directly.

[Pixeltable](https://pixeltable.com) is open-source, Python-native **multimodal AI data infrastructure**: tables, incremental computed columns, UDFs, indexes and serving in one library, running locally or on Pixeltable Cloud.

> ⭐ **Like this example?** Star [pixeltable/pixeltable](https://github.com/pixeltable/pixeltable) on GitHub. It helps other developers find it.

## What this example shows

- **`pxt` CLI and local dashboard** for exploring tables and computed columns
- **Reads and writes**: Json columns, primary-key updates and deletes, and quick inspection with the `pxt` CLI (`pxt rows`, `pxt get`, `pxt count`)
- **Pixeltable Cloud lifecycle** from the `pxt` CLI (`db`, `schema`, `service`)
- **Incremental computed columns** powered by plain Python UDFs (`@pxt.udf`)
- **FastAPI serving**: one `FastAPIRouter` turns tables and `@pxt.query` functions into typed REST routes (insert, update, delete, compute and query) with OpenAPI docs
- **Importable UDF module**: UDFs live in `udfs.py`; tables, queries and routes live together in `app.py` (Pixeltable resolves UDFs by module path)
- **`pixeltable.toml`** declares a local database and a **Pixeltable Cloud** database, so the same code deploys with `pxt db update`

## Explore it without writing code

After seeding:

```bash
pxt ls --tree --counts                  # museum/objects, museum/loans with row counts
pxt describe museum/loans               # columns, types and computed expressions
pxt computed museum/loans               # just the computed columns
pxt rows museum/loans -n 5 --cols accession,borrower,overdue,urgency_band
pxt count museum/loans
pxt dashboard                           # opens the local web dashboard
```

The dashboard and the CLI read the same catalog as the API, so a loan created with `POST /loans` shows up immediately.

## What's inside

| File | What it is |
|------|------------|
| `app.py` | The app: tables declared as Python classes, `@pxt.query` functions, and the `FastAPIRouter` routes |
| `client_demo.py` | Register an object, lend it, age the loan and list overdue loans through the API |
| `pixeltable.toml` | Project config: the local database plus a Pixeltable Cloud database (sizing, deploy excludes) |
| `seed.py` | Seed collection objects and loans |
| `udfs.py` | Pixeltable UDFs (`@pxt.udf`) in their own importable module, imported by `app.py` |
| `requirements.txt` / `pyproject.toml` | Dependencies (`pixeltable[serve]>=0.7.14`) |

**Tables**

| Table | Stored columns | Computed columns |
|-------|---------|------------------|
| `objects` | `accession`, `title`, `medium`, `year`, `gallery` | `id`, `accession_upper`, `title_lower` |
| `loans` | `accession`, `borrower`, `venue`, `status`, `days_out`, `notes`, `curator` | `id`, `label`, `overdue`, `urgency_band` |

**API routes** (service `loans_api`)

| Method | Path | Kind | Backed by | Notes |
|--------|------|------|-----------|-------|
| `POST` | `/objects` | insert | `Objects` |  |
| `POST` | `/loans` | insert | `Loans` |  |
| `POST` | `/loans/update` | update | `Loans` |  |
| `POST` | `/urgency` | compute | `Loans` |  |
| `GET` | `/loans/overdue` | query | `overdue_loans` |  |

## Quickstart

Requires Python 3.11+ and `pixeltable[serve]>=0.7.14`.

```bash
git clone https://github.com/pierrebrunelle/pixeltable-museum-loans.git
cd pixeltable-museum-loans
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Create the tables in a local catalog directory named `museum`
pxt schema update app.py museum

python seed.py museum
pxt service run app.py museum --port 8000   # open http://localhost:8000/docs
python client_demo.py                      # in another terminal
pxt dashboard                              # browse the tables in your browser
```

Try it:

```bash
curl -s -X POST localhost:8000/urgency -H 'Content-Type: application/json' -d '{"status": "out", "days_out": 130}'
curl -s 'localhost:8000/loans/overdue?curator=okafor'
```

## Deploy to Pixeltable Cloud

The same `app.py` runs on [Pixeltable Cloud](https://pixeltable.com). Sign in (or get a free trial database with `pxt new`), point the second database entry in `pixeltable.toml` at your own database, then deploy:

```bash
pxt login                       # or: export PIXELTABLE_API_KEY=<your-api-key>
# edit pixeltable.toml: name = 'pxt://<your-org>:<your-db>'
pxt db update pxt://<your-org>:<your-db>                 # build the image and upload the project
pxt schema update app.py pxt://<your-org>:<your-db>/museum   # create the tables in the hosted database
pxt service update app.py pxt://<your-org>:<your-db>/museum  # start the API there
pxt service list pxt://<your-org>:<your-db>              # list hosted services
```

Hosted routes require an API key: send it in the `X-api-key` header (for example `-H "X-api-key: $PIXELTABLE_API_KEY"`). Keep keys in environment variables or `pxt secret set`, never in code.

## Code walkthrough

**1. Business logic is plain Python, in `udfs.py`.** A `@pxt.udf` function can be used as a column expression. Pixeltable records UDFs by module path (`udfs.is_overdue`), so they live in their own importable module rather than inline in the app: the daemon, serving workers and Pixeltable Cloud import it again by that path.

```python
# udfs.py
@pxt.udf
def is_overdue(status: str, days_out: int) -> bool:
    return days_out > LOAN_TERM_DAYS.get(status, 90)
```

**2. Tables are Python classes (`app.py`).** Annotated attributes are stored columns; attributes assigned an expression are **computed columns** (`id`, `label`, `overdue`, `urgency_band`), evaluated incrementally on every insert or update and recomputed when their inputs change.

```python
# app.py
class Loans(TableModel, name='loans'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    accession: pxt.String
    borrower: pxt.String
    venue: pxt.String
    status: pxt.String
    days_out: pxt.Int
    notes: pxt.String | None
    curator: pxt.String

    label = loan_label(accession, borrower, venue)
    overdue = is_overdue(status, days_out)
    urgency_band = urgency(status, days_out)
```

**3. Queries are functions (`app.py`).** `@pxt.query` wraps a Pixeltable query so it can be called from Python or exposed as a route:

```python
# app.py
@pxt.query
def overdue_loans(curator: str):
    """Overdue loans for one curator, most urgent first."""
    return Loans.where((Loans.curator == curator) & (Loans.overdue == True)).select(  # noqa: E712
        Loans.id, Loans.label, Loans.days_out, Loans.urgency_band
    ).order_by(Loans.days_out, asc=False)
```

**4. One router, a full REST API.** `FastAPIRouter` generates request/response models from the column types, validates input, and publishes OpenAPI docs at `/docs`:

```python
# app.py
loans_api = FastAPIRouter(name='loans_api')
loans_api.add_insert_route(Objects, path='/objects',
                           inputs=[Objects.accession, Objects.title, Objects.medium, Objects.year, Objects.gallery],
                           outputs=[Objects.id, Objects.accession_upper, Objects.title_lower])
loans_api.add_insert_route(Loans, path='/loans',
                           inputs=[Loans.accession, Loans.borrower, Loans.venue, Loans.status, Loans.days_out,
                                   Loans.notes, Loans.curator],
                           outputs=[Loans.id, Loans.label, Loans.overdue, Loans.urgency_band])
loans_api.add_update_route(Loans, path='/loans/update', inputs=[Loans.status, Loans.days_out],
                           outputs=[Loans.id, Loans.overdue, Loans.urgency_band])
loans_api.add_compute_route(Loans, path='/urgency', inputs=[Loans.status, Loans.days_out],
                            outputs=[Loans.overdue, Loans.urgency_band])
loans_api.add_query_route(path='/loans/overdue', query=overdue_loans, method='get')
```

## Learn more

- 🌐 Website: https://pixeltable.com
- 📚 Docs: https://docs.pixeltable.com
- 💻 Source: https://github.com/pixeltable/pixeltable (⭐ star it if Pixeltable is useful to you)
- 📦 PyPI: https://pypi.org/project/pixeltable/

---

<sub>Built as part of a daily series of Pixeltable example apps · Pixeltable 0.7.14 · Python, FastAPI, incremental computed columns · Licensed under Apache-2.0.</sub>

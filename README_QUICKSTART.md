# QMMX Deep Patch — Quickstart

**Date:** 2025-08-14T15:42:26.789377 UTC

## What's included
- `migrate.py` — creates/patches required tables (idempotent)
- `upgrade_monitor.py` — hardened UIM with commentary
- `routes_patch.py` — Flask Blueprint with `/health`, `/upgrade/status`, `/predictions/current`
- `start_qmmx.py` — optional launcher that runs migrations + starts engine and API

## How to apply
1. Copy these files into your project root (same folder as `app.py` and `ml_engine.py`).
2. In `app.py`, register the Blueprint:
   ```python
   from routes_patch import bp as patch_bp
   app.register_blueprint(patch_bp)
   ```
   Also ensure you call migrations once at startup:
   ```python
   import migrate; migrate.migrate()
   ```

3. In `ml_engine.py`, call migrations once at startup too:
   ```python
   import migrate; migrate.migrate()
   ```

4. Run for dev:
   ```bash
   python -m venv .venv && .venv\Scripts\activate   # mac: source .venv/bin/activate
   pip install -r requirements.txt
   python start_qmmx.py
   ```

If you prefer manual startup:
```bash
python migrate.py
python ml_engine.py
# new terminal
python app.py
```

## New endpoints
- `GET /health` → `{"ok": true}`
- `GET /upgrade/status` → latest UIM snapshot
- `GET /predictions/current?symbol=SPY` → returns recent predictions ("warming_up" until populated)

## Notes
- All schema changes are **create/patch only** (no destructive ops).
- `upgrade_score` now includes a `notes` field used by Q commentary.

"""Background sync: pushes unsynced rows to the FastAPI backend when the network allows."""
import asyncio
import httpx
from config import API_URL, SYNC_INTERVAL_SEC


async def sync_loop(app):
    while True:
        await asyncio.sleep(SYNC_INTERVAL_SEC)
        rows = app.db.unsynced()
        if not rows:
            continue
        try:
            async with httpx.AsyncClient(timeout=8) as c:
                r = await c.post(f"{API_URL}/api/sync", json={"patient": app.patient["id"], "results": rows})
            if r.status_code == 200:
                app.db.mark_synced([x["id"] for x in rows])
        except Exception:
            pass  # offline: keep rows queued, try again next tick

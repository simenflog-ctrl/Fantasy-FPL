"""
Henter alt vi trenger fra FPLs API og skriver det til data/raw/.

Kjøres av GitHub Actions. Runnerne har åpen internettilgang; skyen der Claude
kjører er blokkert fra fantasy.premierleague.com på organisasjonsnivå, så dette
steget MÅ kjøre her. Alt nedstrøms leser filene dette skrivet legger igjen.

Ingen modellogikk i denne fila. Den skal bare hente, og den skal feile høyt
hvis noe mangler, slik at vi aldri bygger en modell på halve data.
"""

from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE = "https://fantasy.premierleague.com/api"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SUMMARIES = RAW / "element_summary"

# Simens lag. Kan overstyres med miljøvariabel hvis vi noen gang vil kjøre for et annet lag.
ENTRY_ID = os.environ.get("FPL_ENTRY_ID", "7089878")

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": "fpl-model/0.1 (github actions; personal analysis)",
        "Accept": "application/json",
    }
)

MAX_WORKERS = 8          # høflig mot API-et; runneren har ikke dårlig tid
MAX_RETRIES = 4
BACKOFF_BASE = 1.6


class FetchError(RuntimeError):
    pass


def get_json(path: str, *, allow_404: bool = False) -> dict | list | None:
    """GET med backoff. Returnerer None kun ved 404 dersom det er tillatt."""
    url = f"{BASE}{path}"
    last_exc: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            resp = SESSION.get(url, timeout=30)
            if resp.status_code == 404 and allow_404:
                return None
            if resp.status_code == 429:
                # rate limit — vent lenger enn vanlig backoff
                wait = float(resp.headers.get("Retry-After", BACKOFF_BASE ** (attempt + 2)))
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # noqa: BLE001 - vi vil retry-e på alt transient
            last_exc = exc
            if attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF_BASE ** attempt)

    raise FetchError(f"Ga opp {url} etter {MAX_RETRIES} forsøk: {last_exc}")


def write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # sort_keys gir stabile diffs i git, slik at en commit viser hva som faktisk endret seg
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=1))


def fetch_core() -> dict:
    """bootstrap-static, fixtures og Simens lag."""
    print("→ bootstrap-static")
    bootstrap = get_json("/bootstrap-static/")
    write(RAW / "bootstrap.json", bootstrap)

    print("→ fixtures")
    fixtures = get_json("/fixtures/")
    write(RAW / "fixtures.json", fixtures)

    print(f"→ entry {ENTRY_ID}")
    write(RAW / "entry.json", get_json(f"/entry/{ENTRY_ID}/"))
    write(RAW / "entry_history.json", get_json(f"/entry/{ENTRY_ID}/history/"))

    current = next((e for e in bootstrap["events"] if e["is_current"]), None)
    if current:
        picks = get_json(f"/entry/{ENTRY_ID}/event/{current['id']}/picks/", allow_404=True)
        if picks:
            write(RAW / f"picks_gw{current['id']}.json", picks)

    # live-data for hver runde som er startet. Trengs til kalibrering (M9):
    # vi må kunne sammenligne prediksjon mot faktisk utfall i ettertid.
    for event in bootstrap["events"]:
        if event["finished"] or event["is_current"]:
            live = get_json(f"/event/{event['id']}/live/", allow_404=True)
            if live:
                write(RAW / f"live_gw{event['id']}.json", live)

    return bootstrap


def fetch_element_summaries(bootstrap: dict) -> None:
    """
    Per-spiller kamphistorikk. Dette er den eneste kilden til xG per kamp,
    og dermed grunnlaget for lagstyrkemodellen (M1) — FPL publiserer ikke
    xG på lagnivå noe sted.

    ~700 kall. Med 8 tråder tar det under et minutt.
    """
    elements = bootstrap["elements"]
    print(f"→ element-summary for {len(elements)} spillere")

    failures: list[tuple[int, str]] = []
    done = 0

    def one(pid: int):
        return pid, get_json(f"/element-summary/{pid}/", allow_404=True)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(one, el["id"]): el["id"] for el in elements}
        for fut in as_completed(futures):
            pid = futures[fut]
            try:
                pid, payload = fut.result()
                if payload is not None:
                    write(SUMMARIES / f"{pid}.json", payload)
            except Exception as exc:  # noqa: BLE001
                failures.append((pid, str(exc)))
            done += 1
            if done % 100 == 0:
                print(f"   {done}/{len(elements)}")

    if failures:
        # Enkelte feil er greit (nysignerte spillere kan mangle), men mange feil
        # betyr at datagrunnlaget er hullete og modellen ikke skal stole på det.
        print(f"   {len(failures)} feilet", file=sys.stderr)
        if len(failures) > len(elements) * 0.02:
            raise FetchError(
                f"For mange element-summary-feil ({len(failures)}/{len(elements)}). "
                "Avbryter heller enn å bygge modell på hullete data."
            )


def main() -> None:
    started = datetime.now(timezone.utc)
    bootstrap = fetch_core()
    fetch_element_summaries(bootstrap)

    current = next((e for e in bootstrap["events"] if e["is_current"]), None)
    nxt = next((e for e in bootstrap["events"] if e["is_next"]), None)

    write(
        ROOT / "data" / "meta.json",
        {
            "fetched_at": started.isoformat(),
            "duration_seconds": round((datetime.now(timezone.utc) - started).total_seconds(), 1),
            "entry_id": ENTRY_ID,
            "current_event": current["id"] if current else None,
            "current_event_finished": current["finished"] if current else None,
            "next_event": nxt["id"] if nxt else None,
            "next_deadline": nxt["deadline_time"] if nxt else None,
            "n_players": len(bootstrap["elements"]),
            "n_teams": len(bootstrap["teams"]),
        },
    )
    print(f"✓ ferdig på {(datetime.now(timezone.utc) - started).total_seconds():.0f}s")


if __name__ == "__main__":
    main()

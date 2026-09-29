"""IT network asset inventory and incident notes."""
from datetime import date, timedelta
import ipaddress


def init(db):
    db.executescript(
        """CREATE TABLE IF NOT EXISTS devices(
            id INTEGER PRIMARY KEY,
            hostname TEXT NOT NULL,
            ip TEXT NOT NULL UNIQUE,
            kind TEXT NOT NULL,
            owner TEXT NOT NULL,
            status TEXT NOT NULL,
            warranty_until TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT ''
        )"""
    )
    if not db.execute("SELECT COUNT(*) FROM devices").fetchone()[0]:
        db.executemany(
            "INSERT INTO devices(hostname,ip,kind,owner,status,warranty_until,notes) VALUES(?,?,?,?,?,?,?)",
            [
                ("edge-router-01", "192.168.10.1", "Router", "IT", "Online", (date.today()+timedelta(days=420)).isoformat(), "Primary gateway"),
                ("sales-printer", "192.168.10.55", "Printer", "Sales", "Watch", (date.today()+timedelta(days=60)).isoformat(), "Toner alerts"),
                ("nas-backup", "192.168.10.20", "NAS", "Ops", "Online", (date.today()+timedelta(days=250)).isoformat(), "Nightly backups"),
            ],
        )


def devices(db):
    return [dict(row) for row in db.execute("SELECT * FROM devices ORDER BY hostname")]


def handle(method, path, data, db):
    if method == "GET" and path == "/api/state":
        rows = devices(db)
        return {"devices": rows, "online": sum(1 for row in rows if row["status"] == "Online")}

    if method == "POST" and path == "/api/devices":
        hostname = str(data.get("hostname", "")).strip().lower()
        try:
            ip = str(ipaddress.ip_address(str(data.get("ip", "")).strip()))
        except ValueError as error:
            raise ValueError("Enter a valid IPv4 or IPv6 address.") from error
        if not 2 <= len(hostname) <= 80:
            raise ValueError("Enter a hostname.")
        db.execute(
            "INSERT INTO devices(hostname,ip,kind,owner,status,warranty_until,notes) VALUES(?,?,?,?,?,?,?)",
            (hostname, ip, str(data.get("kind", "Workstation")).strip(), str(data.get("owner", "")).strip() or "Unassigned", "Online", str(data.get("warranty_until", date.today().isoformat())), str(data.get("notes", "")).strip()[:500]),
        )
        return {"ok": True}

    if method == "POST" and path == "/api/status":
        status = str(data.get("status", "")).strip()
        if status not in {"Online", "Watch", "Offline"}:
            raise ValueError("Choose a listed device status.")
        row = db.execute("UPDATE devices SET status=?, notes=? WHERE id=?", (status, str(data.get("notes", "")).strip()[:500], data.get("id")))
        if not row.rowcount:
            raise LookupError()
        return {"ok": True}

    raise LookupError()

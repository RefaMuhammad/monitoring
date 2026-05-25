import streamlit as st
import requests
import time
import datetime
import os
import pytz

# ── Timezone WIB (UTC+7) ──────────────────────────────────────────────────────
WIB = pytz.timezone("Asia/Jakarta")

def now_wib():
    return datetime.datetime.now(pytz.utc).astimezone(WIB)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Uptime Monitor", page_icon="🟢", layout="wide")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif; background-color: #0a0a0f; color: #e8e8f0; }
.stApp { background: #0a0a0f; }
h1,h2,h3 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }
.monitor-header { padding: 2rem 0 1rem 0; border-bottom: 1px solid #1e1e2e; margin-bottom: 2rem; }
.monitor-title { font-family: 'Syne', sans-serif; font-size: 2.4rem; font-weight: 800; color: #e8e8f0; letter-spacing: -0.03em; margin: 0; }
.monitor-subtitle { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #5a5a7a; margin-top: 0.3rem; letter-spacing: 0.08em; text-transform: uppercase; }
.status-card { background: #13131f; border: 1px solid #1e1e2e; border-radius: 12px; padding: 1.4rem 1.6rem; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 1rem; }
.status-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
.dot-up      { background: #00e676; box-shadow: 0 0 8px #00e676aa; }
.dot-down    { background: #ff1744; box-shadow: 0 0 8px #ff1744aa; }
.dot-unknown { background: #5a5a7a; }
.site-url { font-family: 'JetBrains Mono', monospace; font-size: 0.88rem; color: #b0b0c8; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.status-label-up    { color: #00e676; font-size: 0.82rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.status-label-down  { color: #ff1744; font-size: 0.82rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.status-label-unknown { color: #5a5a7a; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; }
.response-time { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #5a5a7a; min-width: 70px; text-align: right; }
.metric-box { background: #13131f; border: 1px solid #1e1e2e; border-radius: 12px; padding: 1.2rem 1.4rem; text-align: center; }
.metric-value { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; line-height: 1; }
.metric-label { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #5a5a7a; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.4rem; }
.log-entry { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; padding: 0.35rem 0; border-bottom: 1px solid #1a1a2a; }
.countdown-bar-wrap { background: #13131f; border: 1px solid #1e1e2e; border-radius: 8px; padding: 0.8rem 1.2rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 1rem; }
.countdown-text { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #5a5a7a; white-space: nowrap; }
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input { background: #13131f !important; border: 1px solid #2e2e4e !important; border-radius: 8px !important; color: #e8e8f0 !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.88rem !important; }
.stButton > button { background: #1e1e3f !important; border: 1px solid #3a3a6a !important; border-radius: 8px !important; color: #e8e8f0 !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 0.85rem !important; transition: all 0.2s !important; }
.stButton > button:hover { background: #2a2a5a !important; border-color: #5a5a9a !important; }
hr { border-color: #1e1e2e !important; }
.stProgress > div > div > div { background: linear-gradient(90deg, #3a3aff, #00e676) !important; border-radius: 4px !important; }
div[data-testid="stProgress"] > div { background: #1e1e2e !important; border-radius: 4px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "urls" not in st.session_state:
    st.session_state.urls = ["https://www.instagram.com/gagak.kecilll?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw=="]
if "results" not in st.session_state:
    st.session_state.results = {}
if "log" not in st.session_state:
    st.session_state.log = []
if "last_check" not in st.session_state:
    st.session_state.last_check = None
if "check_interval" not in st.session_state:
    st.session_state.check_interval = 30 

LOG_FILE = "uptime_log.txt"

# ── Keyword konten tidak tersedia ─────────────────────────────────────────────
DEAD_KEYWORDS = [
    # Indonesia
    "konten ini tidak tersedia saat ini",
    "konten ini tidak tersedia",
    "konten tidak tersedia",
    "halaman tidak ditemukan",
    "maaf, halaman ini tidak tersedia",
    # English
    "this content isn't available right now",
    "this content isn't available",
    "this content is no longer available",
    "this page isn't available",
    "sorry, this page isn't available",
    "page not found",
    "content not found",
    "the link you followed may be broken",
    "this link may be broken",
    # Facebook spesifik
    "buka kabar beranda",          # muncul di halaman error FB Indonesia
    "go to news feed",             # muncul di halaman error FB English
]

# ── Helper functions ──────────────────────────────────────────────────────────
def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

import re
from urllib.parse import unquote, urlparse

_PATH_SKIP = {"share", "groups", "g", "v", "p", "watch", "reel", "videos", "permalink", "photo", "story"}

# Domain yang pakai Playwright (JS rendering, blokir datacenter IP)
SOCIAL_DOMAINS = ("facebook.com", "fb.com", "instagram.com")

def is_social_url(url: str) -> bool:
    return any(d in url for d in SOCIAL_DOMAINS)

def extract_url_id(url: str):
    parsed = urlparse(unquote(url))
    for seg in parsed.path.split("/"):
        if seg and seg.lower() not in _PATH_SKIP and len(seg) >= 6:
            return seg
    return None

def is_redirected_away(original_url: str, final_url: str):
    url_id = extract_url_id(original_url)
    if url_id:
        if url_id in unquote(final_url):
            return False, ""
        return True, f"ID '{url_id}' tidak ditemukan di URL redirect"
    orig  = urlparse(original_url)
    final = urlparse(final_url)
    orig_depth  = len([p for p in orig.path.split("/") if p])
    final_depth = len([p for p in final.path.split("/") if p])
    if orig_depth >= 2 and final_depth <= 1:
        return True, f"Redirect ke root: {final_url[:60]}"
    return False, ""

# ── Keyword konten tidak tersedia ─────────────────────────────────────────────
DEAD_KEYWORDS = [
    # ── Instagram (dari debug HTML) ───────────────────────────────────────────
    "post tidak tersedia",           # <title>Post tidak tersedia • Instagram</title>
    "tautan mungkin rusak",          # "Tautan mungkin rusak, atau profil mungkin sudah dihapus"
    "sorry, this page isn't available",   # versi english
    "the link you followed may be broken",
    "the page may have been removed",
    "page isn't available",

    # ── Facebook (dari debug sebelumnya) ──────────────────────────────────────
    "konten ini tidak tersedia saat ini",
    "konten ini tidak tersedia",
    "konten tidak tersedia",
    "buka kabar beranda",            # tombol di halaman error FB Indonesia
    "go to news feed",               # tombol di halaman error FB English
    "this content isn't available right now",
    "this content isn't available",
    "this content is no longer available",
    "this page isn't available",

    # ── Generic ───────────────────────────────────────────────────────────────
    "halaman tidak ditemukan",
    "page not found",
    "content not found",
]

# Title tag yang menandakan halaman error
DEAD_TITLES = [
    "post tidak tersedia",       # Instagram ID
    "page not found",            # Instagram/FB EN
    "content not available",
    "sorry, this page",
    "tidak tersedia",
]

def _extract_title(body: str) -> str:
    """Ekstrak isi <title> dari HTML."""
    import re
    m = re.search(r"<title[^>]*>(.*?)</title>", body, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip().lower() if m else ""

def _check_body(body: str, status_code: int, elapsed: int, resp_url: str, original_url: str) -> dict:
    """Cek body HTML untuk keyword dan redirect. Dipakai oleh requests & playwright."""
    redirected, reason = is_redirected_away(original_url, resp_url)
    if redirected:
        return {"up": False, "status_code": status_code, "response_ms": elapsed, "error": reason}

    # Cek <title> dulu — paling reliable
    title = _extract_title(body)
    for dead_title in DEAD_TITLES:
        if dead_title in title:
            return {"up": False, "status_code": status_code, "response_ms": elapsed,
                    "error": f"Konten tidak ada (title: '{title[:50]}')"}

    # Cek keyword di body
    body_lower = body.lower()
    for kw in DEAD_KEYWORDS:
        if kw in body_lower:
            return {"up": False, "status_code": status_code, "response_ms": elapsed,
                    "error": f"Konten tidak ada: '{kw[:35]}'"}

    return {"up": True, "status_code": status_code, "response_ms": elapsed, "error": None}

# ── Check via requests (non-social) ──────────────────────────────────────────
def check_url_requests(url: str) -> dict:
    try:
        import time as _time
        start   = _time.time()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8",
        }
        resp    = requests.get(url, timeout=10, allow_redirects=True, headers=headers)
        elapsed = round((_time.time() - start) * 1000)
        if resp.status_code >= 400:
            return {"up": False, "status_code": resp.status_code, "response_ms": elapsed,
                    "error": f"HTTP {resp.status_code}"}
        return _check_body(resp.text, resp.status_code, elapsed, resp.url, url)
    except requests.exceptions.ConnectionError:
        return {"up": False, "status_code": None, "response_ms": None, "error": "Connection refused"}
    except requests.exceptions.Timeout:
        return {"up": False, "status_code": None, "response_ms": None, "error": "Timeout"}
    except Exception as e:
        return {"up": False, "status_code": None, "response_ms": None, "error": str(e)[:50]}

# ── Check via Playwright (FB/IG) ──────────────────────────────────────────────
def _playwright_worker(url: str, result_holder: list):
    """
    Jalankan Playwright di thread terpisah.
    Fix Windows: set ProactorEventLoop agar asyncio bisa spawn subprocess (Chromium).
    """
    try:
        import asyncio
        import sys
        import time as _time
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

        # Windows fix: Playwright butuh ProactorEventLoop untuk spawn subprocess
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        start = _time.time()
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            ctx = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
                locale="id-ID",
                java_script_enabled=True,
            )
            page = ctx.new_page()
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(2500)  # tunggu JS render
                elapsed   = round((_time.time() - start) * 1000)
                status    = resp.status if resp else 0
                final_url = page.url
                body      = page.content()
                browser.close()
                if status >= 400:
                    result_holder.append({"up": False, "status_code": status,
                                          "response_ms": elapsed, "error": f"HTTP {status}"})
                else:
                    result_holder.append(_check_body(body, status, elapsed, final_url, url))
            except PWTimeout:
                browser.close()
                elapsed = round((_time.time() - start) * 1000)
                result_holder.append({"up": False, "status_code": None,
                                      "response_ms": elapsed, "error": "Timeout (Playwright)"})
    except ImportError:
        result_holder.append({"up": None, "status_code": None, "response_ms": None,
                              "error": "Playwright tidak terinstall: pip install playwright && playwright install chromium"})
    except Exception as e:
        import traceback
        full_tb = traceback.format_exc()
        # Tulis full traceback ke file untuk debug
        with open("playwright_error.log", "a", encoding="utf-8") as logf:
            logf.write(f"\n=== {url} ===\n")
            logf.write(full_tb)
            logf.write("\n")
        err_detail = full_tb.strip().split("\n")[-1]
        result_holder.append({"up": False, "status_code": None, "response_ms": None,
                              "error": f"Playwright error: {err_detail[:120]}"})

def check_url_playwright(url: str) -> dict:
    """Jalankan _playwright_worker di thread terpisah untuk hindari asyncio conflict di Windows."""
    import threading
    result_holder = []
    t = threading.Thread(target=_playwright_worker, args=(url, result_holder), daemon=True)
    t.start()
    t.join(timeout=35)  # maksimal tunggu 35 detik
    if result_holder:
        return result_holder[0]
    return {"up": False, "status_code": None, "response_ms": None, "error": "Thread timeout / tidak ada hasil"}

# ── Router utama ──────────────────────────────────────────────────────────────
def check_url(url: str) -> dict:
    if is_social_url(url):
        return check_url_playwright(url)
    return check_url_requests(url)

def append_log_file(entries: list):
    """Simpan log ke file TXT: datetime:url:status"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for e in entries:
            f.write(f'{e["datetime"]} WIB : {e["url"]} : {e["status"]}\n')
def run_checks():
    now = now_wib()                              # waktu WIB yang benar
    ts  = now.strftime("%Y-%m-%d %H:%M:%S")     # contoh: 2026-05-24 14:47:00

    st.session_state.last_check = now
    new_entries = []
    for url in st.session_state.urls:
        result     = check_url(url)
        status_str = "UP" if result["up"] is True else ("UNKNOWN" if result["up"] is None else "DOWN")
        entry = {
            "datetime":    ts,
            "url":         url,
            "status":      status_str,
            "response_ms": f"{result['response_ms']}ms" if result["response_ms"] else (result["error"] or "—"),
            "error":       result.get("error") or "",
        }
        new_entries.append(entry)
        st.session_state.results[url] = result
        st.session_state.log.append(entry)

    append_log_file(new_entries)
    st.session_state.log = st.session_state.log[-100:]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="monitor-header">
  <div class="monitor-title">⬡ Uptime Monitor</div>
  <div class="monitor-subtitle">Website availability checker · WIB (UTC+7) · auto-refresh</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Pengaturan")
    st.markdown("---")
    interval = st.number_input("Interval cek (menit)", min_value=1, max_value=60,
                               value=st.session_state.check_interval, step=1)
    st.session_state.check_interval = interval

    st.markdown("---")
    st.markdown("**Daftar URL**")
    urls_text = st.text_area("Satu URL per baris", value="\n".join(st.session_state.urls),
                             height=160, label_visibility="collapsed")
    if st.button("💾 Simpan URL"):
        raw = [u.strip() for u in urls_text.splitlines() if u.strip()]
        st.session_state.urls = [normalize_url(u) for u in raw]
        st.success(f"{len(st.session_state.urls)} URL disimpan")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("▶ Cek Sekarang"):
            run_checks()
            st.rerun()
    with col_b:
        if st.button("🗑 Reset Log"):
            st.session_state.log = []
            st.session_state.results = {}
            st.rerun()

    # Debug timezone — bisa dihapus setelah konfirmasi benar
    st.markdown("---")
    st.markdown(f"**🕐 Jam server sekarang:**")
    st.code(now_wib().strftime("%Y-%m-%d %H:%M:%S WIB"))

# ── Auto-refresh ──────────────────────────────────────────────────────────────
interval_seconds = st.session_state.check_interval * 60
now = now_wib()

if st.session_state.last_check is None:
    run_checks()
    st.rerun()

elapsed   = (now - st.session_state.last_check).total_seconds()
remaining = max(0, interval_seconds - elapsed)
progress  = 1.0 - (remaining / interval_seconds)

# ── Countdown ─────────────────────────────────────────────────────────────────
mins_left = int(remaining) // 60
secs_left = int(remaining) % 60
last_str  = st.session_state.last_check.strftime("%Y-%m-%d %H:%M:%S WIB")

st.markdown(f"""
<div class="countdown-bar-wrap">
  <span class="countdown-text">Last check: <b style="color:#e8e8f0">{last_str}</b></span>
  <span class="countdown-text">·</span>
  <span class="countdown-text">Next in: <b style="color:#e8e8f0">{mins_left:02d}:{secs_left:02d}</b></span>
</div>
""", unsafe_allow_html=True)
st.progress(min(progress, 1.0))

# ── Summary metrics ───────────────────────────────────────────────────────────
results    = st.session_state.results
total      = len(st.session_state.urls)
up_count   = sum(1 for r in results.values() if r.get("up"))
down_count = total - up_count
ms_vals    = [r["response_ms"] for r in results.values() if r.get("response_ms")]
avg_ms     = round(sum(ms_vals) / len(ms_vals)) if ms_vals else None

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-box"><div class="metric-value" style="color:#e8e8f0">{total}</div><div class="metric-label">Total Sites</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-box"><div class="metric-value" style="color:#00e676">{up_count}</div><div class="metric-label">Online</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-box"><div class="metric-value" style="color:#ff1744">{down_count}</div><div class="metric-label">Down</div></div>', unsafe_allow_html=True)
with c4:
    ms_display = f"{avg_ms}ms" if avg_ms else "—"
    st.markdown(f'<div class="metric-box"><div class="metric-value" style="color:#b0b0c8;font-size:1.6rem">{ms_display}</div><div class="metric-label">Avg Response</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Status cards ──────────────────────────────────────────────────────────────
st.markdown("### Status Sites")
for url in st.session_state.urls:
    r = results.get(url)
    if r is None:
        dot_cls = "dot-unknown"
        status_html = '<span class="status-label-unknown">PENDING</span>'
        detail = "—"
    elif r["up"] is None:
        dot_cls = "dot-unknown"
        status_html = '<span class="status-label-unknown">⚠ UNKNOWN</span>'
        detail = r.get("error") or "Tidak bisa dicek dari server"
    elif r["up"]:
        dot_cls = "dot-up"
        status_html = '<span class="status-label-up">● UP</span>'
        detail = f"{r['response_ms']}ms · HTTP {r['status_code']}"
    else:
        dot_cls = "dot-down"
        status_html = '<span class="status-label-down">✕ DOWN</span>'
        detail = r.get("error") or f"HTTP {r.get('status_code','—')}"

    st.markdown(f"""
    <div class="status-card">
      <div class="status-dot {dot_cls}"></div>
      <div class="site-url">{url}</div>
      {status_html}
      <div class="response-time">{detail}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Log ───────────────────────────────────────────────────────────────────────
if st.session_state.log:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander(f"📋 Log ({len(st.session_state.log)} entri)", expanded=False):
        log_lines = []
        for e in reversed(st.session_state.log):
            color = "#00e676" if e["status"] == "UP" else "#ff1744"
            log_lines.append(
                f'<div class="log-entry">'
                f'<span style="color:#5a5a7a">{e["datetime"]} WIB</span>'
                f'<span style="color:#3a3a5a"> : </span>'
                f'<span style="color:#b0b0c8">{e["url"]}</span>'
                f'<span style="color:#3a3a5a"> : </span>'
                f'<span style="color:{color};font-weight:700">{e["status"]}</span>'
                f'</div>'
            )

        st.markdown(
            '<div style="max-height:320px;overflow-y:auto;background:#0d0d18;'
            'border:1px solid #1e1e2e;border-radius:8px;padding:0.8rem 1rem;">'
            + "\n".join(log_lines) + "</div>",
            unsafe_allow_html=True,
        )

        # Download TXT
        txt_lines = []
        for e in st.session_state.log:
            txt_lines.append(f'{e["datetime"]} WIB : {e["url"]} : {e["status"]}')
        ts_now = now_wib().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="⬇ Download Log (TXT)",
            data="\n".join(txt_lines).encode("utf-8"),
            file_name=f"uptime_log_{ts_now}.txt",
            mime="text/plain",
        )

# ── Auto-rerun setiap 5 detik ─────────────────────────────────────────────────
if remaining <= 0:
    run_checks()
    st.rerun()
else:
    time.sleep(5)
    st.rerun()

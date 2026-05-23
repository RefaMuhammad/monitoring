import streamlit as st
import requests
import time
import datetime
import pandas as pd
from urllib.parse import urlparse

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Uptime Monitor",
    page_icon="🟢",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0a0a0f;
    color: #e8e8f0;
}

.stApp {
    background: #0a0a0f;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}

/* Header */
.monitor-header {
    padding: 2rem 0 1rem 0;
    border-bottom: 1px solid #1e1e2e;
    margin-bottom: 2rem;
}

.monitor-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: #e8e8f0;
    letter-spacing: -0.03em;
    margin: 0;
}

.monitor-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #5a5a7a;
    margin-top: 0.3rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Status card */
.status-card {
    background: #13131f;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: border-color 0.2s;
}

.status-card:hover { border-color: #2e2e4e; }

.status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-up   { background: #00e676; box-shadow: 0 0 8px #00e676aa; }
.dot-down { background: #ff1744; box-shadow: 0 0 8px #ff1744aa; }
.dot-unknown { background: #5a5a7a; }

.site-url {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    color: #b0b0c8;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.status-label-up   { color: #00e676; font-size: 0.82rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.status-label-down { color: #ff1744; font-size: 0.82rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.status-label-unknown { color: #5a5a7a; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; }

.response-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #5a5a7a;
    min-width: 70px;
    text-align: right;
}

/* Summary metric boxes */
.metric-box {
    background: #13131f;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
}

.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
}

.metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #5a5a7a;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.4rem;
}

/* Log table styling */
.log-entry {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    padding: 0.3rem 0;
    border-bottom: 1px solid #1a1a2a;
    color: #8888aa;
}

/* Input styling override */
div[data-testid="stTextInput"] input {
    background: #13131f !important;
    border: 1px solid #2e2e4e !important;
    border-radius: 8px !important;
    color: #e8e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
}

div[data-testid="stNumberInput"] input {
    background: #13131f !important;
    border: 1px solid #2e2e4e !important;
    border-radius: 8px !important;
    color: #e8e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Button */
.stButton > button {
    background: #1e1e3f !important;
    border: 1px solid #3a3a6a !important;
    border-radius: 8px !important;
    color: #e8e8f0 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.03em !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    background: #2a2a5a !important;
    border-color: #5a5a9a !important;
}

/* Divider */
hr { border-color: #1e1e2e !important; }

/* Countdown bar */
.countdown-bar-wrap {
    background: #13131f;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.countdown-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #5a5a7a;
    white-space: nowrap;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, #3a3aff, #00e676) !important;
    border-radius: 4px !important;
}

div[data-testid="stProgress"] > div {
    background: #1e1e2e !important;
    border-radius: 4px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "urls" not in st.session_state:
    st.session_state.urls = ["https://google.com", "https://github.com"]
if "results" not in st.session_state:
    st.session_state.results = {}
if "log" not in st.session_state:
    st.session_state.log = []
if "last_check" not in st.session_state:
    st.session_state.last_check = None
if "running" not in st.session_state:
    st.session_state.running = False
if "check_interval" not in st.session_state:
    st.session_state.check_interval = 10  # minutes

# ── Helper functions ──────────────────────────────────────────────────────────
def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def check_url(url: str) -> dict:
    try:
        start = time.time()
        resp = requests.get(url, timeout=10, allow_redirects=True)
        elapsed = round((time.time() - start) * 1000)
        is_up = resp.status_code < 400
        return {
            "up": is_up,
            "status_code": resp.status_code,
            "response_ms": elapsed,
            "error": None,
        }
    except requests.exceptions.ConnectionError:
        return {"up": False, "status_code": None, "response_ms": None, "error": "Connection refused"}
    except requests.exceptions.Timeout:
        return {"up": False, "status_code": None, "response_ms": None, "error": "Timeout"}
    except Exception as e:
        return {"up": False, "status_code": None, "response_ms": None, "error": str(e)[:40]}

def run_checks():
    now = datetime.datetime.now()
    st.session_state.last_check = now
    for url in st.session_state.urls:
        result = check_url(url)
        st.session_state.results[url] = result
        status_str = "UP" if result["up"] else "DOWN"
        ms_str = f"{result['response_ms']}ms" if result["response_ms"] else (result["error"] or "—")
        st.session_state.log.append({
            "time": now.strftime("%H:%M:%S"),
            "url": url,
            "status": status_str,
            "detail": ms_str,
        })
    # keep log to last 100 entries
    st.session_state.log = st.session_state.log[-100:]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="monitor-header">
  <div class="monitor-title">⬡ Uptime Monitor</div>
  <div class="monitor-subtitle">Website availability checker · auto-refresh every N minutes</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar: Settings ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Pengaturan")
    st.markdown("---")

    interval = st.number_input(
        "Interval cek (menit)",
        min_value=1, max_value=60,
        value=st.session_state.check_interval,
        step=1,
    )
    st.session_state.check_interval = interval

    st.markdown("---")
    st.markdown("**Daftar URL**")
    urls_text = st.text_area(
        "Satu URL per baris",
        value="\n".join(st.session_state.urls),
        height=160,
        label_visibility="collapsed",
    )
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

# ── Auto-refresh logic ────────────────────────────────────────────────────────
interval_seconds = st.session_state.check_interval * 60
now = datetime.datetime.now()

if st.session_state.last_check is None:
    # First run: check immediately
    run_checks()
    st.rerun()

elapsed_since_last = (now - st.session_state.last_check).total_seconds()
remaining = max(0, interval_seconds - elapsed_since_last)
progress_val = 1.0 - (remaining / interval_seconds)

# ── Countdown display ─────────────────────────────────────────────────────────
mins_left = int(remaining) // 60
secs_left = int(remaining) % 60
last_str = st.session_state.last_check.strftime("%H:%M:%S") if st.session_state.last_check else "—"

st.markdown(f"""
<div class="countdown-bar-wrap">
  <span class="countdown-text">Last check: {last_str}</span>
  <span class="countdown-text">·</span>
  <span class="countdown-text">Next check in: <b style="color:#e8e8f0">{mins_left:02d}:{secs_left:02d}</b></span>
</div>
""", unsafe_allow_html=True)
st.progress(min(progress_val, 1.0))

# ── Summary metrics ───────────────────────────────────────────────────────────
results = st.session_state.results
total = len(st.session_state.urls)
up_count = sum(1 for r in results.values() if r.get("up"))
down_count = sum(1 for r in results.values() if not r.get("up"))
avg_ms = None
ms_vals = [r["response_ms"] for r in results.values() if r.get("response_ms")]
if ms_vals:
    avg_ms = round(sum(ms_vals) / len(ms_vals))

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-box">
      <div class="metric-value" style="color:#e8e8f0">{total}</div>
      <div class="metric-label">Total Sites</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-box">
      <div class="metric-value" style="color:#00e676">{up_count}</div>
      <div class="metric-label">Online</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-box">
      <div class="metric-value" style="color:#ff1744">{down_count}</div>
      <div class="metric-label">Down</div>
    </div>""", unsafe_allow_html=True)
with c4:
    ms_display = f"{avg_ms}ms" if avg_ms else "—"
    st.markdown(f"""
    <div class="metric-box">
      <div class="metric-value" style="color:#b0b0c8;font-size:1.6rem">{ms_display}</div>
      <div class="metric-label">Avg Response</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Status cards ──────────────────────────────────────────────────────────────
st.markdown("### Status Sites")

for url in st.session_state.urls:
    r = results.get(url)
    if r is None:
        dot_cls = "dot-unknown"
        status_html = '<span class="status-label-unknown">PENDING</span>'
        detail = "—"
    elif r["up"]:
        dot_cls = "dot-up"
        status_html = '<span class="status-label-up">● UP</span>'
        detail = f"{r['response_ms']}ms · HTTP {r['status_code']}"
    else:
        dot_cls = "dot-down"
        status_html = '<span class="status-label-down">✕ DOWN</span>'
        detail = r["error"] or f"HTTP {r['status_code']}"

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
        log_df = pd.DataFrame(list(reversed(st.session_state.log)))
        log_df.columns = ["Waktu", "URL", "Status", "Detail"]
        st.dataframe(
            log_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn(
                    "Status",
                    width="small",
                )
            }
        )

# ── Auto-rerun logic ──────────────────────────────────────────────────────────
# Rerun every ~5 seconds to update countdown, trigger check when time is up
if remaining <= 0:
    run_checks()
    st.rerun()
else:
    # Sleep briefly then rerun to update the countdown display
    time.sleep(5)
    st.rerun()

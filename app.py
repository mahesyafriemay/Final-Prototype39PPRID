"""
Integrated DECIDE Decision Cockpit — Dynamic Demand to Production Decision System
TI4001 Proyek Rekayasa Inter-Disiplin ITB — Kelompok 39

Prototype MVP. Data simulasi (dikalibrasi dari dokumen tugas & referensi publik);
tidak terhubung ke SAP maupun sistem PT Paragon.

Jalankan:  streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title="DECIDE Decision Cockpit", page_icon="🧭", layout="wide",
                   initial_sidebar_state="expanded")

from engine import workflow_engine as wfe  # noqa: E402
from utils import state  # noqa: E402
from utils.styles import footer, inject_css, next_step_card, process_tracker  # noqa: E402
from views import (approval, demand_buffer, feasibility, monitoring, overview, priority,  # noqa: E402
                   scenario, sequencing)

RENDER = {
    "Overview": overview.render,
    "Demand & Buffer": demand_buffer.render,
    "Priority": priority.render,
    "Feasibility": feasibility.render,
    "Sequencing & ETA": sequencing.render,
    "What-if": scenario.render,
    "Decision Review": approval.render,
    "Performance": monitoring.render,
}
INITIALS = {state.PPC: "PPC", state.SUPPLY: "SP", state.LEADER: "LP"}

state.init_state()
inject_css()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="dc-brand"><div class="dc-logo">D</div><div><div class="dc-brand-t">DECIDE</div>'
                '<div class="dc-brand-s">DEMAND → PRODUCTION COCKPIT</div></div></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.selectbox("Select Role", state.ROLES, key="role")
    role = st.session_state.role
    st.markdown(f'<div class="dc-role"><div class="dc-avatar">{INITIALS[role]}</div><div>'
                f'<div class="lbl">Current Role</div><div class="val">{role}</div></div></div>', unsafe_allow_html=True)

    pages = state.allowed_pages(role)
    if st.session_state.nav not in pages:
        st.session_state.nav = "Overview"
    st.markdown("---")
    st.radio("Menu", pages, key="nav", format_func=lambda p: f"{state.PAGES[p][0]}   {p}",
             label_visibility="collapsed")
    st.markdown("---")

    wf = st.session_state.workflow
    st.markdown(
        f'<div class="dc-side-kv"><span>Siklus · Revisi</span><b>C{wf["cycle"]:02d} · Rev.{wf["revision"]:02d}</b></div>'
        f'<div class="dc-side-kv"><span>Skenario aktif</span><b>{wf["active_scenario"]}</b></div>'
        f'<div class="dc-side-kv"><span>Status</span><b>{wf["status"].replace("_", " ").title()}</b></div>'
        f'<div class="dc-side-kv"><span>Horizon produksi</span><b>16–20 Nov 2026</b></div>'
        f'<div class="dc-side-note">{state.DATA_LABEL}</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Halaman
# ---------------------------------------------------------------------------
if st.session_state.get("flash"):
    st.toast(st.session_state.pop("flash"), icon="✅")
process_tracker(state.PAGES[st.session_state.nav][0], state.tracker_stages())
_who, _what, _page = wfe.next_action(st.session_state.workflow)
next_step_card(_who, f"{_what}  ·  {wfe.label(st.session_state.workflow['status'])}",
               f"{state.PAGES[_page][0]} {_page}", _who == st.session_state.role)
RENDER[st.session_state.nav]()
footer()

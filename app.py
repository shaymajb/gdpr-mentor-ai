import streamlit as st
import plotly.graph_objects as go
from langchain_core.messages import HumanMessage, AIMessage
from core.agent import run_agent
from fpdf import FPDF
import tempfile, os
from datetime import datetime

st.set_page_config(
    page_title="GDPR Mentor",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ─── MAIN AREA: WHITE ─── */
.stApp { background: #FFFFFF !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* ─── SIDEBAR: DARK ─── */
[data-testid="stSidebar"] {
    background: #111218 !important;
    border-right: 1px solid #1E2130 !important;
}
[data-testid="stSidebar"] * { color: #9CA3AF !important; }

/* ─── HIDE CHROME ─── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ─── SIDEBAR LOGO ─── */
.sb-logo {
    padding: 22px 16px 18px;
    border-bottom: 1px solid #1E2130;
    display: flex; align-items: center; gap: 10px;
}
.sb-icon {
    width: 34px; height: 34px; border-radius: 9px;
    background: linear-gradient(135deg,#1D4ED8,#2563EB);
    display: flex; align-items: center;
    justify-content: center; font-size: 16px; flex-shrink:0;
}
.sb-name { font-size:14px; font-weight:600; color:#F9FAFB !important; letter-spacing:-.2px; }
.sb-sub  { font-size:11px; color:#374151 !important; margin-top:2px; }

/* ─── SIDEBAR SECTION ─── */
.sb-sec {
    font-size:10px; font-weight:600; letter-spacing:.1em;
    text-transform:uppercase; color:#374151 !important;
    padding:18px 16px 6px;
}

/* ─── SIDEBAR NAV BUTTONS ─── */
.stButton > button {
    background: transparent !important;
    color: #9CA3AF !important;
    border: none !important;
    border-radius: 7px !important;
    font-family: 'Inter',sans-serif !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    padding: 8px 12px !important;
    width: 100% !important;
    text-align: left !important;
    transition: all .1s !important;
}
.stButton > button:hover {
    background: #1A1D28 !important;
    color: #E5E7EB !important;
}

/* ─── DOWNLOAD BUTTON ─── */
.stDownloadButton > button {
    background: #2563EB !important; color:#fff !important;
    border:none !important; border-radius:8px !important;
    font-family:'Inter',sans-serif !important; font-size:13px !important;
    font-weight:500 !important; padding:9px 18px !important;
    margin-top:14px !important; transition: opacity .15s !important;
}
.stDownloadButton > button:hover { opacity:.88 !important; }

/* ─── TOP BAR ─── */
.topbar {
    position: sticky; top:0; z-index:100;
    background:#FFFFFF; border-bottom:1px solid #E5E7EB;
    padding:13px 40px;
    display:flex; align-items:center; justify-content:space-between;
}
.tb-title { font-size:15px; font-weight:600; color:#111827; }
.tb-right { display:flex; align-items:center; gap:12px; font-size:12px; color:#9CA3AF; }
.status-pill {
    display:inline-flex; align-items:center; gap:5px;
    background:#F0FDF4; color:#16A34A;
    border:1px solid #BBF7D0; border-radius:99px;
    padding:3px 10px; font-size:11px; font-weight:500;
}
.sdot { width:6px;height:6px;border-radius:50%;background:#16A34A;display:inline-block; }

/* ─── CHAT MESSAGES: TRANSPARENT CONTAINER ─── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 4px 40px !important;
    margin: 0 !important;
}

/* USER → RIGHT, BLUE BUBBLE */
[data-testid="stChatMessage"]:has([data-testid*="user"]) {
    flex-direction: row-reverse !important;
}
[data-testid="stChatMessage"]:has([data-testid*="user"])
[data-testid="stChatMessageContent"] {
    background: #2563EB !important;
    color: #FFFFFF !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 12px 16px !important;
    max-width: 65% !important;
    margin-left: auto !important;
    border: none !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
}
[data-testid="stChatMessage"]:has([data-testid*="user"])
[data-testid="stChatMessageContent"] p { color:#FFFFFF !important; }

/* ASSISTANT → LEFT, WHITE CARD */
[data-testid="stChatMessage"]:has([data-testid*="assistant"])
[data-testid="stChatMessageContent"] {
    background: #FFFFFF !important;
    color: #111827 !important;
    border-radius: 4px 18px 18px 18px !important;
    padding: 16px 20px !important;
    max-width: 78% !important;
    border: 1px solid #E5E7EB !important;
    font-size: 14px !important;
    line-height: 1.75 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.05) !important;
}
[data-testid="stChatMessage"]:has([data-testid*="assistant"])
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessage"]:has([data-testid*="assistant"])
[data-testid="stChatMessageContent"] li,
[data-testid="stChatMessage"]:has([data-testid*="assistant"])
[data-testid="stChatMessageContent"] strong {
    color: #111827 !important;
}

/* AVATARS */
[data-testid="stChatMessageAvatarUser"] {
    background: #DBEAFE !important; color:#1D4ED8 !important;
    border-radius:50% !important;
    font-size:13px !important; font-weight:600 !important;
    width:32px !important; height:32px !important;
    flex-shrink:0 !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
    background: linear-gradient(135deg,#1D4ED8,#2563EB) !important;
    border-radius:9px !important;
    width:32px !important; height:32px !important;
    flex-shrink:0 !important;
}

/* ─── CHAT INPUT ─── */
[data-testid="stChatInput"] {
    background: #FFFFFF !important;
    border-top: 1px solid #E5E7EB !important;
    padding: 14px 40px 18px !important;
}
[data-testid="stChatInput"] textarea {
    background: #F9FAFB !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 12px !important;
    color: #111827 !important;
    font-family:'Inter',sans-serif !important;
    font-size:14px !important;
    padding:12px 16px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,.08) !important;
    background: #fff !important; outline:none !important;
}
[data-testid="stChatInput"] textarea::placeholder { color:#9CA3AF !important; }

/* ─── EXPANDER ─── */
[data-testid="stExpander"] {
    background:#F9FAFB !important; border:1px solid #E5E7EB !important;
    border-radius:8px !important; margin-top:10px !important;
}
[data-testid="stExpander"] summary { color:#6B7280 !important; font-size:12px !important; }
[data-testid="stExpander"] p { color:#374151 !important; font-size:12px !important; }

/* ─── TOOL BADGES (light — inside white chat) ─── */
.tbadge {
    display:inline-flex; align-items:center;
    padding:3px 10px; border-radius:5px;
    font-size:10px; font-weight:600;
    letter-spacing:.07em; text-transform:uppercase;
    margin-bottom:10px;
}
.tb-search   { background:#EFF6FF; color:#1D4ED8; border:1px solid #BFDBFE; }
.tb-comply   { background:#F0FDF4; color:#15803D; border:1px solid #BBF7D0; }
.tb-risk     { background:#FFF1F2; color:#BE123C; border:1px solid #FECDD3; }
.tb-template { background:#F5F3FF; color:#6D28D9; border:1px solid #DDD6FE; }

/* ─── RISK PILL (light) ─── */
.rpill { display:inline-block;padding:3px 12px;border-radius:99px;font-size:12px;font-weight:600; }
.rp-low    { background:#F0FDF4;color:#15803D;border:1px solid #BBF7D0; }
.rp-medium { background:#FFFBEB;color:#B45309;border:1px solid #FDE68A; }
.rp-high   { background:#FFF1F2;color:#BE123C;border:1px solid #FECDD3; }

/* ─── RISK PILL (sidebar dark) ─── */
.rpill-dark { display:inline-block;padding:3px 12px;border-radius:99px;font-size:12px;font-weight:600; }
.rpd-low    { background:#063B2F;color:#34D399 !important;border:1px solid #065F46; }
.rpd-medium { background:#451A03;color:#FBBF24 !important;border:1px solid #92400E; }
.rpd-high   { background:#3B0F0F;color:#F87171 !important;border:1px solid #7F1D1D; }

/* ─── SOURCE ITEMS ─── */
.sitem { font-size:12px;color:#6B7280;padding:5px 0;border-bottom:1px solid #F3F4F6; }
.sitem:last-child { border-bottom:none; }

/* ─── SIDEBAR RISK CARD ─── */
.sb-risk {
    margin:12px 12px 4px;
    background:#1A1D28; border:1px solid #1E2130;
    border-radius:10px; padding:14px;
}
.sb-risk-lbl {
    font-size:10px; font-weight:600; letter-spacing:.08em;
    text-transform:uppercase; color:#374151 !important; margin-bottom:8px;
}

/* ─── DIVIDER ─── */
hr { border-color:#1E2130 !important; margin:10px 0 !important; }

/* ─── SPINNER ─── */
.stSpinner > div { border-top-color:#2563EB !important; }

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:#F9FAFB; }
::-webkit-scrollbar-thumb { background:#E5E7EB; border-radius:3px; }

/* ─── COLUMNS ─── */
[data-testid="stColumns"] { gap:16px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ───────────────────────────────────────────
for k, v in {
    "messages": [], "history": [],
    "last_risk_score": None, "prefill": ""
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Gauge (dark, for sidebar) ───────────────────────────────
def gauge_dark(score):
    color = "#34D399" if score<=3 else "#FBBF24" if score<=6 else "#F87171"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"font":{"size":28,"color":"#F9FAFB","family":"Inter"}},
        domain={"x":[0,1],"y":[0,1]},
        gauge={
            "axis":{"range":[0,10],"tickwidth":0,
        "tickfont":{"color":"#374151","size":9,"family":"Inter"}},
            "bar":{"color":color,"thickness":.55},
            "bgcolor":"#1A1D28","borderwidth":0,
            "steps":[
                
                    {"range":[0,3], "color":"#0F2A1F"},
                    {"range":[3,6], "color":"#2A2210"},
                    {"range":[6,10],"color":"#2D1414"},
]
            
        }
    ))
    fig.update_layout(height=150,margin=dict(l=14,r=14,t=18,b=0),
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      font={"family":"Inter"})
    return fig

# ── Gauge (light, for main area) ───────────────────────────
def gauge_light(score):
    color = "#16A34A" if score<=3 else "#B45309" if score<=6 else "#DC2626"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"font":{"size":28,"color":"#111827","family":"Inter"}},
        domain={"x":[0,1],"y":[0,1]},
        gauge={
            "axis":{"range":[0,10],"tickwidth":0,
        "tickfont":{"color":"#9CA3AF","size":9}},
            "bar":{"color":color,"thickness":.55},
            "bgcolor":"#F9FAFB","borderwidth":0,
            "steps":[
                {"range":[0,3], "color":"#F0FDF4"},
                {"range":[3,6], "color":"#FFFBEB"},
                {"range":[6,10],"color":"#FFF1F2"},
            ]
        }
    ))
    fig.update_layout(height=155,margin=dict(l=14,r=14,t=18,b=0),
                      paper_bgcolor="rgba(0,0,0,0)",
                      font={"family":"Inter"})
    return fig

# ── PDF ─────────────────────────────────────────────────────
def make_pdf(question, response, tool, score, sources):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(22,22,22)
    pdf.set_auto_page_break(True, margin=22)

    pdf.set_font("Helvetica","B",20)
    pdf.set_text_color(10,20,40)
    pdf.cell(0,12,"GDPR Compliance Report",ln=True)
    pdf.set_font("Helvetica","",9)
    pdf.set_text_color(120,130,150)
    pdf.cell(0,6,f"GDPR Mentor  ·  {datetime.now().strftime('%d %B %Y, %H:%M')}",ln=True)
    pdf.ln(4)
    pdf.set_draw_color(220,226,236)
    pdf.line(22,pdf.get_y(),188,pdf.get_y())
    pdf.ln(6)

    for heading, content in [("Analysis type", tool),("Question / Situation", question)]:
        pdf.set_font("Helvetica","B",8)
        pdf.set_text_color(100,116,140)
        pdf.cell(0,5,heading.upper(),ln=True)
        pdf.set_font("Helvetica","",10)
        pdf.set_text_color(20,32,56)
        pdf.multi_cell(0,6,content)
        pdf.ln(4)

    if score:
        level = "LOW" if score<=3 else "MEDIUM" if score<=6 else "HIGH"
        pdf.set_font("Helvetica","B",8)
        pdf.set_text_color(100,116,140)
        pdf.cell(0,5,"RISK ASSESSMENT",ln=True)
        pdf.set_font("Helvetica","",10)
        pdf.set_text_color(20,32,56)
        pdf.cell(0,6,f"Score: {score}/10   Level: {level}",ln=True)
        pdf.ln(4)

    pdf.set_font("Helvetica","B",8)
    pdf.set_text_color(100,116,140)
    pdf.cell(0,5,"ANALYSIS",ln=True)
    pdf.set_font("Helvetica","",10)
    pdf.set_text_color(20,32,56)
    pdf.multi_cell(0,6,response.encode("latin-1","replace").decode("latin-1"))
    pdf.ln(4)

    if sources:
        pdf.set_font("Helvetica","B",8)
        pdf.set_text_color(100,116,140)
        pdf.cell(0,5,"REGULATORY SOURCES",ln=True)
        pdf.set_font("Helvetica","",9)
        pdf.set_text_color(60,80,110)
        for s in sources:
            pdf.cell(0,5,f"  ·  {s}",ln=True)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name

# ── Tool map ─────────────────────────────────────────────────
TMAP = {
    "GDPR Document Search": ("tb-search",   "Regulation Search"),
    "Compliance Check":     ("tb-comply",   "Compliance Check"),
    "Risk Assessment":      ("tb-risk",     "Risk Assessment"),
    "Template Generator":   ("tb-template", "Document Template"),
}

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='sb-logo'>
        <div class='sb-icon'>🛡</div>
        <div>
            <div class='sb-name'>GDPR Mentor</div>
            <div class='sb-sub'>Compliance Intelligence</div>
        </div>
    </div>""", unsafe_allow_html=True)

    if st.session_state.last_risk_score:
        s = st.session_state.last_risk_score
        level = "LOW" if s<=3 else "MEDIUM" if s<=6 else "HIGH"
        css   = f"rpd-{'low' if s<=3 else 'medium' if s<=6 else 'high'}"
        st.markdown("<div class='sb-risk'>", unsafe_allow_html=True)
        st.markdown(f"<div class='sb-risk-lbl'>Current Risk</div>", unsafe_allow_html=True)
        st.plotly_chart(gauge_dark(s), use_container_width=True,
                        config={"displayModeBar":False})
        st.markdown(
            f"<div style='text-align:center;margin-top:-6px'>"
            f"<span class='rpill-dark {css}'>{level} — {s}/10</span></div>",
            unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<div class='sb-sec'>Quick analysis</div>", unsafe_allow_html=True)
    queries = [
        ("Data retention periods",
         "What does GDPR say about data retention periods?"),
        ("Email marketing compliance",
         "We store customer emails for 5 years. Are we compliant?"),
        ("Third-party data sharing",
         "Assess the risk of sharing employee data with a US-based HR tool"),
        ("Privacy notice template",
         "Generate a privacy notice for an e-commerce website"),
        ("Right to erasure",
         "What are our obligations when a user requests data deletion?"),
    ]
    for label, q in queries:
        if st.button(label, key=f"sb_{label[:20]}"):
            st.session_state.prefill = q

    st.divider()
    if st.button("Clear conversation", key="clear"):
        st.session_state.messages = []
        st.session_state.history  = []
        st.session_state.last_risk_score = None
        st.rerun()

# ── TOP BAR ──────────────────────────────────────────────────
st.markdown(f"""
<div class='topbar'>
    <div class='tb-title'>Compliance Analysis</div>
    <div class='tb-right'>
        <span class='status-pill'>
            <span class='sdot'></span>Active
        </span>
        <span>{datetime.now().strftime('%d %b %Y')}</span>
    </div>
</div>""", unsafe_allow_html=True)

# ── MESSAGES ─────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("tool"):
            css, label = TMAP.get(msg["tool"], ("tb-search", msg["tool"]))
            st.markdown(f'<div class="tbadge {css}">{label}</div>',
                        unsafe_allow_html=True)
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Regulatory sources"):
                for s in msg["sources"]:
                    st.markdown(f'<div class="sitem">{s}</div>',
                                unsafe_allow_html=True)

# ── INPUT ─────────────────────────────────────────────────────
prefill = st.session_state.prefill
st.session_state.prefill = ""
prompt = st.chat_input(
    "Describe a data practice, ask a compliance question, or request a template..."
) or prefill

if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                res      = run_agent(prompt, st.session_state.history)
                response = res["response"]
                tool     = res["tool_used"]
                score    = res["risk_score"]
                sources  = res["sources"]

                css, label = TMAP.get(tool, ("tb-search", tool))
                st.markdown(f'<div class="tbadge {css}">{label}</div>',
                            unsafe_allow_html=True)
                st.markdown(response)

                if sources:
                    with st.expander("Regulatory sources"):
                        for s in sources:
                            st.markdown(f'<div class="sitem">{s}</div>',
                                        unsafe_allow_html=True)

                if score:
                    st.session_state.last_risk_score = score
                    level = "LOW" if score<=3 else "MEDIUM" if score<=6 else "HIGH"
                    css_r = f"rp-{'low' if score<=3 else 'medium' if score<=6 else 'high'}"
                    c1, c2 = st.columns([1,2])
                    with c1:
                        st.plotly_chart(gauge_light(score),
                                        use_container_width=True,
                                        config={"displayModeBar":False})
                    with c2:
                        st.markdown(f"""
                        <div style='padding-top:36px'>
                            <div style='font-size:10px;color:#9CA3AF;letter-spacing:.08em;
                                        text-transform:uppercase;margin-bottom:8px'>
                                Risk level
                            </div>
                            <span class='rpill {css_r}'
                                  style='font-size:15px;padding:5px 18px'>
                                {level}
                            </span>
                            <div style='font-size:12px;color:#6B7280;margin-top:12px;line-height:1.6'>
                                Score {score}/10 — based on official GDPR documentation
                            </div>
                        </div>""", unsafe_allow_html=True)

                pdf_path = make_pdf(prompt, response, tool, score, sources)
                with open(pdf_path,"rb") as f:
                    st.download_button(
                        label="Download compliance report",
                        data=f,
                        file_name=f"gdpr_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf"
                    )

                st.session_state.history.append(HumanMessage(content=prompt))
                st.session_state.history.append(AIMessage(content=response))
                st.session_state.messages.append({
                    "role":"assistant","content":response,
                    "tool":tool,"sources":sources
                })

            except Exception as e:
                st.error(f"Analysis failed — {e}")
    st.rerun()
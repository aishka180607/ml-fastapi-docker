import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Bird Strike Prediction", page_icon="✈️", layout="centered")

# ---------- icons (simple svg so they match the colors) ----------
PLANE = """<svg viewBox="0 0 24 24" width="{s}" height="{s}"><path fill="{c}" d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></svg>"""
CLOUD = """<svg viewBox="0 0 24 24" width="{s}" height="{s}"><path fill="{c}" d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z"/></svg>"""
BIRD = """<svg viewBox="0 0 26 14" width="{s}" height="{s}"><path d="M1 7 Q7 0 13 7 Q19 0 25 7" stroke="{c}" stroke-width="2.4" fill="none" stroke-linecap="round"/></svg>"""


def icon(svg, size=20, color="#8E4A5C"):
    return svg.format(s=size, c=color)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

html, body, p, label, div, span, input, button, li {
    font-family: 'Outfit', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #FCEEF2 0%, #F6EAF6 45%, #EAF1FA 100%);
}
header[data-testid="stHeader"] {
    background: transparent;
}

/* ---------- hero ---------- */
.hero {
    position: relative;
    overflow: hidden;
    border-radius: 32px;
    padding: 52px 30px 48px 30px;
    text-align: center;
    background: linear-gradient(160deg, #F9D5DF 0%, #EBD3EE 45%, #CFE2F5 100%);
    box-shadow: 0 14px 40px rgba(201, 123, 142, 0.25);
    margin-bottom: 30px;
}
.hero-label {
    position: relative;
    z-index: 2;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 3px;
    color: #A0687B;
    margin-bottom: 10px;
}
.hero-title {
    position: relative;
    z-index: 2;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 48px;
    letter-spacing: -1px;
    line-height: 1.1;
    color: #6E3349;
}
.hero-subtitle {
    position: relative;
    z-index: 2;
    color: #8E5A6C;
    font-size: 17px;
    font-weight: 400;
    margin-top: 10px;
}

.cloud {
    position: absolute;
    background: #FFFFFF;
    border-radius: 50px;
    opacity: 0.75;
    z-index: 1;
}
.cloud::before, .cloud::after {
    content: "";
    position: absolute;
    background: #FFFFFF;
    border-radius: 50%;
}
.cloud1 { width: 110px; height: 34px; top: 26px; left: -120px; animation: drift 38s linear infinite; }
.cloud1::before { width: 50px; height: 50px; top: -24px; left: 16px; }
.cloud1::after { width: 38px; height: 38px; top: -16px; left: 56px; }
.cloud2 { width: 80px; height: 26px; top: 160px; left: -100px; animation: drift 52s linear infinite; animation-delay: -20s; }
.cloud2::before { width: 36px; height: 36px; top: -18px; left: 12px; }
.cloud2::after { width: 28px; height: 28px; top: -12px; left: 40px; }
.cloud3 { width: 95px; height: 30px; top: 100px; left: -110px; animation: drift 45s linear infinite; animation-delay: -35s; }
.cloud3::before { width: 44px; height: 44px; top: -22px; left: 14px; }
.cloud3::after { width: 32px; height: 32px; top: -14px; left: 50px; }
@keyframes drift {
    from { transform: translateX(0); }
    to { transform: translateX(900px); }
}

.plane {
    position: absolute;
    top: 12px;
    left: -60px;
    z-index: 1;
    animation: fly 16s linear infinite;
}
.plane svg {
    transform: rotate(80deg);
}
@keyframes fly {
    0% { transform: translate(0, 10px); }
    100% { transform: translate(900px, -6px); }
}

.bird {
    position: absolute;
    z-index: 1;
    animation: birdfly 10s ease-in-out infinite;
}
.bird svg {
    animation: flap 0.6s ease-in-out infinite alternate;
}
.bird1 { top: 16px; right: 80px; }
.bird2 { top: 34px; right: 48px; animation-delay: -3s; }
.bird3 { top: 12px; right: 24px; animation-delay: -6s; }
@keyframes birdfly {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(-30px, 10px); }
}
@keyframes flap {
    from { transform: scaleY(1); }
    to { transform: scaleY(0.5); }
}

/* ---------- form ---------- */
.section-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 6px;
}
.section-icon {
    width: 40px;
    height: 40px;
    border-radius: 14px;
    background: #FBE3EA;
    display: flex;
    align-items: center;
    justify-content: center;
}
.section-title {
    font-weight: 700;
    color: #6E3349;
    font-size: 21px;
    line-height: 1.1;
}
.section-sub {
    color: #A9808C;
    font-size: 13px;
}
.st-key-flight_card, .st-key-conditions_card {
    background: rgba(255, 255, 255, 0.85);
    border-radius: 26px !important;
    border: 1px solid #F2D7DE !important;
    box-shadow: 0 8px 24px rgba(201, 123, 142, 0.12);
    padding: 24px !important;
}
.stApp label p {
    color: #7A5562 !important;
    font-weight: 500;
}
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stNumberInput input {
    background: #FDF5F7 !important;
    border-radius: 14px !important;
}

/* ---------- button ---------- */
.stButton > button {
    background: linear-gradient(120deg, #F2B5C4 0%, #D99AAB 45%, #B9A3D9 100%);
    color: #FFFFFF;
    border: none;
    border-radius: 40px;
    padding: 16px 0;
    box-shadow: 0 10px 24px rgba(201, 123, 142, 0.35);
    transition: all 0.25s ease;
}
.stButton > button p {
    font-size: 19px;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 28px rgba(185, 163, 217, 0.45);
    color: #FFFFFF;
}

/* ---------- result ---------- */
.result-card {
    border-radius: 30px;
    padding: 30px 26px 26px 26px;
    text-align: center;
    margin-top: 26px;
    box-shadow: 0 12px 30px rgba(122, 59, 82, 0.12);
    animation: pop 0.5s ease;
}
@keyframes pop {
    from { opacity: 0; transform: translateY(14px) scale(0.98); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}
.result-affected {
    background: linear-gradient(150deg, #FDE7EC 0%, #F8D0DA 100%);
    border: 2px solid #EDB3C1;
}
.result-safe {
    background: linear-gradient(150deg, #EEF7F1 0%, #DCEFE4 100%);
    border: 2px solid #BCDCC7;
}
.risk-pill {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 2px;
    padding: 4px 14px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.8);
    color: #8E4A5C;
    margin-top: 4px;
}
.result-title {
    font-weight: 700;
    font-size: 30px;
    color: #5E2E40;
    margin: 8px 0 4px 0;
}
.result-text {
    color: #7A5562;
    font-size: 15px;
}
.chips {
    margin-top: 16px;
}
.chip {
    display: inline-block;
    background: rgba(255, 255, 255, 0.75);
    color: #7A5562;
    border-radius: 12px;
    padding: 5px 12px;
    margin: 3px;
    font-size: 13px;
}
.chip b {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 500;
    font-size: 11px;
    color: #A9808C;
    margin-right: 4px;
}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #F8E3EA 0%, #EDE3F4 100%);
}
.ticket {
    background: #FFFFFF;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 8px 22px rgba(201, 123, 142, 0.15);
    margin-top: 10px;
}
.ticket-head {
    background: linear-gradient(120deg, #F2B5C4 0%, #C9A9DE 100%);
    padding: 14px 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.ticket-head span {
    font-family: 'IBM Plex Mono', monospace;
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 3px;
}
.ticket-route {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 18px 6px 18px;
}
.code {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 24px;
    font-weight: 600;
    color: #6E3349;
    line-height: 1;
}
.code-sub {
    font-size: 11px;
    color: #A9808C;
}
.route-line {
    flex: 1;
    margin: 0 10px;
    border-top: 2px dashed #E7C3CE;
    position: relative;
    height: 0;
}
.route-line svg {
    position: absolute;
    top: -10px;
    left: 50%;
    margin-left: -9px;
    transform: rotate(90deg);
}
.ticket-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px 10px;
    padding: 12px 18px 16px 18px;
}
.field-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 1.5px;
    color: #B8919D;
}
.field-value {
    font-size: 15px;
    font-weight: 600;
    color: #5E2E40;
}

.steps-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 3px;
    color: #A0687B;
    margin: 28px 0 12px 4px;
}
.step {
    display: flex;
    gap: 12px;
    position: relative;
    padding-bottom: 18px;
}
.step:not(:last-child)::before {
    content: "";
    position: absolute;
    left: 15px;
    top: 32px;
    bottom: 0;
    border-left: 2px dashed #E3BFCB;
}
.step-num {
    min-width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #FFFFFF;
    color: #8E4A5C;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 3px 10px rgba(201, 123, 142, 0.2);
}
.step-text b {
    display: block;
    color: #5E2E40;
    font-size: 14px;
    font-weight: 600;
}
.step-text span {
    color: #9A7380;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)


def show_html(html):
    # remove line breaks, otherwise markdown can show part of html as code
    st.markdown(" ".join(line.strip() for line in html.splitlines()), unsafe_allow_html=True)


def get_model_version():
    try:
        import mlflow
        from mlflow import MlflowClient
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        versions = MlflowClient().search_model_versions("name='bird-strike-model'")
        return max(int(v.version) for v in versions)
    except Exception:
        return None


def risk_gauge(percent, color):
    # half circle gauge, length of the arc is about 251
    filled = 251 * percent / 100
    return f"""
    <svg width="220" height="130" viewBox="0 0 220 130">
        <path d="M 30 115 A 80 80 0 0 1 190 115" stroke="#FFFFFF" stroke-width="18" fill="none" stroke-linecap="round"/>
        <path d="M 30 115 A 80 80 0 0 1 190 115" stroke="{color}" stroke-width="18" fill="none" stroke-linecap="round"
              stroke-dasharray="{filled} 251"/>
        <text x="110" y="102" text-anchor="middle" font-family="Outfit, sans-serif" font-size="40" font-weight="700" fill="#6E3349">{percent}%</text>
        <text x="110" y="124" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="11" letter-spacing="1" fill="#A9808C">RISK OF EFFECT</text>
    </svg>
    """


def section_head(svg, title, subtitle):
    show_html(f"""
    <div class='section-head'>
        <div class='section-icon'>{icon(svg, 22)}</div>
        <div>
            <div class='section-title'>{title}</div>
            <div class='section-sub'>{subtitle}</div>
        </div>
    </div>
    """)


# ---------- sidebar: model boarding pass ----------
with st.sidebar:
    version = get_model_version()
    version_text = f"v{version}" if version else "-"

    show_html(f"""
    <div class='ticket'>
        <div class='ticket-head'>
            <span>MODEL PASS</span>
            {icon(PLANE, 20, "#FFFFFF")}
        </div>
        <div class='ticket-route'>
            <div><div class='code'>FAA</div><div class='code-sub'>strike data</div></div>
            <div class='route-line'>{icon(PLANE, 18, "#D99AAB")}</div>
            <div style='text-align:right'><div class='code'>RISK</div><div class='code-sub'>prediction</div></div>
        </div>
        <div class='ticket-grid'>
            <div><div class='field-label'>MODEL</div><div class='field-value'>Gradient Boosting</div></div>
            <div><div class='field-label'>VERSION</div><div class='field-value'>{version_text}</div></div>
            <div><div class='field-label'>F1 SCORE</div><div class='field-value'>0.49</div></div>
            <div><div class='field-label'>RECALL</div><div class='field-value'>0.78</div></div>
            <div><div class='field-label'>REPORTS</div><div class='field-value'>13 584</div></div>
            <div><div class='field-label'>FEATURES</div><div class='field-value'>8</div></div>
        </div>
    </div>

    <div class='steps-title'>HOW IT WORKS</div>
    <div class='step'>
        <div class='step-num'>1</div>
        <div class='step-text'><b>Describe the flight</b><span>height, speed, phase, sky, birds</span></div>
    </div>
    <div class='step'>
        <div class='step-num'>2</div>
        <div class='step-text'><b>Request to FastAPI</b><span>Streamlit sends data to /predict</span></div>
    </div>
    <div class='step'>
        <div class='step-num'>3</div>
        <div class='step-text'><b>Model prediction</b><span>Gradient Boosting from MLflow</span></div>
    </div>
    <div class='step'>
        <div class='step-num'>4</div>
        <div class='step-text'><b>See the risk</b><span>probability that the flight is affected</span></div>
    </div>
    """)

# ---------- hero ----------
show_html(f"""
<div class='hero'>
    <div class='cloud cloud1'></div>
    <div class='cloud cloud2'></div>
    <div class='cloud cloud3'></div>
    <div class='plane'>{icon(PLANE, 30, "#B9849A")}</div>
    <div class='bird bird1'>{icon(BIRD, 26, "#8E5A6C")}</div>
    <div class='bird bird2'>{icon(BIRD, 22, "#8E5A6C")}</div>
    <div class='bird bird3'>{icon(BIRD, 26, "#8E5A6C")}</div>
    <div class='hero-label'>AVIATION SAFETY &nbsp; ML MODEL</div>
    <div class='hero-title'>Bird Strike Prediction</div>
    <div class='hero-subtitle'>Will a bird strike affect the flight? Describe the situation and check the risk</div>
</div>
""")

# ---------- form ----------
with st.container(border=True, key="flight_card"):
    section_head(PLANE, "Flight details", "Where was the aircraft when the strike happened?")
    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input("Height (feet)", min_value=0, max_value=35000, value=500, step=100)
        ac_mass = st.selectbox("Aircraft mass class", [1, 2, 3, 4, 5], index=3,
                               help="1 - smallest aircraft, 5 - largest aircraft")
    with col2:
        speed = st.number_input("Speed (knots)", min_value=0, max_value=400, value=140, step=10)
        num_engs = st.selectbox("Number of engines", [1, 2, 3, 4], index=1)
    phase_of_flt = st.selectbox("Phase of flight", ["Take-off run", "Climb", "En Route", "Descent",
                                                    "Approach", "Landing Roll", "Taxi", "Parked"])

with st.container(border=True, key="conditions_card"):
    section_head(CLOUD, "Sky & birds", "What were the conditions outside?")
    col3, col4 = st.columns(2)
    with col3:
        time_of_day = st.selectbox("Time of day", ["Day", "Night", "Dawn", "Dusk"])
    with col4:
        sky = st.selectbox("Sky", ["No Cloud", "Some Cloud", "Overcast"])
    birds_struck = st.select_slider("Birds struck", options=["1", "2-10", "11-100", "Over 100"], value="11-100")

st.write("")

# ---------- prediction ----------
if st.button("Check the flight", width="stretch"):
    data = {
        "height": height,
        "speed": speed,
        "ac_mass": ac_mass,
        "num_engs": num_engs,
        "phase_of_flt": phase_of_flt,
        "time_of_day": time_of_day,
        "sky": sky,
        "birds_struck": birds_struck
    }

    try:
        result = requests.post(API_URL + "/predict", json=data).json()
        percent = round(result["probability"] * 100)

        if result["prediction"] == 1:
            card_class = "result-affected"
            color = "#E595A9"
            pill = "HIGH RISK"
            title = "Flight affected"
            text = "The model thinks this strike will affect the flight, for example a precautionary landing or aborted take-off."
        else:
            card_class = "result-safe"
            color = "#8CC7A1"
            pill = "LOW RISK"
            title = "Flight not affected"
            text = "The model thinks the flight will continue normally after this strike."

        show_html(f"""
        <div class='result-card {card_class}'>
            {risk_gauge(percent, color)}
            <div><span class='risk-pill'>{pill}</span></div>
            <div class='result-title'>{title}</div>
            <div class='result-text'>{text}</div>
            <div class='chips'>
                <span class='chip'><b>PHASE</b>{phase_of_flt}</span>
                <span class='chip'><b>HEIGHT</b>{height} ft</span>
                <span class='chip'><b>SPEED</b>{speed} kn</span>
                <span class='chip'><b>TIME</b>{time_of_day}</span>
                <span class='chip'><b>SKY</b>{sky}</span>
                <span class='chip'><b>BIRDS</b>{birds_struck}</span>
            </div>
        </div>
        """)

    except requests.exceptions.ConnectionError:
        st.warning("API is not running. Start it with: uvicorn main:app --reload")

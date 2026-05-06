import streamlit as st
import random
import plotly.graph_objects as go
from datetime import datetime
from streamlit_agraph import agraph, Node, Edge, Config

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURARE PAGINĂ & STILURI CSS
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Arhitectură Zigbee",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: #080c14; color: #e2e8f0; }

.main-header { background: linear-gradient(135deg, #0d1526 0%, #111827 100%); border: 1px solid #1e3a5f; border-radius: 16px; padding: 22px 28px; margin-bottom: 28px; }
.main-title { font-size: 2rem; font-weight: 800; color: #38bdf8; letter-spacing: -1px; }
.main-sub { color: #4b6080; font-size: 0.85rem; margin-top: 4px; }
.sec-hdr { font-size: 0.68rem; font-weight: 700; letter-spacing: 2px; color: #2563eb; text-transform: uppercase; margin-bottom: 10px; padding-bottom: 6px; border-bottom: 1px solid #1e2d45; }

/* Cards & Badges */
.dev-card { background: #0d1526; border: 1px solid #1e2d45; border-radius: 14px; padding: 14px 18px; margin-bottom: 8px; transition: all 0.3s ease;}
.dev-card:hover { transform: translateY(-2px); border-color: #4b6080; }
.dev-card.on { border-color: #38bdf8; box-shadow: 0 0 18px #38bdf812; }
.dev-card.off { opacity: 0.65; }
.dev-card.orphaned { border-color: #dc2626; box-shadow: 0 0 18px #dc262612; }
.dev-name { font-size: 1rem; font-weight: 700; color: #e2e8f0; }
.dev-meta { font-size: 0.75rem; color: #4b6080; margin-top: 5px; font-family: 'JetBrains Mono', monospace; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 0.68rem; font-weight: 700; margin-left: 5px; vertical-align: middle; }
.b-coord { background: #1d4ed8; color: #bfdbfe; }
.b-router { background: #065f46; color: #6ee7b7; }
.b-end { background: #4c1d95; color: #ddd6fe; }
.b-on { background: #164e63; color: #67e8f9; }
.b-off { background: #1e2d45; color: #475569; }
.b-orphan { background: #dc2626; color: #fecaca; }

/* Terminal Logs & Packets */
.log-wrap { background: #060a10; border: 1px solid #1e2d45; border-radius: 12px; padding: 12px 14px; height: 200px; overflow-y: auto; font-family: 'JetBrains Mono', monospace; font-size: 0.73rem; }
.log-line { padding: 2px 0; border-bottom: 1px solid #0a0f1a; }
.log-ts { color: #2563eb; } .log-msg { color: #94a3b8; }
.pkt { display: flex; align-items: center; gap: 8px; background: #0d1526; border-radius: 8px; padding: 6px 12px; margin-bottom: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; }
.pkt-ts { color: #2563eb; min-width: 52px; } .pkt-src { color: #38bdf8; } .pkt-dst { color: #34d399; } .pkt-cmd { color: #f59e0b; font-weight: 700; min-width: 110px; } .pkt-pay { color: #475569; } .arrow { color: #334155; }

/* Info Boxes & Protocol Blocks */
.info-box { background: #0d1526; border-left: 4px solid #38bdf8; padding: 16px; border-radius: 4px; margin-bottom: 16px; }
.info-box h4 { margin-top: 0; color: #e2e8f0; }
.proto-block { padding: 10px 15px; border-radius: 8px; text-align: center; font-weight: bold; color: white; display: inline-block; width: 100%; margin-bottom: 5px; cursor: pointer; transition: 0.2s;}
.proto-block:hover { filter: brightness(1.2); }
.pb-mac { background: #475569; } .pb-nwk { background: #2563eb; } .pb-aps { background: #9333ea; } .pb-zcl { background: #16a34a; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE & HELPERS
# ══════════════════════════════════════════════════════════════════════════════
if "slide" not in st.session_state: st.session_state.slide = 1
if "devices" not in st.session_state: st.session_state.devices = {
    "coordinator": {"name": "Coordinator", "type": "coordinator", "icon": "📡", "addr": "0x0000", "on": True,
                    "parent": None}}
if "log" not in st.session_state: st.session_state.log = []
if "packets" not in st.session_state: st.session_state.packets = []
if "counter" not in st.session_state: st.session_state.counter = 1


def next_slide(): st.session_state.slide += 1


def prev_slide(): st.session_state.slide -= 1


TEMPLATES = {
    "💡 Bec Smart": {"type": "end", "icon": "💡", "attrs": {"luminozitate": "100%", "culoare": "alb cald"}, "on": False},
    "🌡️ Senzor Temperatură": {"type": "end", "icon": "🌡️", "attrs": {"temp": None, "umid": None}, "on": True},
    "🔌 Priză Smart": {"type": "end", "icon": "🔌", "attrs": {"putere": "0W"}, "on": False},
    "🚪 Senzor Ușă": {"type": "end", "icon": "🚪", "attrs": {"status": "închis"}, "on": True},
    "🔁 Router Zigbee": {"type": "router", "icon": "🔁", "attrs": {}, "on": True},
}


def rand_addr(): return f"0x{random.randint(0x1000, 0xFFFE):04X}"


def now(): return datetime.now().strftime("%H:%M:%S")


def add_log(msg):
    st.session_state.log.append((now(), msg))
    if len(st.session_state.log) > 100: st.session_state.log.pop(0)


def add_pkt(src, dst, cmd, pay=""):
    st.session_state.packets.insert(0, {"ts": now(), "src": src, "dst": dst, "cmd": cmd, "pay": pay})
    if len(st.session_state.packets) > 30: st.session_state.packets.pop()


def find_best_parent(dev_key, dev_type=None):
    devs = st.session_state.devices
    if dev_type is None: dev_type = devs.get(dev_key, {}).get("type", "end")
    if dev_type == "router": return "coordinator"
    active_routers = [k for k, v in devs.items() if v["type"] == "router" and v.get("on", True)]
    return active_routers[0] if active_routers else "coordinator"


def rejoin_network(dev_key):
    devs = st.session_state.devices
    d = devs[dev_key]
    old_parent = d.get("parent")
    new_parent = find_best_parent(dev_key)
    if new_parent != old_parent:
        d["parent"] = new_parent
        add_log(f"🔄 {d['icon']} {d['name']} → rejoin prin {devs[new_parent]['name']}")
        add_pkt(d["addr"], devs[new_parent]["addr"], "REJOIN_REQ", "")
        add_pkt(devs[new_parent]["addr"], d["addr"], "REJOIN_RSP", "status=OK")


def check_orphans():
    devs = st.session_state.devices
    for key, d in devs.items():
        if key == "coordinator" or not d.get("on", True): continue
        parent_key = d.get("parent")
        if not parent_key or parent_key not in devs or not devs[parent_key].get("on", True):
            rejoin_network(key)


def toggle(key):
    d = st.session_state.devices[key]
    d["on"] = not d["on"]
    s = "ON ✅" if d["on"] else "OFF ❌"
    add_log(f"{d['icon']} {d['name']} → {s}")
    add_pkt(d["addr"], "0x0000", "REPORT_ATTR", f"on_off={int(d['on'])}")
    if d["on"] and d["type"] != "coordinator":
        parent = find_best_parent(key)
        d["parent"] = parent
        add_pkt(d["addr"], "0x0000", "DEV_ANNOUNCE", f"parent={parent}")
    if not d["on"] and d["type"] == "router": check_orphans()


def read_sensor(key):
    d = st.session_state.devices[key]
    a = d.get("attrs", {})
    if "temp" in a:
        a["temp"] = f"{random.uniform(18.0, 27.0):.1f}°C"
        a["umid"] = f"{random.randint(35, 75)}%"
        add_log(f"🌡️ {d['name']} → {a['temp']} / {a['umid']}")
        add_pkt(d["addr"], "0x0000", "SENSOR_RPT", f"temp={a['temp']} hum={a['umid']}")
    elif "status" in a and d["icon"] == "🚪":
        a["status"] = random.choice(["deschis 🟡", "închis 🟢"])
        add_log(f"🚪 {d['name']} → {a['status']}")
        add_pkt(d["addr"], "0x0000", "ZONE_STATUS", f"state={a['status']}")


def render_agraph_topology():
    devs = st.session_state.devices
    nodes, edges = [], []
    COLORS = {"coordinator": "#38bdf8", "router": "#34d399", "end": "#a78bfa"}
    for key, d in devs.items():
        is_on = d.get("on", True)
        node_color = COLORS.get(d["type"], "#ffffff") if is_on else "#1e2d45"
        border_color = node_color if is_on else "#dc2626"
        size = 30 if d["type"] == "coordinator" else (22 if d["type"] == "router" else 15)
        nodes.append(Node(id=key, label=f"{d['icon']} {d['name'][:12]}", size=size,
                          color={"background": node_color, "border": border_color}, font={"color": "#e2e8f0"}))
        if key != "coordinator" and is_on:
            parent_key = d.get("parent")
            if parent_key and parent_key in devs and devs[parent_key].get("on", True):
                edges.append(Edge(source=parent_key, target=key, color="#4b6080", dashes=True))
    config = Config(width="100%", height=400, directed=True, physics=True,
                    interaction={"hover": True, "dragNodes": True})
    return agraph(nodes=nodes, edges=edges, config=config)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR - NAVIGARE
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📊 Navigare Prezentare")
    st.progress(st.session_state.slide / 4)

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Înapoi", on_click=prev_slide, disabled=st.session_state.slide == 1, use_container_width=True)
    with col2:
        st.button("Înainte ➡️", on_click=next_slide, disabled=st.session_state.slide == 4, use_container_width=True)

    st.divider()

    if st.session_state.slide == 4:
        st.markdown('<div class="sec-hdr">➕ Adaugă Device Live</div>', unsafe_allow_html=True)
        dev_type = st.selectbox("Tip device", list(TEMPLATES.keys()), label_visibility="collapsed")
        dev_name = st.text_input("Nume", placeholder="ex: Bec living", label_visibility="collapsed")

        if st.button("🔗 Conectează la rețea", use_container_width=True, type="primary"):
            if dev_name.strip():
                tpl = TEMPLATES[dev_type]
                key = f"dev_{st.session_state.counter}"
                st.session_state.counter += 1
                addr = rand_addr()
                parent_key = find_best_parent(key, dev_type=tpl["type"]) if tpl["on"] else None
                st.session_state.devices[key] = {
                    "name": dev_name.strip(), "type": tpl["type"], "icon": tpl["icon"], "addr": addr, "on": tpl["on"],
                    "attrs": dict(tpl["attrs"]), "parent": parent_key
                }
                add_log(f"🔗 {tpl['icon']} '{dev_name}' conectat ({addr})")
                if tpl["on"]:
                    parent_addr = st.session_state.devices[parent_key]["addr"]
                    add_pkt("0x0000", addr, "PERMIT_JOIN", "dur=60s")
                    add_pkt(addr, parent_addr, "ASSOC_REQ", "")
                    add_pkt(parent_addr, addr, "ASSOC_RSP", "status=OK")
                    add_pkt(addr, "0x0000", "DEV_ANNOUNCE", f"parent={parent_key}")
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1: STIVA DE PROTOCOALE (DEEP DIVE)
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.slide == 1:
    st.markdown("""
    <div class="main-header">
      <span class="main-title">⚡ Arhitectura și Stiva de Protocoale Zigbee</span>
      <div class="main-sub">Diferența dintre IEEE 802.15.4 și Zigbee Alliance</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.5], gap="large")
    with col1:
        st.markdown("### Modelul Stratificat")
        st.write(
            "Deseori confundăm tehnologia radio de bază cu protocolul software. Selectează un strat pentru a vedea ce protocoale guvernează fiecare nivel.")
        strat = st.radio("Selectează nivelul:",
                         ["🌐 Nivel Aplicație (ZCL)", "🔀 Nivel Rețea (NWK)", "📡 Nivel MAC (802.15.4)",
                          "🔌 Nivel Fizic (PHY)"], label_visibility="collapsed")

    with col2:
        if "ZCL" in strat:
            st.markdown("""
            <div class="info-box">
            <h4>🌐 Nivelul Aplicație - Zigbee Cluster Library (ZCL)</h4>
            Acesta este „limbajul” comun pe care îl vorbesc device-urile. Definit de <b>CSA (fostă Zigbee Alliance)</b>.
            <ul>
                <li><b>Endpoint-uri (1-240):</b> Un dispozitiv fizic poate avea mai multe funcții logice (ex. o priză dublă are 2 endpoint-uri).</li>
                <li><b>Clustere:</b> Pachete standardizate de funcții. De exemplu: <i>Cluster 0x0006</i> înseamnă întotdeauna On/Off. <i>Cluster 0x0402</i> este Temperature Measurement.</li>
                <li>Acest strat face ca un bec Philips Hue să fie compatibil nativ cu un senzor de mișcare Ikea Tradfri.</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        elif "NWK" in strat:
            st.markdown("""
            <div class="info-box">
            <h4>🔀 Nivelul de Rețea (NWK) - Zigbee PRO</h4>
            Creierul topologiei Mesh, definit tot de <b>Zigbee Alliance</b>.
            <ul>
                <li><b>Adresare pe scurt:</b> Alocă Adresele de Rețea de 16-bit (ex. <code>0x1A2B</code>) pentru a minimiza mărimea pachetelor. Coordonatorul este mereu <code>0x0000</code>.</li>
                <li><b>Rutare dinamică:</b> Găsește calea optimă de la A la B folosind algoritmul AODV.</li>
                <li><b>Securitate Nativă:</b> Criptează tot payload-ul folosind algoritmul <b>AES-128</b> și cheia rețelei (Network Key).</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        elif "MAC" in strat:
            st.markdown("""
            <div class="info-box">
            <h4>📡 Nivelul MAC - IEEE 802.15.4</h4>
            Standardul hardware de bază. Nu știe ce este "Zigbee", doar mută biți.
            <ul>
                <li><b>Adresare Absolută:</b> Folosește adrese MAC unice global de 64-bit.</li>
                <li><b>Acces la mediu (CSMA/CA):</b> Înainte de a emite un semnal radio, ascultă canalul. Dacă e ocupat (de Wi-Fi de ex.), așteaptă o fracțiune de secundă.</li>
                <li>Gestionează PAN ID-ul (ex. 0x1A2B) și confirmările la nivel radio (Acknowledge).</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
            <h4>🔌 Nivelul Fizic (PHY) - IEEE 802.15.4</h4>
            Fizica pură a undelor electromagnetice.
            <ul>
                <li><b>Frecvență:</b> Operează predominant în banda de <b>2.4 GHz</b> (Global).</li>
                <li><b>Canale:</b> Împarte banda în 16 canale (de la 11 la 26), fiecare de 2 MHz, poziționate strategic între canalele de Wi-Fi pentru a reduce interferențele.</li>
                <li><b>Modulație:</b> DSSS (Direct Sequence Spread Spectrum) cu O-QPSK - extrem de rezistent la zgomot radio, ideal pentru senzori cu putere de emisie mică.</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2: TOPOLOGIE & DISSECȚIE PACHET
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.slide == 2:
    st.markdown("""
    <div class="main-header">
      <span class="main-title">🎭 Dispozitive și Anatomia unui Pachet Zigbee</span>
    </div>
    """, unsafe_allow_html=True)

    t1, t2 = st.tabs(["1️⃣ Roluri Logice (Topologie)", "2️⃣ Disecție Pachet de Date"])

    with t1:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                "<div class='dev-card'><h3 style='color:#38bdf8;margin-top:0'>📡 Coordinator (ZC)</h3>Startul rețelei. Inițiază PAN-ul pe canalul ales. Adresă fixă <code>0x0000</code>. Trebuie să fie mereu alimentat. Există doar UNUL per rețea.</div>",
                unsafe_allow_html=True)
        with c2:
            st.markdown(
                "<div class='dev-card'><h3 style='color:#34d399;margin-top:0'>🔁 Router (ZR)</h3>Extinde rețeaua. Repetă semnale și permite asocieri secundare. Exemple: Prize, Becuri sau dispozitive alimentate la 220V. Formează 'Mesh-ul'.</div>",
                unsafe_allow_html=True)
        with c3:
            st.markdown(
                "<div class='dev-card'><h3 style='color:#a78bfa;margin-top:0'>🌡️ End Device (ZED)</h3>Dispozitiv pe baterie (Senzori). Nu rutează nimic. Intră în 'Deep Sleep' pentru luni/ani. Vorbește doar cu Routerul său Părinte.</div>",
                unsafe_allow_html=True)

    with t2:
        st.write("Ce se trimite de fapt prin aer (pe banda de 2.4 GHz) când un senzor raportează temperatura?")
        st.markdown("""
        <div style="display:flex; gap:10px; margin-bottom: 20px;">
            <div style="flex: 2" class="proto-block pb-mac">MAC Header<br><span style="font-size:0.7em;font-weight:normal">802.15.4 (PAN ID, Src/Dst 64-bit)</span></div>
            <div style="flex: 2" class="proto-block pb-nwk">NWK Header<br><span style="font-size:0.7em;font-weight:normal">Ruta Mesh (Adrese 16-bit)</span></div>
            <div style="flex: 1" class="proto-block pb-aps">APS<br><span style="font-size:0.7em;font-weight:normal">Endpoint</span></div>
            <div style="flex: 3" class="proto-block pb-zcl">ZCL Payload (Encrypted)<br><span style="font-size:0.7em;font-weight:normal">Ex: REPORT_ATTR temp=22.5°C</span></div>
            <div style="flex: 1" class="proto-block pb-mac">FCS<br><span style="font-size:0.7em;font-weight:normal">Checksum</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.info(
            "💡 **De reținut:** Doar secțiunile APS și ZCL sunt complet criptate cu Network Key (AES-128). Header-ele MAC și NWK sunt trimise în clar pentru a permite dirijarea corectă a pachetului prin nodurile intermediare.")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3: RUTARE & SECURITATE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.slide == 3:
    st.markdown("""
    <div class="main-header">
      <span class="main-title">🕸️ Auto-vindecare (Self-Healing) & Securitate</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown("### Simularea rutării pas-cu-pas")
        st.write(
            "Descoperă mecanismul de Self-Healing. Ce se întâmplă când o priză (Router) este deconectată?")

        pas = st.select_slider(
            "Evoluția rețelei:",
            options=["1. Normal", "2. Pană curent", "3. REJOIN_REQ", "4. Rută refăcută"]
        )

        if pas == "1. Normal":
            st.success(
                "Senzorul trimite date (ex: `ZONE_STATUS`) Routerului său, care le trimite mai departe spre Coordonator.")
        elif pas == "2. Pană curent":
            st.error("Routerul pică. Senzorul nu primește ACK la pachet. Dispozitivul devine OFFLINE/ORPHAN.")
        elif pas == "3. REJOIN_REQ":
            st.warning(
                "Senzorul emite disperat un semnal radio de `REJOIN_REQ` (Căutare Părinte Nou). Caută pe canalul curent.")
        else:
            st.info(
                "Un alt Router din zonă prinde semnalul, îi răspunde cu `REJOIN_RSP`, iar topologia se repară invizibil pentru utilizator.")

    with col2:
        st.markdown("""
        <div class="info-box" style="height: 100%;">
        <h4>🔒 Cele 3 Chei de Securitate</h4>
        <p>Securitatea nativă garantează integritatea smart home-ului:</p>
        <ol>
            <li><b>Network Key (Cheia Rețelei):</b> Cheie unică pe 128 biți comună pentru TOT PAN-ul. Cu ea se criptează datele aplicației.</li>
            <li><b>Link Key:</b> Cheie specială creată temporar între un device nou și Coordonator pentru a-i transmite în siguranță <i>Network Key</i>-ul prima dată.</li>
            <li><b>Install Code:</b> (Zigbee 3.0) Un cod QR de pe spatele dispozitivului care forțează un Link Key extrem de sigur, eliminând vulnerabilitățile la asociere.</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4: SIMULATORUL INTERACTIV
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.slide == 4:
    devs = st.session_state.devices
    n_total = len(devs)
    n_on = sum(1 for d in devs.values() if d.get("on", True))

    st.markdown(f"""
    <div class="main-header" style="margin-bottom: 10px;">
      <span class="pulse"></span>
      <span class="main-title">⚡ Demonstrație Live: Simulator Zigbee</span>
      <div class="main-sub">IEEE 802.15.4 &nbsp;·&nbsp; PAN 0x1A2B &nbsp;·&nbsp; Canal 11 &nbsp;·&nbsp; {n_on}/{n_total} noduri online</div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([5, 4], gap="large")

    with col_left:
        st.markdown('<div class="sec-hdr">🏠 Device-uri (Baza de Date NWK)</div>', unsafe_allow_html=True)
        if len(devs) == 1: st.info("👈 Folosește Sidebar-ul pentru a adăuga Routere și Senzori!")

        for key, d in devs.items():
            is_on = d.get("on", True)
            is_orphan = False
            if d["type"] != "coordinator" and is_on:
                parent_key = d.get("parent")
                if parent_key and parent_key in devs and not devs[parent_key].get("on", True):
                    is_orphan = True

            cls = "on" if is_on and not is_orphan else ("orphaned" if is_orphan else "off")
            b_type = {"coordinator": "b-coord", "router": "b-router", "end": "b-end"}[d["type"]]
            b_lbl = {"coordinator": "Coordinator (ZC)", "router": "Router (ZR)", "end": "End Device (ZED)"}[d["type"]]
            b_st = '<span class="badge b-on">ONLINE</span>' if d["type"] == "coordinator" else (
                '<span class="badge b-orphan">ORPHAN</span>' if is_orphan else (
                    '<span class="badge b-on">ON</span>' if is_on else '<span class="badge b-off">OFF</span>'))

            attrs_html = " &nbsp;·&nbsp; ".join(
                f'<span class="dev-attr">{k}: <b>{v}</b></span>' for k, v in d.get("attrs", {}).items() if
                v is not None)
            parent_info = f" &nbsp;·&nbsp; <span class='dev-attr'>parent_nwk: <b>{devs.get(d.get('parent', '?'), {}).get('addr', '?')}</b></span>" if \
            d["type"] != "coordinator" and is_on else ""

            st.markdown(f"""
            <div class="dev-card {cls}">
              <div class="dev-name">{d['icon']} {d['name']} <span class="badge {b_type}">{b_lbl}</span>{b_st}</div>
              <div class="dev-meta">NwkAddr: <b>{d['addr']}</b>{parent_info}{"&nbsp;&nbsp;|&nbsp;&nbsp;" + attrs_html if attrs_html else ""}</div>
            </div>
            """, unsafe_allow_html=True)

            if key != "coordinator":
                btns = st.columns([1.3, 1, 0.6, 3])
                with btns[0]:
                    if st.button("🔴 Oprește (Simulează Pană)" if is_on else "🟢 Reconectează", key=f"tog_{key}",
                                 use_container_width=True): toggle(key); st.rerun()
                with btns[1]:
                    if any(x in d.get("attrs", {}) for x in ["temp", "status"]) and is_on:
                        if st.button("📊 Forțează Payload", key=f"rd_{key}", use_container_width=True): read_sensor(
                            key); st.rerun()
                with btns[2]:
                    if st.button("🗑️", key=f"del_{key}", use_container_width=True):
                        add_log(f"❌ '{d['name']}' force leave_req")
                        add_pkt(d["addr"], "0x0000", "LEAVE_REQ", "")
                        del st.session_state.devices[key]
                        check_orphans()
                        st.rerun()

    with col_right:
        st.markdown('<div class="sec-hdr">🗺️ Harta Topologiei (Renderizare Agraph)</div>', unsafe_allow_html=True)
        render_agraph_topology()

        st.markdown('<div class="sec-hdr">📦 Packet Sniffer (Log Pachete 802.15.4)</div>', unsafe_allow_html=True)
        pkts = st.session_state.packets
        if pkts:
            html = "".join(
                f'<div class="pkt"><span class="pkt-ts">{p["ts"]}</span><span class="pkt-src">{p["src"]}</span><span class="arrow">→</span><span class="pkt-dst">{p["dst"]}</span><span class="pkt-cmd">{p["cmd"]}</span><span class="pkt-pay">{p["pay"]}</span></div>'
                for p in pkts[:8])
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.caption("Așteptare pachete de la Nivelul MAC...")

        st.markdown('<div class="sec-hdr" style="margin-top:14px">📋 Jurnal Evenimente Consolă</div>',
                    unsafe_allow_html=True)
        log_html = "".join(
            f'<div class="log-line"><span class="log-ts">[{t}]</span> <span class="log-msg">{m}</span></div>' for t, m
            in reversed(st.session_state.log[-25:]))
        st.markdown(
            f'<div class="log-wrap">{log_html or "<span style=\'color:#1e3a5f\'>Niciun eveniment de sistem...</span>"}</div>',
            unsafe_allow_html=True)
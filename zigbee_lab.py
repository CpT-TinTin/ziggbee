import streamlit as st
import random
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG + CSS
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Zigbee Lab – Wireshark",
    page_icon="🦈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: #080c14; color: #e2e8f0; }

/* ─── Header ─── */
.main-header { background: linear-gradient(135deg,#0d1526 0%,#111827 100%); border:1px solid #1e3a5f; border-radius:16px; padding:18px 26px; margin-bottom:20px; }
.main-title  { font-size:1.8rem; font-weight:800; color:#38bdf8; letter-spacing:-1px; }
.main-sub    { color:#4b6080; font-size:0.82rem; margin-top:4px; }
.sec-hdr     { font-size:0.66rem; font-weight:700; letter-spacing:2px; color:#2563eb; text-transform:uppercase; margin-bottom:8px; padding-bottom:5px; border-bottom:1px solid #1e2d45; }

/* ─── Device cards ─── */
.dev-card { background:#0d1526; border:1px solid #1e2d45; border-radius:12px; padding:12px 16px; margin-bottom:6px; }
.dev-card.on  { border-color:#38bdf8; }
.dev-card.off { opacity:.65; }
.dev-card.orphaned { border-color:#dc2626; }
.dev-name { font-size:.95rem; font-weight:700; color:#e2e8f0; }
.dev-meta { font-size:.72rem; color:#4b6080; margin-top:4px; font-family:'JetBrains Mono',monospace; }
.badge { display:inline-block; padding:2px 7px; border-radius:20px; font-size:.66rem; font-weight:700; margin-left:5px; vertical-align:middle; }
.b-coord { background:#1d4ed8; color:#bfdbfe; }
.b-router { background:#065f46; color:#6ee7b7; }
.b-end   { background:#4c1d95; color:#ddd6fe; }
.b-on    { background:#164e63; color:#67e8f9; }
.b-off   { background:#1e2d45; color:#475569; }
.b-orphan{ background:#dc2626; color:#fecaca; }

/* ─── Wireshark Packet List ─── */
.ws-table { width:100%; border-collapse:collapse; font-family:'JetBrains Mono',monospace; font-size:.72rem; }
.ws-table thead th { background:#0d1526; color:#4b6080; text-align:left; padding:5px 8px; border-bottom:1px solid #1e2d45; font-size:.65rem; letter-spacing:1px; text-transform:uppercase; }
.ws-table tbody tr { border-bottom:1px solid #0a0f1a; cursor:pointer; }
.ws-table tbody tr:hover { background:#0d2040; }
.ws-table tbody tr.selected { background:#1e3a5f; }
.ws-table td { padding:4px 8px; }
.ws-td-no  { color:#4b6080; }
.ws-td-ts  { color:#2563eb; }
.ws-td-src { color:#38bdf8; }
.ws-td-dst { color:#34d399; }
.ws-td-pro-ZCL { color:#f59e0b; font-weight:700; }
.ws-td-pro-NWK { color:#8b5cf6; font-weight:700; }
.ws-td-pro-MAC { color:#94a3b8; font-weight:700; }
.ws-td-info { color:#64748b; }

/* ─── Protocol Tree ─── */
.tree-root { font-family:'JetBrains Mono',monospace; font-size:.73rem; }
.tree-layer { border:1px solid; border-radius:8px; padding:8px 12px; margin-bottom:6px; }
.tree-mac  { border-color:#475569; background:#0c1420; }
.tree-nwk  { border-color:#3730a3; background:#0e0f30; }
.tree-aps  { border-color:#7e22ce; background:#130e28; }
.tree-zcl  { border-color:#15803d; background:#0a1a10; }
.tree-hdr  { font-weight:700; color:#e2e8f0; font-size:.78rem; margin-bottom:4px; }
.tree-field { display:flex; gap:8px; padding:2px 0; }
.tree-key  { color:#60a5fa; min-width:160px; }
.tree-val  { color:#e2e8f0; }
.tree-desc { color:#4b6080; font-style:italic; }

/* ─── Hex View ─── */
.hex-wrap  { font-family:'JetBrains Mono',monospace; font-size:.7rem; background:#060a10; border:1px solid #1e2d45; border-radius:10px; padding:12px 14px; }
.hex-offset { color:#334155; margin-right:12px; }
.hex-b-mac { color:#60a5fa; }
.hex-b-nwk { color:#a78bfa; }
.hex-b-aps { color:#34d399; }
.hex-b-zcl { color:#fbbf24; }
.hex-b-pad { color:#1e2d45; }
.hex-legend { display:flex; gap:14px; margin-bottom:8px; font-size:.68rem; }
.hl-mac  { color:#60a5fa; font-weight:700; }
.hl-nwk  { color:#a78bfa; font-weight:700; }
.hl-aps  { color:#34d399; font-weight:700; }
.hl-zcl  { color:#fbbf24; font-weight:700; }

/* ─── Info box ─── */
.info-box { background:#0d1526; border-left:4px solid #38bdf8; padding:14px; border-radius:4px; margin-bottom:14px; }
.info-box h4 { margin-top:0; color:#e2e8f0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "mode"         not in st.session_state: st.session_state.mode         = "📚 Teorie"
if "chapter"      not in st.session_state: st.session_state.chapter      = 0
if "seq"          not in st.session_state: st.session_state.seq          = 1
if "pan_id"       not in st.session_state: st.session_state.pan_id       = "0x1A2B"
if "channel"      not in st.session_state: st.session_state.channel      = 11
if "pkt_selected" not in st.session_state: st.session_state.pkt_selected = 0
if "devices"      not in st.session_state: st.session_state.devices      = {
    "coordinator": {"name": "Coordinator", "type": "coordinator", "icon": "📡",
                    "addr": "0x0000", "on": True, "parent": None, "attrs": {}}}
if "log"          not in st.session_state: st.session_state.log          = []
if "packets"      not in st.session_state: st.session_state.packets      = []
if "counter"      not in st.session_state: st.session_state.counter      = 1

# ══════════════════════════════════════════════════════════════════════════════
# ACADEMIC DATA: CHAPTERS, GLOSSARY, REFERENCES
# ══════════════════════════════════════════════════════════════════════════════
CHAPTERS = [
    {
        "title": "1. Arhitectura Zigbee & Stiva de Protocoale",
        "content": """
Zigbee este un standard de comunicație wireless pentru rețele cu consum redus de energie și rată mică de transfer.
Stiva de protocoale Zigbee este împărțită în **4 straturi principale**:

| Strat | Standard | Rol principal |
|---|---|---|
| **PHY** | IEEE 802.15.4 | Transmisie radio pe 2.4 GHz (canale 11–26) |
| **MAC** | IEEE 802.15.4 | Acces la mediu (CSMA/CA), adresare 64-bit, ACK |
| **NWK** | Zigbee Alliance | Rutare Mesh, adresare 16-bit, securitate |
| **APS + ZCL** | Zigbee Alliance (CSA) | Endpoint-uri, Clustere, Atribute, Comenzi |

Diferența esențială: **IEEE 802.15.4** definește **hardware-ul radio** (PHY+MAC), iar **Zigbee Alliance (CSA)**
construiește deasupra lui un protocol software interoperabil (NWK/APS/ZCL).
""",
        "notes": """
- Zigbee Pro (Zigbee 2007) adaugă suport pentru rețele mari (>64k noduri), routing îmbunătățit.
- Zigbee 3.0 (2016) unifică toate profilurile aplicative (HA, ZLL, etc.) într-un singur standard.
- CSA (Connectivity Standards Alliance) este denumirea actuală a Zigbee Alliance (redenumit 2021).
- IEEE 802.15.4 este standardul radio pentru și Z-Wave (cu unele variante), Thread, 6LoWPAN.
""",
        "glossary": {
            "PHY": "Physical Layer – nivelul fizic radio (2.4 GHz, DSSS, O-QPSK)",
            "MAC": "Medium Access Control – controlul accesului la mediu (CSMA/CA, ACK)",
            "NWK": "Network Layer – rutare Mesh, adresare scurtă de 16-bit",
            "APS": "Application Support Sub-layer – endpoints, binding, grupuri",
            "ZCL": "Zigbee Cluster Library – clusters standardizate (On/Off, Temperature, etc.)",
            "PAN": "Personal Area Network – rețeaua Zigbee identificată printr-un PAN ID de 16-bit",
            "CSA": "Connectivity Standards Alliance – organizația care standardizează Zigbee",
        },
        "example_cmd": ("ASSOC_REQ", "0x1234", "0x0000", "cap=FFD"),
        "compare": True,
    },
    {
        "title": "2. IEEE 802.15.4 – Stratul MAC",
        "content": """
Stratul MAC din IEEE 802.15.4 gestionează accesul la canalul radio și fiabilitatea la nivel de hop.

**Mecanisme principale:**
- **CSMA/CA** (Carrier Sense Multiple Access / Collision Avoidance): înainte de a transmite, nodu ascultă canalul;
  dacă este ocupat, așteaptă un interval aleatoriu (*backoff*).
- **Acknowledge (ACK)**: fiecare frame de date poate solicita confirmare. Dacă ACK nu vine în timp, se retransmite.
- **Adresare duală**: fiecare dispozitiv are o adresă **EUI-64** (globală, unică pe 64 biți) și o adresă
  **scurtă de 16 biți** alocată dinamic de coordinator.
- **PAN ID**: identificatorul rețelei (16 biți). Permite mai multe rețele Zigbee în aceeași zonă fără interferențe.

**Format frame MAC (simplificat):**
`[Frame Control (2B)] [Seq# (1B)] [PAN ID (2B)] [Dst Addr (2B)] [Src Addr (2B)] [Payload] [FCS (2B)]`
""",
        "notes": """
- Frame types MAC: Beacon (0x00), Data (0x01), ACK (0x02), Command (0x03).
- Super-frame structure (beacon mode) permite reglarea duty-cycle-ului pentru End Devices.
- CSMA/CA în Zigbee: max 4 retransmisii la nivel MAC, macMaxFrameRetries = 3 implicit.
- FCS (Frame Check Sequence): CRC-16 ITU-T pe tot frame-ul. Detectează erori de transmisie.
""",
        "glossary": {
            "CSMA/CA": "Carrier Sense Multiple Access / Collision Avoidance – mecanism de acces la mediu",
            "EUI-64": "Extended Unique Identifier pe 64 biți – adresa MAC globală unică",
            "PAN ID": "Personal Area Network Identifier – identificatorul rețelei de 16 biți",
            "FCS": "Frame Check Sequence – CRC-16 pentru detecția erorilor",
            "ACK": "Acknowledgment – confirmare la nivel MAC pentru livrarea unui frame",
            "Backoff": "Interval de așteptare aleatoriu înainte de re-transmisie în CSMA/CA",
        },
        "example_cmd": ("ASSOC_REQ", "0x2A3B", "0x0000", ""),
        "compare": False,
    },
    {
        "title": "3. Zigbee NWK – Stratul de Rețea",
        "content": """
Stratul NWK este definit de Zigbee Alliance și operează deasupra MAC-ului IEEE 802.15.4.

**Responsabilități principale:**
- **Adresare scurtă (16-bit):** Coordonatorul alocă adrese scurte (`0x0001`–`0xFFF7`) la asociere.
  Adresa `0x0000` = Coordinator, `0xFFFF` = Broadcast all.
- **Rutare Mesh (AODV):** Algoritmul *Ad hoc On-Demand Distance Vector* descoperă dinamic rute
  optime de la sursă la destinație prin noduri intermediare (Routere).
- **Self-Healing:** Dacă un Router cade, dispozitivele copil emit `REJOIN_REQ` și se asociază
  la un alt Router disponibil. Rețeaua se repară fără intervenție umană.
- **Securitate NWK:** Payload-ul NWK poate fi criptat cu *Network Key* (AES-128, CCM* mode).

**Format frame NWK (simplificat):**
`[Frame Control (2B)] [Dst Addr (2B)] [Src Addr (2B)] [Radius (1B)] [Seq# (1B)] [Payload (criptat)]`
""",
        "notes": """
- Radius (hop count): câmpul Radius scade cu 1 la fiecare hop; când ajunge la 0, pachetul este drop-at.
  Valoarea default: nwkcMaxDepth × 2 = 10 hopuri.
- AODV în Zigbee: Route Discovery folosește RREQ (Route Request) și RREP (Route Reply) broadcasts.
- Many-to-one routing: Coordonatorul (sink) trimite periodic Route Record requests pentru a construi
  tabelele de rutare ale routerelor. Extrem de eficient în topologii concentrice.
""",
        "glossary": {
            "AODV": "Ad hoc On-Demand Distance Vector – algoritm de rutare dinamic",
            "Radius": "Câmpul NWK care limitează numărul de hopuri (hop count limiter)",
            "RREQ": "Route Request – pachet de descoperire a rutei broadcast",
            "RREP": "Route Reply – răspuns unicast la RREQ",
            "Rejoin": "Procesul prin care un dispozitiv găsește un nou părinte după pierderea legăturii",
            "NWK Seq": "Numărul de secvență NWK, incrementat per pachet (0–255, wraps)",
            "Network Key": "Cheie AES-128 partajată de toate nodurile din PAN pentru criptare NWK",
        },
        "example_cmd": ("REJOIN_REQ", "0x3C4D", "0x0000", ""),
        "compare": False,
    },
    {
        "title": "4. Zigbee APS – Application Support Sub-layer",
        "content": """
Stratul APS face legătura dintre rețea (NWK) și aplicație (ZCL). Gestionează **endpoint-urile**,
**binding-ul** și **group-urile**.

**Concepte cheie:**
- **Endpoint (1–240):** Un dispozitiv fizic poate expune mai multe funcții logice. Ex: o priză dublă
  are endpoint 1 (prize stânga) și endpoint 2 (priză dreapta), fiecare cu propriul cluster On/Off.
- **Profile ID:** Identificator al "limbajului" de aplicație. `0x0104` = Home Automation Profile.
- **Cluster ID:** Funcționalitate standardizată. `0x0006` = On/Off, `0x0402` = Temperature Measurement.
- **Binding:** O legătură persistentă src_endpoint → dst_endpoint (ex: un buton Ikea legat direct
  de un bec Philips, fără ca Coordonatorul să fie implicat în fiecare comandă).

**Format frame APS (simplificat):**
`[Frame Control (1B)] [Dst Endpoint (1B)] [Cluster ID (2B)] [Profile ID (2B)] [Src Endpoint (1B)] [ZCL Payload]`
""",
        "notes": """
- Endpoint 0 = ZDO (Zigbee Device Object) – administrare dispozitiv (join, leave, describe).
- Endpoint 255 = Broadcast to all endpoints.
- APS ACK: confirmarea la nivel APS garantează livrarea end-to-end (nu doar hop-by-hop ca MAC ACK).
- Fragmentation APS: pachete mari (>80 bytes payload) sunt fragmentate de APS și reasamblate la destinație.
""",
        "glossary": {
            "Endpoint": "Funcție logică (1-240) a unui dispozitiv fizic Zigbee",
            "Profile ID": "Identificator al profilului aplicativ (ex: 0x0104 Home Automation)",
            "Cluster ID": "Funcționalitate standardizată (ex: 0x0006 On/Off, 0x0402 Temperature)",
            "Binding": "Legătură persistentă endpoint→endpoint, fără medierea Coordinator-ului",
            "ZDO": "Zigbee Device Object – endpoint 0, pentru management dispozitiv",
            "APS ACK": "Confirmare end-to-end la nivel APS (diferit de MAC ACK hop-by-hop)",
            "Group": "Adresă multicast de grup Zigbee (0x0001–0xFFF7) pentru comenzi simulatane",
        },
        "example_cmd": ("REPORT_ATTR", "0x4E5F", "0x0000", "on_off=1"),
        "compare": False,
    },
    {
        "title": "5. Zigbee Cluster Library (ZCL)",
        "content": """
ZCL este **dicționarul comun** al Zigbee. Definește ce înseamnă fiecare pachet la nivel aplicativ,
asigurând interoperabilitatea între dispozitive de la diferiți producători.

**Structura ZCL:**
- **Cluster:** Grup de atribute și comenzi cu o funcție specifică (ex: `Cluster 0x0006` = On/Off).
- **Atribut:** O proprietate a cluster-ului cu tip de date și valoare (ex: `AttrID 0x0000` = *OnOff*, tip Bool).
- **Comandă:** O acțiune (ex: `Command 0x00` = *Off*, `0x01` = *On*, `0x02` = *Toggle*).

**Clustere importante (Academic):**

| Cluster ID | Nume | Utilizare |
|---|---|---|
| `0x0006` | On/Off | Becuri, prize, comutatoare |
| `0x0402` | Temperature Measurement | Senzori de temperatură |
| `0x0405` | Relative Humidity Measurement | Senzori de umiditate |
| `0x0500` | IAS Zone | Alarme, senzori de mișcare/ușă |
| `0x0000` | Basic | Informații dispozitiv (model, producător) |
| `0x0001` | Power Configuration | Nivel baterie |

**Format frame ZCL (simplificat):**
`[Frame Control (1B)] [Trans Seq (1B)] [Command ID (1B)] [Payload (variabil)]`
""",
        "notes": """
- Frame control ZCL bits: [0-1] = Frame Type (00=global, 01=cluster-specific), [2] = Manufacturer Specific,
  [3] = Direction (0=client→server, 1=server→client), [4] = Disable Default Response.
- ZCL Read Attributes Response: AttrID (2B) + Status (1B) + DataType (1B) + Value.
- ZCL Report Attributes: AttrID (2B) + DataType (1B) + Value. Trimis periodic sau la schimbare.
- ZHA (Zigbee Home Automation) vs Zigbee 3.0: 3.0 a înlocuit ZHA, ZLL, și alte profile cu un standard unificat.
""",
        "glossary": {
            "ZCL": "Zigbee Cluster Library – standard de interoperabilitate la nivel aplicație",
            "Cluster": "Grup standardizat de atribute+comenzi cu o funcție specifică",
            "Atribut": "Proprietate a unui cluster cu ID, tip de date și valoare",
            "Comandă ZCL": "Acțiune definită într-un cluster (ex: On, Off, Toggle)",
            "Trans Seq": "Transaction Sequence Number – corelează request/response ZCL",
            "Frame Type": "Tipul frame-ului ZCL: 00=global (attr), 01=specific clusterului",
            "Report Attributes": "Comandă ZCL prin care un device trimite valori curente ale atributelor",
        },
        "example_cmd": ("SENSOR_RPT", "0x5F6A", "0x0000", "temp=22.5°C hum=55%"),
        "compare": False,
    },
    {
        "title": "6. Securitate Zigbee",
        "content": """
Zigbee implementează **securitate pe mai multe niveluri** bazată pe algoritmul **AES-128 în modul CCM***.

**Cele 3 chei de securitate:**

1. **Network Key (Cheie de Rețea):**
   - Cheie AES-128 partajată de **toate nodurile** din PAN.
   - Folosită pentru criptarea payload-ului NWK+APS+ZCL.
   - Transmisă noilor dispozitive în mod **securizat** prin Link Key.

2. **Link Key (Cheie de Legătură):**
   - Cheie AES-128 **unică per pereche** de dispozitive.
   - Folosită **o singură dată** pentru a transmite Network Key-ul unui dispozitiv nou.
   - Derivată din Install Code (Zigbee 3.0) sau `ZigbeeAlliance09` (implicit – vulnerabil!).

3. **Install Code:**
   - Un cod **unic per dispozitiv**, tipărit pe carcasă (cod QR).
   - Generează un Link Key unic prin funcția hash MMO (Matyas-Meyer-Oseas).
   - Elimină vulnerabilitatea cheii `ZigbeeAlliance09` universale.

**De ce contează:** Fără Install Code, un atacator care știe cheia default `ZigbeeAlliance09`
poate intercepta schimbul de Network Key la prima asociere și decripta tot traficul rețelei.
""",
        "notes": """
- AES-128-CCM*: Counter with CBC-MAC (varianta *). Oferă atât confidențialitate cât și integritate.
- Frame Counter: câmpul Auxiliary Security Header conține un contor crescător per dispozitiv,
  previne replay attacks.
- Zigbee 3.0 mandatează Install Code pentru toate dispozitivele certificate.
- Centralized vs Distributed security model: în modelul centralizat, Coordonatorul e Trust Center.
""",
        "glossary": {
            "AES-128": "Advanced Encryption Standard cu cheie de 128 biți",
            "CCM*": "Counter with CBC-MAC mode (varianta *) – criptare + integritate simultan",
            "Network Key": "Cheie AES-128 partajată la nivel de PAN pentru criptare trafic",
            "Link Key": "Cheie AES-128 per-pereche de dispozitive, folosită pentru key transport",
            "Install Code": "Cod unic per dispozitiv (cod QR) care generează un Link Key sigur",
            "Trust Center": "Rolul Coordinator-ului de a gestiona distribuția cheilor în rețea",
            "Frame Counter": "Contor anti-replay în Auxiliary Security Header (AES)",
        },
        "example_cmd": ("PERMIT_JOIN", "0x0000", "0xFFFF", "dur=60s"),
        "compare": False,
    },
    {
        "title": "7. Topologie Mesh & Self-Healing",
        "content": """
Zigbee suportă topologiile **Star**, **Tree** și **Mesh**. Topologia **Mesh** este cea mai robustă
și cel mai des folosită în aplicații Smart Home / Industrie.

**Roluri logice:**

| Rol | Abrev. | Alimentare | Funcție |
|---|---|---|---|
| **Coordinator** | ZC | Permanentă | Inițiază PAN-ul. Adresă fixă `0x0000`. Unic per rețea. |
| **Router** | ZR | Permanentă | Extinde rețeaua. Rutează pachete. Permite asocieri copil. |
| **End Device** | ZED | Baterie | Nu rutează. Deep Sleep. Vorbește doar cu Routerul Părinte. |

**Self-Healing Mesh:**
1. End Device trimite date → Router Părinte
2. Router Părinte cade (pană curent)
3. End Device nu primește ACK → stare ORPHAN
4. End Device emite `REJOIN_REQ` pe canalul curent (beacon request)
5. Router vecin răspunde cu `REJOIN_RSP`
6. End Device adoptă noul Router ca Părinte → rețeaua e reparată **invizibil**

**Mesh Routing:** Datele pot traversa mai mulți Routeri intermediari.
Routerul A → Routerul B → Routerul C → Coordinator (max `nwkcMaxDepth × 2 = 10` hopuri).
""",
        "notes": """
- Tree topology în Zigbee: Fiecare Router poate accepta max cSkip copii (configurat la compilare).
- Mesh topology: fiecare Router menține o Routing Table și o Neighbor Table (vecini direcți).
- Association vs Orphan Scan: Association = device nou; Orphan Scan = device care și-a pierdut părintele.
- End Device Polling: End Device-urile pe baterie trebuie să "tragă" (poll) periodic date de la Router Părinte.
""",
        "glossary": {
            "ZC": "Zigbee Coordinator – inițiator PAN, adresă 0x0000",
            "ZR": "Zigbee Router – nod intermediar care rutează și extinde rețeaua",
            "ZED": "Zigbee End Device – dispozitiv pe baterie, nu rutează",
            "ORPHAN": "Starea unui device care și-a pierdut legătura cu Routerul Părinte",
            "Mesh": "Topologie de rețea cu multiple rute redundante",
            "Neighbor Table": "Tabelul unui Router cu toți vecinii săi radio direcți",
            "Routing Table": "Tabelul unui Router cu rutele cunoscute spre alte noduri",
        },
        "example_cmd": ("REJOIN_REQ", "0x7B8C", "0x0000", ""),
        "compare": False,
    },
]

REFERENCES = [
    "IEEE 802.15.4-2020 Standard – *IEEE Standard for Low-Rate Wireless Networks*",
    "Zigbee Specification r22.1.0 (2021) – Connectivity Standards Alliance",
    "Zigbee Cluster Library Specification r7 – CSA",
    "Zigbee Security White Paper – Zigbee Alliance (2009)",
    "Kim & Tosa, *Wireless Sensor Networks*, 2021 – Chapter 4: Zigbee",
    "Farahani, *ZigBee Wireless Networks and Transceivers*, Newnes, 2008",
    "Wireshark ZigBee Dissector – open source, github.com/wireshark/wireshark",
]

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
TEMPLATES = {
    "💡 Bec Smart":            {"type": "end",    "icon": "💡", "attrs": {"luminozitate": "100%", "culoare": "alb cald"}, "on": False},
    "🌡️ Senzor Temperatură":   {"type": "end",    "icon": "🌡️", "attrs": {"temp": None, "umid": None}, "on": True},
    "🔌 Priză Smart":          {"type": "end",    "icon": "🔌", "attrs": {"putere": "0W"}, "on": False},
    "🚪 Senzor Ușă":           {"type": "end",    "icon": "🚪", "attrs": {"status": "închis"}, "on": True},
    "🔁 Router Zigbee":        {"type": "router", "icon": "🔁", "attrs": {}, "on": True},
}


def rand_addr():
    return f"0x{random.randint(0x1000, 0xFFFE):04X}"


def now():
    return datetime.now().strftime("%H:%M:%S")


def add_log(msg):
    st.session_state.log.append((now(), msg))
    if len(st.session_state.log) > 100:
        st.session_state.log.pop(0)


def find_best_parent(dev_key, dev_type=None):
    devs = st.session_state.devices
    if dev_type is None:
        dev_type = devs.get(dev_key, {}).get("type", "end")
    if dev_type == "router":
        return "coordinator"
    active_routers = [k for k, v in devs.items() if v["type"] == "router" and v.get("on", True)]
    return active_routers[0] if active_routers else "coordinator"


def rejoin_network(dev_key):
    devs = st.session_state.devices
    d = devs[dev_key]
    old_parent = d.get("parent")
    new_parent = find_best_parent(dev_key)
    if new_parent != old_parent:
        d["parent"] = new_parent
        add_log(f"🔄 {d['icon']} {d['name']} → rejoin via {devs[new_parent]['name']}")
        add_pkt(d["addr"], devs[new_parent]["addr"], "REJOIN_REQ", "")
        add_pkt(devs[new_parent]["addr"], d["addr"], "REJOIN_RSP", "status=OK")


def check_orphans():
    devs = st.session_state.devices
    for key, d in devs.items():
        if key == "coordinator" or not d.get("on", True):
            continue
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
    if not d["on"] and d["type"] == "router":
        check_orphans()


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


# ══════════════════════════════════════════════════════════════════════════════
# PACKET DISSECTOR CORE
# ══════════════════════════════════════════════════════════════════════════════

# ── CMD metadata map ──────────────────────────────────────────────────────────
CMD_META = {
    "REPORT_ATTR":  {"protocol": "ZCL", "cluster_id": "0x0006", "cluster_name": "On/Off",
                     "zcl_cmd": "0x0A", "zcl_cmd_name": "Report Attributes",
                     "profile_id": "0x0104", "src_ep": 1, "dst_ep": 1},
    "SENSOR_RPT":   {"protocol": "ZCL", "cluster_id": "0x0402", "cluster_name": "Temperature Measurement",
                     "zcl_cmd": "0x0A", "zcl_cmd_name": "Report Attributes",
                     "profile_id": "0x0104", "src_ep": 1, "dst_ep": 1},
    "ZONE_STATUS":  {"protocol": "ZCL", "cluster_id": "0x0500", "cluster_name": "IAS Zone",
                     "zcl_cmd": "0x00", "zcl_cmd_name": "Zone Status Change Notification",
                     "profile_id": "0x0104", "src_ep": 1, "dst_ep": 1},
    "DEV_ANNOUNCE": {"protocol": "NWK", "cluster_id": None, "cluster_name": None,
                     "zcl_cmd": None, "zcl_cmd_name": "Device Announce",
                     "profile_id": None, "src_ep": 0, "dst_ep": 0},
    "ASSOC_REQ":    {"protocol": "MAC", "cluster_id": None, "cluster_name": None,
                     "zcl_cmd": None, "zcl_cmd_name": "Association Request (simulated)",
                     "profile_id": None, "src_ep": 0, "dst_ep": 0},
    "ASSOC_RSP":    {"protocol": "MAC", "cluster_id": None, "cluster_name": None,
                     "zcl_cmd": None, "zcl_cmd_name": "Association Response (simulated)",
                     "profile_id": None, "src_ep": 0, "dst_ep": 0},
    "REJOIN_REQ":   {"protocol": "NWK", "cluster_id": None, "cluster_name": None,
                     "zcl_cmd": None, "zcl_cmd_name": "Rejoin Request",
                     "profile_id": None, "src_ep": 0, "dst_ep": 0},
    "REJOIN_RSP":   {"protocol": "NWK", "cluster_id": None, "cluster_name": None,
                     "zcl_cmd": None, "zcl_cmd_name": "Rejoin Response",
                     "profile_id": None, "src_ep": 0, "dst_ep": 0},
    "LEAVE_REQ":    {"protocol": "NWK", "cluster_id": None, "cluster_name": None,
                     "zcl_cmd": None, "zcl_cmd_name": "Leave Request",
                     "profile_id": None, "src_ep": 0, "dst_ep": 0},
    "PERMIT_JOIN":  {"protocol": "NWK", "cluster_id": None, "cluster_name": None,
                     "zcl_cmd": None, "zcl_cmd_name": "Mgmt Permit Join",
                     "profile_id": None, "src_ep": 0, "dst_ep": 0},
}


def _addr_int(addr_str):
    """Convert '0x1A2B' → 0x1A2B (int)."""
    try:
        return int(addr_str, 16)
    except (ValueError, TypeError):
        return 0


def _pan_int():
    try:
        return int(st.session_state.pan_id, 16)
    except (ValueError, TypeError):
        return 0x1A2B


def build_packet(cmd, src, dst, pay):
    """Build a full structured Zigbee packet dict from event parameters."""
    meta = CMD_META.get(cmd, CMD_META["REPORT_ATTR"])
    seq = st.session_state.seq
    st.session_state.seq = (seq + 1) % 256

    pan_int = _pan_int()
    src_int = _addr_int(src)
    dst_int = _addr_int(dst)
    nwk_seq = (seq + 17) % 256

    # ── MAC layer ────────────────────────────────────────────────────────────
    mac = {
        "pan_id":     st.session_state.pan_id,
        "seq":        seq,
        "frame_type": "Command" if meta["protocol"] == "MAC" else "Data",
    }

    # ── NWK layer ────────────────────────────────────────────────────────────
    nwk = {
        "src":      src,
        "dst":      dst,
        "radius":   10,
        "seq":      nwk_seq,
        "security": meta["protocol"] in ("ZCL", "NWK"),
    }

    # ── APS layer (ZCL only) ─────────────────────────────────────────────────
    aps = None
    if meta["protocol"] == "ZCL":
        aps = {
            "src_ep":     meta["src_ep"],
            "dst_ep":     meta["dst_ep"],
            "profile_id": meta["profile_id"],
            "cluster_id": meta["cluster_id"],
            "cluster_name": meta["cluster_name"],
            "security":   False,
        }

    # ── ZCL layer (ZCL only) ─────────────────────────────────────────────────
    zcl = None
    if meta["protocol"] == "ZCL":
        payload_dict = _parse_payload(pay)
        zcl = {
            "frame_control_flags": "0x18",
            "trans_seq":           seq % 256,
            "command_id":          meta["zcl_cmd"],
            "command_name":        meta["zcl_cmd_name"],
            "payload_dict":        payload_dict,
            "payload_raw":         pay,
        }

    # ── Columns (for packet list) ─────────────────────────────────────────────
    info = _build_info(cmd, meta, pay)
    columns = {
        "time":     now(),
        "src":      src,
        "dst":      dst,
        "protocol": meta["protocol"],
        "info":     info,
    }

    # ── Serialize to bytes ────────────────────────────────────────────────────
    raw_bytes, slices = serialize_packet_to_bytes(mac, nwk, aps, zcl,
                                                   src_int, dst_int, pan_int, nwk_seq, seq, pay)

    return {
        "ts":      now(),
        "columns": columns,
        "mac":     mac,
        "nwk":     nwk,
        "aps":     aps,
        "zcl":     zcl,
        "raw":     {"bytes": raw_bytes, "slices": slices},
    }


def _parse_payload(pay):
    """Parse 'key=val key2=val2' into a dict."""
    result = {}
    for token in pay.split():
        if "=" in token:
            k, v = token.split("=", 1)
            result[k] = v
    if not result and pay.strip():
        result["data"] = pay.strip()
    return result


def _build_info(cmd, meta, pay):
    cluster = meta.get("cluster_name") or ""
    cmd_name = meta.get("zcl_cmd_name") or cmd
    if cluster:
        return f"{cmd_name} ({cluster})" + (f" — {pay}" if pay else "")
    return cmd_name + (f" — {pay}" if pay else "")


def serialize_packet_to_bytes(mac, nwk, aps, zcl, src_int, dst_int, pan_int, nwk_seq, mac_seq, pay):
    """
    Deterministic serialization into bytes with layer slice map.
    Returns (byte_list: list[int], slices: dict)
    """
    buf = []

    # ── MAC header (9 bytes) ─────────────────────────────────────────────────
    # Frame Control: Data frame (0x4188) or Command (0x4308) – simplified
    fc_lo = 0x41 if mac["frame_type"] == "Data" else 0x43
    fc_hi = 0x88
    p_lo = pan_int & 0xFF
    p_hi = (pan_int >> 8) & 0xFF
    d_lo = dst_int & 0xFF
    d_hi = (dst_int >> 8) & 0xFF
    s_lo = src_int & 0xFF
    s_hi = (src_int >> 8) & 0xFF
    mac_bytes = [fc_lo, fc_hi, mac_seq & 0xFF, p_lo, p_hi, d_lo, d_hi, s_lo, s_hi]
    mac_start = 0
    buf.extend(mac_bytes)
    mac_end = len(buf)

    # ── NWK header (8 bytes) ─────────────────────────────────────────────────
    # Frame Control NWK: 0x0848 (Data, security if enabled)
    nwk_fc_lo = 0x48
    nwk_fc_hi = 0x08 | (0x02 if nwk.get("security") else 0x00)
    nwk_bytes = [
        nwk_fc_lo, nwk_fc_hi,
        d_lo, d_hi,
        s_lo, s_hi,
        nwk.get("radius", 10) & 0xFF,
        nwk_seq & 0xFF,
    ]
    nwk_start = mac_end
    buf.extend(nwk_bytes)
    nwk_end = len(buf)

    # ── APS header (6 bytes, if present) ─────────────────────────────────────
    aps_start = aps_end = nwk_end
    if aps:
        profile_int = int(aps["profile_id"], 16) if aps.get("profile_id") else 0x0104
        cluster_int = int(aps["cluster_id"], 16) if aps.get("cluster_id") else 0x0000
        src_ep = aps.get("src_ep", 1) & 0xFF
        dst_ep = aps.get("dst_ep", 1) & 0xFF
        aps_fc = 0x40
        aps_bytes = [
            aps_fc,
            dst_ep,
            cluster_int & 0xFF,
            (cluster_int >> 8) & 0xFF,
            profile_int & 0xFF,
            (profile_int >> 8) & 0xFF,
            src_ep,
        ]
        aps_start = nwk_end
        buf.extend(aps_bytes)
        aps_end = len(buf)

    # ── ZCL payload (variable, if present) ───────────────────────────────────
    zcl_start = zcl_end = aps_end
    if zcl:
        cmd_id = int(zcl["command_id"], 16) if zcl.get("command_id") else 0x0A
        trans = zcl.get("trans_seq", 0) & 0xFF
        fc = int(zcl["frame_control_flags"], 16) if zcl.get("frame_control_flags") else 0x18
        pay_bytes = [ord(c) & 0xFF for c in (zcl.get("payload_raw") or "")[:16]]
        zcl_bytes = [fc, trans, cmd_id] + pay_bytes
        zcl_start = aps_end
        buf.extend(zcl_bytes)
        zcl_end = len(buf)

    slices = {
        "mac": (mac_start, mac_end),
        "nwk": (nwk_start, nwk_end),
        "aps": (aps_start, aps_end),
        "zcl": (zcl_start, zcl_end),
    }
    return buf, slices


def render_hex_view(byte_list, slices):
    """Render an HTML hex dump with per-layer color coding."""
    if not byte_list:
        return "<div class='hex-wrap'><span style='color:#1e2d45'>No bytes</span></div>"

    mac_r = slices.get("mac", (0, 0))
    nwk_r = slices.get("nwk", (0, 0))
    aps_r = slices.get("aps", (0, 0))
    zcl_r = slices.get("zcl", (0, 0))

    def byte_class(i):
        if mac_r[0] <= i < mac_r[1]: return "hex-b-mac"
        if nwk_r[0] <= i < nwk_r[1]: return "hex-b-nwk"
        if aps_r[0] <= i < aps_r[1]: return "hex-b-aps"
        if zcl_r[0] <= i < zcl_r[1]: return "hex-b-zcl"
        return "hex-b-pad"

    lines = []
    for row_start in range(0, len(byte_list), 16):
        row = byte_list[row_start:row_start + 16]
        offset = f'<span class="hex-offset">{row_start:04X}:</span>'
        hex_cols = ""
        for j, b in enumerate(row):
            cls = byte_class(row_start + j)
            hex_cols += f'<span class="{cls}">{b:02X}</span> '
        # pad to 16
        for _ in range(16 - len(row)):
            hex_cols += '<span class="hex-b-pad">   </span>'
        lines.append(f"<div>{offset}{hex_cols}</div>")

    legend = (
        '<div class="hex-legend">'
        '<span class="hl-mac">■ MAC</span>'
        '<span class="hl-nwk">■ NWK</span>'
        '<span class="hl-aps">■ APS</span>'
        '<span class="hl-zcl">■ ZCL</span>'
        '</div>'
    )
    return f'<div class="hex-wrap">{legend}{"".join(lines)}</div>'


def render_protocol_tree(pkt):
    """Render Wireshark-style protocol tree as HTML."""
    if not pkt:
        return "<div class='tree-root' style='color:#334155'>Select a packet to inspect.</div>"

    def field(key, val, desc=""):
        desc_html = f' <span class="tree-desc">— {desc}</span>' if desc else ""
        return f'<div class="tree-field"><span class="tree-key">{key}</span><span class="tree-val">{val}</span>{desc_html}</div>'

    html = '<div class="tree-root">'

    # MAC
    mac = pkt.get("mac", {})
    html += '<div class="tree-layer tree-mac">'
    html += '<div class="tree-hdr">📡 IEEE 802.15.4 MAC</div>'
    html += field("PAN ID", mac.get("pan_id", "—"), "Personal Area Network identifier")
    html += field("Sequence Number", mac.get("seq", "—"), "MAC-level frame counter (0–255)")
    html += field("Frame Type", mac.get("frame_type", "—"), "Data / Command / Beacon / ACK")
    html += '</div>'

    # NWK
    nwk = pkt.get("nwk", {})
    html += '<div class="tree-layer tree-nwk">'
    html += '<div class="tree-hdr">🔀 Zigbee NWK (Network Layer)</div>'
    html += field("Source Address", nwk.get("src", "—"), "16-bit short address (assigned by Coordinator)")
    html += field("Destination Address", nwk.get("dst", "—"), "16-bit short address or 0xFFFF broadcast")
    html += field("Radius", nwk.get("radius", "—"), "Max hop count remaining (decremented at each router)")
    html += field("NWK Sequence", nwk.get("seq", "—"), "NWK-level sequence number for deduplication")
    html += field("Security Enabled", "Yes" if nwk.get("security") else "No",
                  "AES-128-CCM* encryption on NWK payload")
    html += '</div>'

    # APS
    aps = pkt.get("aps")
    if aps:
        html += '<div class="tree-layer tree-aps">'
        html += '<div class="tree-hdr">🔗 Zigbee APS (Application Support Sub-layer)</div>'
        html += field("Profile ID", aps.get("profile_id", "—"),
                      "0x0104 = Home Automation Profile")
        html += field("Cluster ID", f'{aps.get("cluster_id","—")} ({aps.get("cluster_name","?")})',
                      "ZCL cluster identifier")
        html += field("Source Endpoint", aps.get("src_ep", "—"), "Logical function on source device (1–240)")
        html += field("Destination Endpoint", aps.get("dst_ep", "—"), "Logical function on dest device")
        html += field("APS Security", "Yes" if aps.get("security") else "No (NWK sec. active)",
                      "Link-key level encryption")
        html += '</div>'

    # ZCL
    zcl = pkt.get("zcl")
    if zcl:
        html += '<div class="tree-layer tree-zcl">'
        html += '<div class="tree-hdr">⚙️ Zigbee Cluster Library (ZCL)</div>'
        html += field("Frame Control", zcl.get("frame_control_flags", "—"),
                      "0x18 = cluster-specific, server→client, disable default response")
        html += field("Transaction Seq#", zcl.get("trans_seq", "—"),
                      "Correlates ZCL request/response pairs")
        html += field("Command ID",
                      f'{zcl.get("command_id","—")} ({zcl.get("command_name","?")})',
                      "ZCL command identifier")
        payload = zcl.get("payload_dict") or {}
        if payload:
            html += field("Payload", "", "Decoded attribute values")
            for k, v in payload.items():
                html += field(f"  · {k}", v, "")
        html += '</div>'

    html += '</div>'
    return html


def render_packet_list_html(packets, selected_idx):
    """Render an HTML table of packets with the selected row highlighted."""
    headers = ["#", "Time", "Src", "Dst", "Protocol", "Info"]
    rows_html = ""
    for i, p in enumerate(packets):
        c = p.get("columns", {})
        sel_class = "selected" if i == selected_idx else ""
        pro = c.get("protocol", "?")
        pro_class = f"ws-td-pro-{pro}" if pro in ("ZCL", "NWK", "MAC") else "ws-td-pro-MAC"
        rows_html += (
            f'<tr class="{sel_class}" onclick="">'
            f'<td class="ws-td-no">{i+1}</td>'
            f'<td class="ws-td-ts">{c.get("time","")}</td>'
            f'<td class="ws-td-src">{c.get("src","")}</td>'
            f'<td class="ws-td-dst">{c.get("dst","")}</td>'
            f'<td class="{pro_class}">{pro}</td>'
            f'<td class="ws-td-info">{c.get("info","")}</td>'
            f'</tr>'
        )
    header_html = "".join(f"<th>{h}</th>" for h in headers)
    return (
        f'<div style="overflow-y:auto;max-height:230px;border:1px solid #1e2d45;border-radius:8px;">'
        f'<table class="ws-table"><thead><tr>{header_html}</tr></thead>'
        f'<tbody>{rows_html}</tbody></table></div>'
    )


def add_pkt(src, dst, cmd, pay=""):
    """Build a structured packet and insert it into the session packets list."""
    pkt = build_packet(cmd, src, dst, pay)
    st.session_state.packets.insert(0, pkt)
    if len(st.session_state.packets) > 50:
        st.session_state.packets.pop()


# ══════════════════════════════════════════════════════════════════════════════
# UI: NAVIGATION (SIDEBAR)
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🦈 Zigbee Lab")
    mode = st.radio(
        "Mod",
        ["📚 Teorie", "🧪 Lab (Simulator)"],
        index=0 if st.session_state.mode == "📚 Teorie" else 1,
        label_visibility="collapsed",
    )
    st.session_state.mode = mode
    st.divider()

    if mode == "📚 Teorie":
        st.markdown('<div class="sec-hdr">📖 Capitol</div>', unsafe_allow_html=True)
        chap_titles = [c["title"] for c in CHAPTERS]
        st.session_state.chapter = st.selectbox(
            "Capitol", range(len(chap_titles)),
            format_func=lambda i: chap_titles[i],
            label_visibility="collapsed",
        )
        st.divider()
        st.markdown("**📚 Referințe**")
        for ref in REFERENCES:
            st.caption(f"• {ref}")

    else:  # Lab
        st.markdown('<div class="sec-hdr">⚙️ Configurare Rețea</div>', unsafe_allow_html=True)
        st.session_state.pan_id = st.text_input("PAN ID", value=st.session_state.pan_id)
        st.session_state.channel = st.number_input("Canal", min_value=11, max_value=26,
                                                    value=st.session_state.channel)
        st.divider()
        st.markdown('<div class="sec-hdr">➕ Adaugă Device</div>', unsafe_allow_html=True)
        dev_type = st.selectbox("Tip", list(TEMPLATES.keys()), label_visibility="collapsed")
        dev_name = st.text_input("Nume", placeholder="ex: Bec living", label_visibility="collapsed")

        if st.button("🔗 Conectează la rețea", use_container_width=True, type="primary"):
            if dev_name.strip():
                tpl = TEMPLATES[dev_type]
                key = f"dev_{st.session_state.counter}"
                st.session_state.counter += 1
                addr = rand_addr()
                parent_key = find_best_parent(key, dev_type=tpl["type"]) if tpl["on"] else None
                st.session_state.devices[key] = {
                    "name": dev_name.strip(), "type": tpl["type"], "icon": tpl["icon"],
                    "addr": addr, "on": tpl["on"], "attrs": dict(tpl["attrs"]),
                    "parent": parent_key,
                }
                add_log(f"🔗 {tpl['icon']} '{dev_name}' conectat ({addr})")
                if tpl["on"] and parent_key:
                    parent_addr = st.session_state.devices[parent_key]["addr"]
                    add_pkt("0x0000", addr, "PERMIT_JOIN", "dur=60s")
                    add_pkt(addr, parent_addr, "ASSOC_REQ", "")
                    add_pkt(parent_addr, addr, "ASSOC_RSP", "status=OK")
                    add_pkt(addr, "0x0000", "DEV_ANNOUNCE", f"parent={parent_key}")
                st.rerun()

        if st.session_state.packets:
            st.divider()
            st.markdown('<div class="sec-hdr">🎯 Selectează Pachet</div>', unsafe_allow_html=True)
            max_idx = len(st.session_state.packets) - 1
            st.session_state.pkt_selected = st.number_input(
                "Nr. pachet (1 = cel mai nou)",
                min_value=1, max_value=max(1, len(st.session_state.packets)),
                value=min(st.session_state.pkt_selected + 1, len(st.session_state.packets)),
            ) - 1

        if st.button("🗑️ Șterge toate pachetele", use_container_width=True):
            st.session_state.packets = []
            st.session_state.pkt_selected = 0
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# UI: TEORIE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.mode == "📚 Teorie":
    ch = CHAPTERS[st.session_state.chapter]

    st.markdown(f"""
    <div class="main-header">
      <span class="main-title">📚 {ch["title"]}</span>
      <div class="main-sub">Prezentare Academică Zigbee — Protocol Stack & Laborator</div>
    </div>
    """, unsafe_allow_html=True)

    # Main content
    st.markdown(ch["content"])

    # Comparison expander (Chapter 1 only)
    if ch.get("compare"):
        with st.expander("⚖️ Comparativ (scurt): Zigbee vs Thread vs BLE Mesh", expanded=False):
            st.markdown("""
| Criteriu | **Zigbee** | **Thread** | **BLE Mesh** |
|---|---|---|---|
| **Standard radio** | IEEE 802.15.4 | IEEE 802.15.4 | Bluetooth LE |
| **Frecvență** | 2.4 GHz | 2.4 GHz | 2.4 GHz |
| **Rată transfer** | 250 kbps | 250 kbps | 1 Mbps (LE 1M) |
| **Topologie** | Mesh | Mesh (IPv6) | Mesh |
| **Protocol rețea** | Zigbee NWK (prop.) | IPv6 / 6LoWPAN | Bluetooth SIG |
| **Consum energie** | Extrem de mic | Mic | Mic–Mediu |
| **Interoperabilitate** | ZCL (profile-based) | Matter (IP-native) | GATT profiles |
| **Securitate** | AES-128-CCM* | DTLS + COAP | AES-128-CCM |
| **Ecosistem** | Smart Home matur | Thread + Matter (nou) | Apple/Google ecosys. |
| **Noduri max** | 65.000+ | Nelimitat (IP) | ~32.000 |

**Concluzie:** Zigbee rămâne standard de facto pentru Smart Home cu consum mic și ecosistem matur.
Thread/Matter are potențial mai mare pe termen lung (IP-native). BLE Mesh e ideal pentru dispozitive
mobile și ecosisteme Apple/Google.
""")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.expander("📐 Rigoare / Note tehnice", expanded=False):
            st.markdown(ch["notes"])

    with col2:
        with st.expander("📖 Glosar relevant", expanded=False):
            for term, defn in ch["glossary"].items():
                st.markdown(f"**`{term}`** — {defn}")

    with st.expander("🔬 Exemplu în sniffer — Generează pachet demonstrativ", expanded=False):
        cmd, src, dst, pay = ch["example_cmd"]
        meta = CMD_META.get(cmd, {})
        st.info(
            f"**Pachet demonstrativ:** `{cmd}` — "
            f"{meta.get('zcl_cmd_name', cmd)} "
            f"({meta.get('cluster_name') or meta.get('protocol', '')})"
        )
        st.code(
            f"Src: {src}  →  Dst: {dst}\n"
            f"Protocol: {meta.get('protocol','?')}\n"
            f"Info: {_build_info(cmd, meta, pay)}",
            language="text"
        )
        if st.button("📡 Generează și trimite în Lab →", key=f"gen_{st.session_state.chapter}"):
            add_pkt(src, dst, cmd, pay)
            add_log(f"📚 [Teorie cap.{st.session_state.chapter+1}] Exemplu generat: {cmd}")
            st.success("✅ Pachet adăugat! Mergi la modul **🧪 Lab** pentru a-l vizualiza în sniffer.")

# ══════════════════════════════════════════════════════════════════════════════
# UI: LAB (SIMULATOR + WIRESHARK SNIFFER)
# ══════════════════════════════════════════════════════════════════════════════
else:
    devs = st.session_state.devices
    n_total = len(devs)
    n_on = sum(1 for d in devs.values() if d.get("on", True))

    st.markdown(f"""
    <div class="main-header" style="margin-bottom:14px">
      <span class="main-title">🧪 Lab Simulator — Wireshark Zigbee</span>
      <div class="main-sub">
        IEEE 802.15.4 &nbsp;·&nbsp; PAN {st.session_state.pan_id}
        &nbsp;·&nbsp; Canal {st.session_state.channel}
        &nbsp;·&nbsp; {n_on}/{n_total} noduri online
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_dev, col_ws = st.columns([1, 3], gap="large")

    # ── Device Panel ────────────────────────────────────────────────────────
    with col_dev:
        st.markdown('<div class="sec-hdr">🏠 Device-uri NWK</div>', unsafe_allow_html=True)
        if len(devs) == 1:
            st.info("👈 Adaugă device-uri din Sidebar")

        for key, d in devs.items():
            is_on = d.get("on", True)
            is_orphan = False
            if d["type"] != "coordinator" and is_on:
                pk = d.get("parent")
                if pk and pk in devs and not devs[pk].get("on", True):
                    is_orphan = True

            cls = "on" if is_on and not is_orphan else ("orphaned" if is_orphan else "off")
            b_type = {"coordinator": "b-coord", "router": "b-router", "end": "b-end"}[d["type"]]
            b_lbl  = {"coordinator": "ZC", "router": "ZR", "end": "ZED"}[d["type"]]
            b_st   = ('<span class="badge b-on">ONLINE</span>' if d["type"] == "coordinator"
                      else ('<span class="badge b-orphan">ORPHAN</span>' if is_orphan
                            else ('<span class="badge b-on">ON</span>' if is_on
                                  else '<span class="badge b-off">OFF</span>')))
            attrs_html = " · ".join(
                f'{k}: <b>{v}</b>' for k, v in d.get("attrs", {}).items() if v is not None
            )
            parent_info = ""
            if d["type"] != "coordinator" and is_on:
                parent_addr = devs.get(d.get("parent", ""), {}).get("addr", "?")
                parent_info = f" · parent: <b>{parent_addr}</b>"

            st.markdown(f"""
            <div class="dev-card {cls}">
              <div class="dev-name">{d['icon']} {d['name']}
                <span class="badge {b_type}">{b_lbl}</span>{b_st}
              </div>
              <div class="dev-meta">{d['addr']}{parent_info}{" · " + attrs_html if attrs_html else ""}</div>
            </div>
            """, unsafe_allow_html=True)

            if key != "coordinator":
                btns = st.columns([1.4, 1.2, 0.6])
                with btns[0]:
                    lbl = "🔴 Oprește" if is_on else "🟢 Reconectează"
                    if st.button(lbl, key=f"tog_{key}", use_container_width=True):
                        toggle(key)
                        st.rerun()
                with btns[1]:
                    has_sensor = any(x in d.get("attrs", {}) for x in ["temp", "status"])
                    if has_sensor and is_on:
                        if st.button("📊 Payload", key=f"rd_{key}", use_container_width=True):
                            read_sensor(key)
                            st.rerun()
                with btns[2]:
                    if st.button("🗑️", key=f"del_{key}", use_container_width=True):
                        add_log(f"❌ '{d['name']}' leave_req")
                        add_pkt(d["addr"], "0x0000", "LEAVE_REQ", "")
                        del st.session_state.devices[key]
                        check_orphans()
                        st.rerun()

    # ── Wireshark Panel ─────────────────────────────────────────────────────
    with col_ws:
        pkts = st.session_state.packets
        selected_idx = min(st.session_state.pkt_selected, len(pkts) - 1) if pkts else 0
        selected_pkt = pkts[selected_idx] if pkts else None

        # ── Pane 1: Packet List ─────────────────────────────────────────────
        st.markdown('<div class="sec-hdr">📋 Packet List</div>', unsafe_allow_html=True)
        if pkts:
            st.markdown(render_packet_list_html(pkts, selected_idx), unsafe_allow_html=True)
            st.caption(
                f"▲ {len(pkts)} pachete capturate · Selectat: #{selected_idx + 1} "
                f"({selected_pkt['columns']['protocol'] if selected_pkt else '—'}) · "
                "Schimbă selecția din Sidebar → Nr. pachet"
            )
        else:
            st.markdown(
                '<div style="background:#060a10;border:1px solid #1e2d45;border-radius:8px;padding:20px;'
                'font-family:JetBrains Mono,monospace;font-size:.75rem;color:#334155;text-align:center;">'
                'No packets captured. Add devices or generate examples from 📚 Teorie.</div>',
                unsafe_allow_html=True
            )

        st.markdown("---")

        # ── Panes 2 + 3: Details + Hex ──────────────────────────────────────
        col_tree, col_hex = st.columns([1, 1], gap="medium")

        with col_tree:
            st.markdown('<div class="sec-hdr">🔍 Packet Details</div>', unsafe_allow_html=True)
            st.markdown(render_protocol_tree(selected_pkt), unsafe_allow_html=True)

        with col_hex:
            st.markdown('<div class="sec-hdr">💾 Packet Bytes (Hex)</div>', unsafe_allow_html=True)
            if selected_pkt:
                raw = selected_pkt.get("raw", {})
                st.markdown(
                    render_hex_view(raw.get("bytes", []), raw.get("slices", {})),
                    unsafe_allow_html=True
                )
                total = len(raw.get("bytes", []))
                slices = raw.get("slices", {})
                mac_len = slices["mac"][1] - slices["mac"][0] if "mac" in slices else 0
                nwk_len = slices["nwk"][1] - slices["nwk"][0] if "nwk" in slices else 0
                aps_len = slices["aps"][1] - slices["aps"][0] if "aps" in slices else 0
                zcl_len = slices["zcl"][1] - slices["zcl"][0] if "zcl" in slices else 0
                st.caption(
                    f"Total: {total}B · MAC: {mac_len}B · NWK: {nwk_len}B"
                    + (f" · APS: {aps_len}B" if aps_len else "")
                    + (f" · ZCL: {zcl_len}B" if zcl_len else "")
                )
            else:
                st.markdown(
                    '<div class="hex-wrap"><span style="color:#334155">No packet selected.</span></div>',
                    unsafe_allow_html=True
                )

        # ── Console Log ─────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<div class="sec-hdr">📋 Jurnal Consolă</div>', unsafe_allow_html=True)
        log_entries = st.session_state.log[-20:]
        if log_entries:
            log_html = "".join(
                f'<div style="padding:2px 0;border-bottom:1px solid #0a0f1a;">'
                f'<span style="color:#2563eb;font-family:JetBrains Mono,monospace;font-size:.7rem;">[{t}]</span>'
                f' <span style="color:#94a3b8;font-family:JetBrains Mono,monospace;font-size:.7rem;">{m}</span></div>'
                for t, m in reversed(log_entries)
            )
            st.markdown(
                f'<div style="background:#060a10;border:1px solid #1e2d45;border-radius:10px;'
                f'padding:10px 12px;height:140px;overflow-y:auto;">{log_html}</div>',
                unsafe_allow_html=True
            )
        else:
            st.caption("Niciun eveniment de sistem...")

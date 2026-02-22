#!/usr/bin/env python3
"""Generate the Alta Via 4 interactive trail guide HTML file."""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load parsed GPX data
with open(os.path.join(SCRIPT_DIR, 'gpx_data.json'), 'r', encoding='utf-8') as f:
    gpx = json.load(f)

wp_json = json.dumps(gpx['waypoints'], separators=(',', ':'), ensure_ascii=False)
tp_json = json.dumps(gpx['trackPoints'], separators=(',', ':'))

html = f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Alta Via 4 — Turguide</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
/* ===== RESET & BASE ===== */
*,*::before,*::after{{ box-sizing:border-box; margin:0; padding:0; }}
html {{ scroll-behavior:smooth; font-size:16px; }}
body {{
  font-family:'Inter',system-ui,sans-serif;
  background:#FAFAF5;
  color:#2A2A28;
  line-height:1.6;
  overflow-x:hidden;
}}

/* ===== VARIABLES ===== */
:root {{
  --green:#2D5016;
  --green-light:#4A7A2E;
  --green-pale:#E8F0E0;
  --amber:#D4A574;
  --amber-light:#F0DCC8;
  --red-alert:#C0392B;
  --blue-water:#3498DB;
  --bg:#FAFAF5;
  --card:#FFFFFF;
  --text:#2A2A28;
  --text-muted:#6B6B68;
  --shadow:0 2px 12px rgba(0,0,0,0.08);
  --shadow-lg:0 8px 32px rgba(0,0,0,0.12);
  --radius:12px;
  --radius-sm:8px;
}}

/* ===== TYPOGRAPHY ===== */
h1,h2,h3 {{ font-family:'Playfair Display',serif; font-weight:700; color:var(--green); }}

/* ===== HERO SECTION ===== */
.hero {{
  position:relative;
  background: linear-gradient(135deg, #2D5016 0%, #4A7A2E 40%, #6B9B4E 100%);
  color:white;
  padding:3rem 2rem 2.5rem;
  text-align:center;
  overflow:hidden;
}}
.hero::before {{
  content:'';
  position:absolute;
  top:0;left:0;right:0;bottom:0;
  background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%23ffffff' fill-opacity='0.05' d='M0,224L48,213.3C96,203,192,181,288,186.7C384,192,480,224,576,224C672,224,768,192,864,170.7C960,149,1056,139,1152,149.3C1248,160,1344,192,1392,208L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'/%3E%3C/svg%3E") no-repeat bottom/cover;
}}
.hero h1 {{
  font-family:'Playfair Display',serif;
  font-size:clamp(2.2rem,5vw,3.8rem);
  font-weight:800;
  color:white;
  letter-spacing:1px;
  margin-bottom:0.3rem;
  position:relative;
}}
.hero .subtitle {{
  font-size:clamp(1rem,2.5vw,1.3rem);
  opacity:0.9;
  margin-bottom:2rem;
  font-weight:400;
  position:relative;
}}
.hero-stats {{
  display:flex;
  justify-content:center;
  gap:2rem;
  flex-wrap:wrap;
  position:relative;
}}
.hero-stat {{
  background:rgba(255,255,255,0.15);
  backdrop-filter:blur(8px);
  border:1px solid rgba(255,255,255,0.2);
  border-radius:var(--radius);
  padding:1rem 1.5rem;
  min-width:140px;
}}
.hero-stat .val {{
  font-size:1.6rem;
  font-weight:700;
  display:block;
}}
.hero-stat .lbl {{
  font-size:0.8rem;
  text-transform:uppercase;
  letter-spacing:1px;
  opacity:0.85;
}}

/* ===== STICKY NAV ===== */
.seg-nav {{
  position:sticky;
  top:0;
  z-index:1000;
  background:var(--card);
  border-bottom:1px solid #e0e0d8;
  padding:0.6rem 1rem;
  display:flex;
  gap:0.4rem;
  overflow-x:auto;
  scrollbar-width:none;
  -webkit-overflow-scrolling:touch;
  box-shadow:0 2px 8px rgba(0,0,0,0.06);
}}
.seg-nav::-webkit-scrollbar {{ display:none; }}
.seg-nav button {{
  flex-shrink:0;
  border:none;
  background:var(--green-pale);
  color:var(--green);
  padding:0.4rem 1rem;
  border-radius:20px;
  font-family:'Inter',sans-serif;
  font-size:0.82rem;
  font-weight:600;
  cursor:pointer;
  transition:all 0.2s;
  white-space:nowrap;
}}
.seg-nav button:hover {{ background:var(--green); color:white; }}
.seg-nav button.active {{ background:var(--green); color:white; box-shadow:0 2px 8px rgba(45,80,22,0.3); }}

/* ===== MAP SECTION ===== */
.map-section {{
  padding:1.5rem;
  max-width:1200px;
  margin:0 auto;
}}
.map-section h2 {{
  font-size:1.5rem;
  margin-bottom:0.8rem;
  display:flex;
  align-items:center;
  gap:0.5rem;
}}
#map {{
  width:100%;
  height:480px;
  border-radius:var(--radius);
  box-shadow:var(--shadow-lg);
  border:2px solid #e0e0d8;
}}
.leaflet-popup-content-wrapper {{
  border-radius:var(--radius-sm)!important;
  font-family:'Inter',sans-serif!important;
}}

/* ===== SEGMENT CARDS ===== */
.segments {{
  max-width:1200px;
  margin:1rem auto 3rem;
  padding:0 1.5rem;
  display:flex;
  flex-direction:column;
  gap:2rem;
}}
.seg-card {{
  background:var(--card);
  border-radius:var(--radius);
  box-shadow:var(--shadow);
  overflow:hidden;
  transition:box-shadow 0.3s, transform 0.15s;
  border:1px solid #eee;
  scroll-margin-top:60px;
}}
.seg-card:hover {{
  box-shadow:var(--shadow-lg);
  transform:translateY(-2px);
}}
.seg-card-header {{
  background:linear-gradient(135deg, var(--green) 0%, var(--green-light) 100%);
  color:white;
  padding:1.2rem 1.5rem;
  cursor:pointer;
  display:flex;
  justify-content:space-between;
  align-items:center;
}}
.seg-card-header h3 {{
  color:white;
  font-size:1.2rem;
  margin:0;
}}
.seg-card-header .seg-route {{
  font-size:0.9rem;
  opacity:0.9;
  font-weight:400;
  font-family:'Inter',sans-serif;
}}
.seg-card-header .seg-arrow {{ font-size:1.4rem; transition:transform 0.3s; }}

.seg-card-body {{
  padding:1.5rem;
}}

/* Stats grid */
.stats-grid {{
  display:grid;
  grid-template-columns:repeat(auto-fit, minmax(130px,1fr));
  gap:0.8rem;
  margin-bottom:1.2rem;
}}
.stat-box {{
  background:var(--bg);
  border-radius:var(--radius-sm);
  padding:0.8rem;
  text-align:center;
  border:1px solid #eee;
}}
.stat-box .stat-val {{
  font-size:1.2rem;
  font-weight:700;
  color:var(--green);
  display:block;
}}
.stat-box .stat-lbl {{
  font-size:0.72rem;
  text-transform:uppercase;
  letter-spacing:0.5px;
  color:var(--text-muted);
  margin-top:2px;
}}
.stat-box.ascent .stat-val {{ color:#27ae60; }}
.stat-box.descent .stat-val {{ color:var(--red-alert); }}

/* Elevation chart */
.elevation-wrap {{
  margin:1rem 0;
  background:var(--bg);
  border-radius:var(--radius-sm);
  padding:1rem;
  border:1px solid #eee;
}}
.elevation-wrap canvas {{
  width:100%!important;
  height:160px!important;
}}

/* POI lists */
.poi-section {{
  margin-top:1rem;
}}
.poi-section h4 {{
  font-family:'Inter',sans-serif;
  font-size:0.85rem;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:0.5px;
  color:var(--text-muted);
  margin-bottom:0.5rem;
  cursor:pointer;
  display:flex;
  align-items:center;
  gap:0.4rem;
}}
.poi-section h4::after {{
  content:'\\25BC';
  font-size:0.6rem;
  transition:transform 0.2s;
}}
.poi-section h4.collapsed::after {{
  transform:rotate(-90deg);
}}
.poi-list {{
  list-style:none;
  display:flex;
  flex-direction:column;
  gap:0.4rem;
}}
.poi-list.hidden {{ display:none; }}
.poi-item {{
  display:flex;
  align-items:center;
  gap:0.6rem;
  padding:0.5rem 0.8rem;
  background:var(--bg);
  border-radius:var(--radius-sm);
  font-size:0.88rem;
  border:1px solid #eee;
}}
.poi-icon {{
  width:28px;
  height:28px;
  border-radius:50%;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:0.85rem;
  flex-shrink:0;
}}
.poi-icon.lodge {{ background:var(--amber-light); }}
.poi-icon.water {{ background:#D6EAF8; }}
.poi-icon.alert {{ background:#FADBD8; }}
.poi-icon.shelter {{ background:#E8DAEF; }}
.poi-icon.restaurant {{ background:#FCF3CF; }}
.poi-icon.landmark {{ background:var(--green-pale); }}
.poi-ele {{
  margin-left:auto;
  font-size:0.78rem;
  color:var(--text-muted);
  font-weight:500;
  white-space:nowrap;
}}

/* Landmark description */
.landmark-desc {{
  margin-top:1rem;
  padding:1rem;
  background:linear-gradient(135deg, var(--green-pale) 0%, #f5f5ee 100%);
  border-radius:var(--radius-sm);
  border-left:3px solid var(--green);
  font-size:0.9rem;
  line-height:1.7;
  color:var(--text);
}}

/* Map button */
.btn-map {{
  margin-top:1rem;
  display:inline-flex;
  align-items:center;
  gap:0.4rem;
  background:var(--green);
  color:white;
  border:none;
  padding:0.6rem 1.2rem;
  border-radius:var(--radius-sm);
  font-family:'Inter',sans-serif;
  font-size:0.85rem;
  font-weight:600;
  cursor:pointer;
  transition:background 0.2s, transform 0.1s;
}}
.btn-map:hover {{ background:var(--green-light); transform:translateY(-1px); }}

/* ===== FOOTER ===== */
footer {{
  text-align:center;
  padding:2rem;
  color:var(--text-muted);
  font-size:0.82rem;
  border-top:1px solid #e0e0d8;
}}

/* ===== RESPONSIVE ===== */
@media(max-width:768px) {{
  .hero {{ padding:2rem 1rem 1.5rem; }}
  .hero-stats {{ gap:0.8rem; }}
  .hero-stat {{ min-width:100px; padding:0.8rem 1rem; }}
  .hero-stat .val {{ font-size:1.2rem; }}
  #map {{ height:350px; }}
  .segments {{ padding:0 1rem; }}
  .seg-card-header {{ padding:1rem; }}
  .seg-card-body {{ padding:1rem; }}
  .stats-grid {{ grid-template-columns:repeat(3,1fr); gap:0.5rem; }}
  .stat-box {{ padding:0.6rem 0.4rem; }}
  .stat-box .stat-val {{ font-size:1rem; }}
}}
@media(max-width:480px) {{
  .stats-grid {{ grid-template-columns:repeat(2,1fr); }}
}}

/* ===== ANIMATIONS ===== */
@keyframes fadeUp {{
  from {{ opacity:0; transform:translateY(20px); }}
  to {{ opacity:1; transform:translateY(0); }}
}}
.seg-card {{ animation:fadeUp 0.5s ease both; }}
.seg-card:nth-child(2) {{ animation-delay:0.05s; }}
.seg-card:nth-child(3) {{ animation-delay:0.1s; }}
.seg-card:nth-child(4) {{ animation-delay:0.15s; }}
.seg-card:nth-child(5) {{ animation-delay:0.2s; }}
.seg-card:nth-child(6) {{ animation-delay:0.25s; }}
.seg-card:nth-child(7) {{ animation-delay:0.3s; }}
.seg-card:nth-child(8) {{ animation-delay:0.35s; }}
.seg-card:nth-child(9) {{ animation-delay:0.4s; }}

/* Legend */
.map-legend {{
  display:flex;
  flex-wrap:wrap;
  gap:0.8rem;
  margin-top:0.6rem;
  font-size:0.8rem;
  color:var(--text-muted);
}}
.legend-item {{
  display:flex;
  align-items:center;
  gap:0.3rem;
}}
.legend-dot {{
  width:12px;height:12px;border-radius:50%;
}}
</style>
</head>
<body>

<!-- ===== HERO ===== -->
<section class="hero">
  <h1>Alta Via 4</h1>
  <p class="subtitle">Dolomittene \\u2022 Fra San Candido til Pieve di Cadore</p>
  <div class="hero-stats">
    <div class="hero-stat"><span class="val" id="total-dist">—</span><span class="lbl">Total avstand</span></div>
    <div class="hero-stat"><span class="val" id="total-asc">—</span><span class="lbl">Total stigning</span></div>
    <div class="hero-stat"><span class="val" id="total-desc">—</span><span class="lbl">Total nedstigning</span></div>
    <div class="hero-stat"><span class="val" id="total-days">9</span><span class="lbl">Etapper</span></div>
    <div class="hero-stat"><span class="val">884–2577</span><span class="lbl">H\\u00f8yde (moh)</span></div>
  </div>
</section>

<!-- ===== STICKY NAV ===== -->
<nav class="seg-nav" id="segNav"></nav>

<!-- ===== MAP ===== -->
<section class="map-section">
  <h2>\\U0001F5FA Oversiktskart</h2>
  <div id="map"></div>
  <div class="map-legend" id="mapLegend"></div>
</section>

<!-- ===== SEGMENTS ===== -->
<div class="segments" id="segments"></div>

<!-- ===== FOOTER ===== -->
<footer>
  Generert fra GPX-data \\u2022 Trek\\u2019n\\u2019Trails \\u2022 Alta Via 4, Dolomittene \\u2022 2026
</footer>

<script>
// ===== EMBEDDED DATA =====
const WAYPOINTS = {wp_json};
const TRACK_POINTS = {tp_json};

// ===== SEGMENT DEFINITIONS =====
const SEGMENTS = [
  {{
    id: 1,
    name: "Etappe 1",
    from: "San Candido",
    to: "Rifugio Tre Scarperi",
    endWpt: "Rifugio Tre Scarperi",
    color: "#E74C3C",
    landmarks: [
      {{ name: "Haunold / Monte Baranci", desc: "Utsiktspunkt over Pustertal-dalen med panorama mot Sextner-Dolomittene." }},
      {{ name: "Innichen / San Candido", desc: "Sjarmerende s\\u00f8rtirolsk landsby med barokk stiftskirke fra 1200-tallet." }},
    ],
    description: "F\\u00f8rste etappe starter i den sjarmerende landsbyen San Candido (Innichen) p\\u00e5 1175 moh og f\\u00f8lger stien sørover gjennom l\\u00e5rke- og furuskoger. Ruten stiger gradvis opp til Rifugio Tre Scarperi (Dreischusterhütte) p\\u00e5 1634 moh, med flott utsikt mot Sextner Dolomittene underveis. En fin oppvarming f\\u00f8r de mer krevende etappene som venter."
  }},
  {{
    id: 2,
    name: "Etappe 2",
    from: "Rifugio Tre Scarperi",
    to: "Rifugio A. Locatelli",
    endWpt: "Rifugio Antonio Locatelli",
    color: "#E67E22",
    landmarks: [
      {{ name: "Tre Cime di Lavaredo (nordsiden)", desc: "Verdens mest ikoniske fjellformasjon i Dolomittene \\u2013 tre majestetiske s\\u00f8yler som reiser seg over 2999 moh. Unesco verdensarv." }},
      {{ name: "Sextner Sonnenuhr", desc: "De tolv toppene i Sextner-Dolomittene som danner et naturlig solur, synlig fra Tre Scarperi-omr\\u00e5det." }},
      {{ name: "Paternkofel / Monte Paterno", desc: "Dramatisk 2744 m h\\u00f8y topp rett ved Locatelli-hytta, kjent fra f\\u00f8rste verdenskrig." }},
    ],
    description: "Den legendariske etappen mot Tre Cime! Fra Rifugio Tre Scarperi stiger ruten kraftig opp mot Locatelli-hytta p\\u00e5 nesten 2400 moh. Her \\u00e5pner et av verdens mest spektakul\\u00e6re fjellpanoramaer seg: Tre Cime di Lavaredo sett fra nordsiden, Monte Paterno og Sextner Sonnenuhr. Locatelli-hytta ligger dramatisk plassert p\\u00e5 en platå med 360-graders utsikt."
  }},
  {{
    id: 3,
    name: "Etappe 3",
    from: "Rifugio A. Locatelli",
    to: "Rifugio Fonda Savio",
    endWpt: "Rifugio Fonda Savio",
    color: "#F1C40F",
    landmarks: [
      {{ name: "Tre Cime di Lavaredo (n\\u00e6rbilde)", desc: "Ruten passerer t\\u00e6t forbi den s\\u00f8rlige siden av Tre Cime \\u2013 en helt annen opplevelse enn nordsiden." }},
      {{ name: "Forcella Lavaredo", desc: "H\\u00f8yt fjellpass (2454 m) med \\u00e5pen utsikt mot Cadini-gruppen og Auronzo-dalen." }},
      {{ name: "Langalm", desc: "Tradisjonell alm-restaurant med lokale spesialiteter p\\u00e5 2235 moh." }},
    ],
    description: "En lang og variert etappe h\\u00f8yt til fjells. Fra Locatelli g\\u00e5r ruten via Langalm-restauranten og passerer t\\u00e6t forbi Rifugio Auronzo og Rifugio Lavaredo, begge med fantastisk n\\u00e6rhet til Tre Cime. Deretter fortsetter stien langs h\\u00f8ydedraget med en utstyrt klatreseksjon (Via Ferrata B) f\\u00f8r du n\\u00e5r Rifugio Fonda Savio p\\u00e5 2344 moh. Medbring klatresele!"
  }},
  {{
    id: 4,
    name: "Etappe 4",
    from: "Rifugio Fonda Savio",
    to: "Albergo Cristallo",
    endWpt: "Albergo Cristallo",
    color: "#2ECC71",
    landmarks: [
      {{ name: "Cadini di Misurina", desc: "En spektakul\\u00e6r gruppe av spisse kalktinder som omgir ruten \\u2013 s\\u00e6rlig imponerende i morgenlys." }},
      {{ name: "Monte Cristallo (3221 m)", desc: "En av de h\\u00f8yeste toppene i Dolomittene, synlig mot nordvest. Massiv gletsjer p\\u00e5 nordsiden." }},
      {{ name: "Misurina-sj\\u00f8en", desc: "Ikonisk alpesj\\u00f8 p\\u00e5 1754 moh, kjent for sitt speilbilde av Sorapiss og Cadini-tindene." }},
    ],
    description: "Fra Fonda Savio starter en lang nedstigning gjennom Cadini-gruppen. Ruten passerer Rifugio Citt\\u00e0 di Carpi (2111 m) og fortsetter ned mot Misurina-omr\\u00e5det. Underveis har du fantastisk utsikt mot Monte Cristallo og Cadini di Misurina. Etappen ender ved Albergo Cristallo (1372 m) \\u2013 en velfortjent komfortabel overnatting etter flere n\\u00e6tter p\\u00e5 fjellhytter."
  }},
  {{
    id: 5,
    name: "Etappe 5",
    from: "Albergo Cristallo",
    to: "Rifugio Vandelli",
    endWpt: "Rifugio Vandelli",
    color: "#1ABC9C",
    landmarks: [
      {{ name: "Sorapiss-gruppen", desc: "Dramatisk fjellmassiv dominert av Punta Sorapiss (3205 m) med imponerende glasialer og bratte vegger." }},
      {{ name: "Lago di Sorapiss", desc: "Eventyrlig turkis alpesjø p\\u00e5 1925 moh, kjent for sitt surrealistiske bl\\u00e5grønne vann. En av Dolomittenes mest fotograferte sjøer." }},
      {{ name: "Croda da Lago", desc: "Markant fjelltopp (2701 m) som reiser seg dramatisk over skoggrensen." }},
    ],
    description: "En fantastisk etappe fra Cristallo opp til Rifugio Vandelli ved foten av Sorapiss! Ruten stiger fra 1372 m til 1931 m gjennom vakre alpeskoger og over alpine enger. H\\u00f8ydepunktet er n\\u00e6rheten til Lago di Sorapiss og utsikten mot Sorapiss-massivet. Vandelli-hytta ligger spektakul\\u00e6rt plassert ved bredden av en demning."
  }},
  {{
    id: 6,
    name: "Etappe 6",
    from: "Rifugio Vandelli",
    to: "Rifugio San Marco",
    endWpt: "Rifugio San Marco",
    color: "#3498DB",
    landmarks: [
      {{ name: "Marmarole-kjeden", desc: "En av de mest avsidesliggende fjellkjedene i Dolomittene, med tinder opp til 2932 m. F\\u00e6rre turister, villere natur." }},
      {{ name: "Croda Marcora (2932 m)", desc: "Marmarole-kjedens h\\u00f8yeste topp, synlig gjennom hele etappen som en mektig veiviser." }},
      {{ name: "Bivacco Slataper (2575 m)", desc: "H\\u00f8yeste punkt p\\u00e5 hele Alta Via 4 \\u2013 en enkel bivakk med fantastisk panorama over Marmarole og Antelao." }},
    ],
    description: "Den mest krevende etappen p\\u00e5 hele Alta Via 4! Fra Vandelli g\\u00e5r ruten over to Via Ferrata-seksjoner (grad C og A), forbi Bivacco Comici og opp til rutens h\\u00f8yeste punkt ved Bivacco Slataper (2575 m). Klatresele og hjelm er obligatorisk. Deretter en lang nedstigning til Rifugio San Marco (1818 m). Kun for erfarne fjellvandrere."
  }},
  {{
    id: 7,
    name: "Etappe 7",
    from: "Rifugio San Marco",
    to: "Rifugio Galassi",
    endWpt: "Rifugio Pietro Galassi",
    color: "#9B59B6",
    landmarks: [
      {{ name: "Val d'Ansiei", desc: "Vakker alpin dal som strekker seg gjennom Marmarole-gruppen med rike blomsterenger." }},
      {{ name: "Marmarole-traverseringen", desc: "Ruten traverserer den s\\u00f8rlige flanken av Marmarole \\u2013 en av de mest avsidesliggende strekningene p\\u00e5 hele banet." }},
    ],
    description: "En variert etappe gjennom Marmarole-gruppen. Fra San Marco passerer du raskt Rifugio Scotter-Palatini (1571 m) f\\u00f8r ruten stiger opp igjen til Rifugio Galassi p\\u00e5 2014 moh. Landskapet er villere og mer avsides enn de nordlige etappene \\u2013 her m\\u00f8ter du f\\u00e6rre vandrere og mer autentisk Dolomitt-natur."
  }},
  {{
    id: 8,
    name: "Etappe 8",
    from: "Rifugio Galassi",
    to: "Rifugio Antelao",
    endWpt: "Rifugio Antelao",
    color: "#E91E63",
    landmarks: [
      {{ name: "Monte Antelao (3264 m)", desc: "\\u00abDolomittenes Konge\\u00bb \\u2013 den nest h\\u00f8yeste toppen i Dolomittene. Dominerer hele den sydlige horisonten med sin majestetiske pyramideform." }},
      {{ name: "Monte Pelmo (3168 m)", desc: "Massiv \\u00abtafelberg\\u00bb synlig mot vest \\u2013 en av Dolomittenes mest gjenkjennelige silhuetter." }},
    ],
    description: "En dramatisk etappe med kraftig stigning! Fra Galassi g\\u00e5r ruten via Rifugio Capanna degli Alpini (1397 m) f\\u00f8r den stiger bratt opp igjen med en Via Ferrata B-seksjon. Monte Antelao (3264 m), \\u00abDolomittenes Konge\\u00bb, dominerer utsikten gjennom hele dagen. Etappen avsluttes ved Rifugio Antelao p\\u00e5 1797 moh."
  }},
  {{
    id: 9,
    name: "Etappe 9",
    from: "Rifugio Antelao",
    to: "Pieve di Cadore",
    endWpt: null,
    color: "#795548",
    landmarks: [
      {{ name: "Centro Cadore-panorama", desc: "Utsikt over den historiske Cadore-dalen med sjøen Lago di Centro Cadore omgitt av gr\\u00f8nne \\u00e5ser." }},
      {{ name: "Pieve di Cadore", desc: "F\\u00f8deby for renessansemaleren Tizian (Titian). Sjarmerende gamlebydel med historiske kirker og museer." }},
      {{ name: "Antelao fra s\\u00f8r", desc: "Siste tilbakeblikk mot den mektige Antelao \\u2013 en verdig avslutning p\\u00e5 Alta Via 4." }},
    ],
    description: "Siste etappe \\u2013 nedstigning til sivilisasjonen! Fra Rifugio Antelao passerer du Rifugio Costa Piana (1568 m) og den reviderte Capanna Tita Panciera f\\u00f8r ruten f\\u00f8rer ned gjennom skoger til Pieve di Cadore (884 m). Underveis har du siste panoramautsikter mot Antelao og Marmarole. Pieve di Cadore er f\\u00f8destedet til Tizian og en verdig avslutning p\\u00e5 denne episke fjellturen."
  }}
];

// Segment color palette
const SEG_COLORS = SEGMENTS.map(s => s.color);

// ===== UTILITIES =====
function haversine(lat1, lon1, lat2, lon2) {{
  const R = 6371000;
  const toRad = x => x * Math.PI / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat/2)**2 + Math.cos(toRad(lat1))*Math.cos(toRad(lat2))*Math.sin(dLon/2)**2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}}

function findNearestTrackIndex(lat, lon) {{
  let minDist = Infinity, idx = 0;
  for (let i = 0; i < TRACK_POINTS.length; i++) {{
    const d = haversine(lat, lon, TRACK_POINTS[i][0], TRACK_POINTS[i][1]);
    if (d < minDist) {{ minDist = d; idx = i; }}
  }}
  return idx;
}}

function formatDist(m) {{
  return m >= 1000 ? (m/1000).toFixed(1) + ' km' : Math.round(m) + ' m';
}}

function formatElev(m) {{
  return Math.round(m) + ' m';
}}

// ===== COMPUTE SEGMENT DATA =====
function computeSegments() {{
  // Find track indices for each segment boundary
  const boundaries = [0]; // start
  for (const seg of SEGMENTS) {{
    if (seg.endWpt) {{
      const wpt = WAYPOINTS.find(w => w.name === seg.endWpt);
      if (wpt) {{
        boundaries.push(findNearestTrackIndex(wpt.lat, wpt.lon));
      }}
    }} else {{
      boundaries.push(TRACK_POINTS.length - 1);
    }}
  }}
  // Ensure boundaries are monotonically increasing
  for (let i = 1; i < boundaries.length; i++) {{
    if (boundaries[i] <= boundaries[i-1]) boundaries[i] = boundaries[i-1] + 1;
  }}

  let totalDist = 0, totalAsc = 0, totalDesc = 0;

  for (let s = 0; s < SEGMENTS.length; s++) {{
    const startIdx = boundaries[s];
    const endIdx = boundaries[s+1];
    const points = TRACK_POINTS.slice(startIdx, endIdx + 1);

    let dist = 0, asc = 0, desc = 0;
    let minEle = Infinity, maxEle = -Infinity;
    const cumDist = [0];

    for (let i = 0; i < points.length; i++) {{
      const ele = points[i][2];
      if (ele < minEle) minEle = ele;
      if (ele > maxEle) maxEle = ele;
      if (i > 0) {{
        const d = haversine(points[i-1][0], points[i-1][1], points[i][0], points[i][1]);
        dist += d;
        cumDist.push(dist);
        const dEle = ele - points[i-1][2];
        if (dEle > 0) asc += dEle;
        else desc += Math.abs(dEle);
      }}
    }}

    // Estimated time (Munter method: flat 4 km/h, +1h per 400m ascent)
    const timeH = dist/4000 + asc/400;

    SEGMENTS[s].data = {{
      startIdx, endIdx, points, dist, asc, desc, minEle, maxEle, cumDist, timeH
    }};

    // Find POIs in this segment's lat range
    const latStart = points[0][0];
    const latEnd = points[points.length-1][0];
    const latMin = Math.min(latStart, latEnd);
    const latMax = Math.max(latStart, latEnd);

    SEGMENTS[s].pois = WAYPOINTS.filter(w => {{
      // Check if waypoint is near any point in this segment
      const nearIdx = findNearestTrackIndex(w.lat, w.lon);
      return nearIdx >= startIdx && nearIdx <= endIdx;
    }});

    totalDist += dist;
    totalAsc += asc;
    totalDesc += desc;
  }}

  // Update hero stats
  document.getElementById('total-dist').textContent = (totalDist/1000).toFixed(1) + ' km';
  document.getElementById('total-asc').textContent = formatElev(totalAsc) + ' \\u2191';
  document.getElementById('total-desc').textContent = formatElev(totalDesc) + ' \\u2193';
}}

// ===== LEAFLET MAP =====
let map, segmentLayers = [], markerLayer;

function initMap() {{
  map = L.map('map', {{
    scrollWheelZoom: true,
    zoomControl: true
  }}).setView([46.58, 12.29], 11);

  L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 17,
    attribution: '&copy; OpenTopoMap'
  }}).addTo(map);

  // Draw segments
  for (const seg of SEGMENTS) {{
    const latlngs = seg.data.points.map(p => [p[0], p[1]]);
    const line = L.polyline(latlngs, {{
      color: seg.color,
      weight: 4,
      opacity: 0.85,
      lineCap: 'round'
    }}).addTo(map);
    line.bindPopup('<strong>' + seg.name + '</strong><br>' + seg.from + ' \\u2192 ' + seg.to);
    segmentLayers.push(line);
  }}

  // Fit map to route
  const allLatLngs = TRACK_POINTS.map(p => [p[0], p[1]]);
  map.fitBounds(L.latLngBounds(allLatLngs).pad(0.05));

  // Custom icons
  function makeIcon(emoji, bgColor) {{
    return L.divIcon({{
      html: '<div style="background:' + bgColor + ';width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3);">' + emoji + '</div>',
      className: '',
      iconSize: [30, 30],
      iconAnchor: [15, 15],
      popupAnchor: [0, -18]
    }});
  }}

  markerLayer = L.layerGroup().addTo(map);

  for (const w of WAYPOINTS) {{
    let icon, popupExtra = '';
    switch(w.sym) {{
      case 'Lodge':
        icon = makeIcon('\\U0001F3D4', '#D4A574');
        break;
      case 'Hotel':
        icon = makeIcon('\\U0001F3E8', '#D4A574');
        break;
      case 'Shelter':
        icon = makeIcon('\\u26FA', '#D7BDE2');
        popupExtra = w.desc ? '<br><em>' + w.desc + '</em>' : '';
        break;
      case 'Alert':
        icon = makeIcon('\\u26A0\\uFE0F', '#F1948A');
        break;
      case 'Drinking Water':
        icon = makeIcon('\\U0001F4A7', '#85C1E9');
        break;
      case 'Restaurant':
        icon = makeIcon('\\U0001F37D', '#F9E79F');
        break;
      default:
        icon = makeIcon('\\U0001F4CD', '#CCC');
    }}
    const marker = L.marker([w.lat, w.lon], {{ icon }}).addTo(markerLayer);
    marker.bindPopup('<strong>' + w.name + '</strong><br>' + Math.round(w.ele) + ' moh' + popupExtra);
  }}

  // Start & End markers
  const startPt = TRACK_POINTS[0];
  const endPt = TRACK_POINTS[TRACK_POINTS.length - 1];
  L.marker([startPt[0], startPt[1]], {{
    icon: makeIcon('\\U0001F3C1', '#27AE60')
  }}).addTo(map).bindPopup('<strong>Start: San Candido</strong><br>' + Math.round(startPt[2]) + ' moh');
  L.marker([endPt[0], endPt[1]], {{
    icon: makeIcon('\\U0001F3C1', '#E74C3C')
  }}).addTo(map).bindPopup('<strong>M\\u00e5l: Pieve di Cadore</strong><br>' + Math.round(endPt[2]) + ' moh');

  // Legend
  const legend = document.getElementById('mapLegend');
  const legendItems = [
    ['\\U0001F3D4', '#D4A574', 'Hytte/Lodge'],
    ['\\U0001F3E8', '#D4A574', 'Hotell'],
    ['\\u26FA', '#D7BDE2', 'Bivakk'],
    ['\\u26A0\\uFE0F', '#F1948A', 'Via Ferrata'],
    ['\\U0001F4A7', '#85C1E9', 'Vannkilde'],
    ['\\U0001F37D', '#F9E79F', 'Restaurant'],
  ];
  legendItems.forEach(([emoji, bg, label]) => {{
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.innerHTML = '<span class="legend-dot" style="background:' + bg + ';display:flex;align-items:center;justify-content:center;font-size:10px;">' + emoji + '</span> ' + label;
    legend.appendChild(item);
  }});
}}

function focusSegment(idx) {{
  const seg = SEGMENTS[idx];
  const bounds = L.latLngBounds(seg.data.points.map(p => [p[0], p[1]]));
  map.fitBounds(bounds.pad(0.15), {{ animate: true, duration: 0.8 }});

  // Highlight this segment
  segmentLayers.forEach((l, i) => {{
    l.setStyle({{ weight: i === idx ? 7 : 3, opacity: i === idx ? 1 : 0.4 }});
    if (i === idx) l.bringToFront();
  }});
}}

function resetMapView() {{
  const allLatLngs = TRACK_POINTS.map(p => [p[0], p[1]]);
  map.fitBounds(L.latLngBounds(allLatLngs).pad(0.05), {{ animate: true }});
  segmentLayers.forEach(l => l.setStyle({{ weight: 4, opacity: 0.85 }}));
}}

// ===== ELEVATION CHARTS =====
const charts = [];

function createElevationChart(canvasId, seg) {{
  const ctx = document.getElementById(canvasId).getContext('2d');
  const points = seg.data.points;
  const cumDist = seg.data.cumDist;

  // Downsample for performance (max 200 points)
  const step = Math.max(1, Math.floor(points.length / 200));
  const labels = [];
  const data = [];
  for (let i = 0; i < points.length; i += step) {{
    labels.push((cumDist[i] / 1000).toFixed(1));
    data.push(points[i][2]);
  }}
  // Always include last point
  if ((points.length - 1) % step !== 0) {{
    labels.push((cumDist[cumDist.length-1] / 1000).toFixed(1));
    data.push(points[points.length-1][2]);
  }}

  const gradient = ctx.createLinearGradient(0, 0, 0, 160);
  gradient.addColorStop(0, seg.color + '40');
  gradient.addColorStop(1, seg.color + '05');

  const chart = new Chart(ctx, {{
    type: 'line',
    data: {{
      labels,
      datasets: [{{
        data,
        borderColor: seg.color,
        backgroundColor: gradient,
        borderWidth: 2,
        fill: true,
        pointRadius: 0,
        pointHitRadius: 8,
        tension: 0.3
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          backgroundColor: 'rgba(0,0,0,0.8)',
          titleFont: {{ family: 'Inter' }},
          bodyFont: {{ family: 'Inter' }},
          callbacks: {{
            title: (items) => items[0].label + ' km',
            label: (item) => Math.round(item.raw) + ' moh'
          }}
        }}
      }},
      scales: {{
        x: {{
          title: {{ display: true, text: 'Avstand (km)', font: {{ size: 11, family: 'Inter' }} }},
          ticks: {{ maxTicksLimit: 8, font: {{ size: 10 }} }},
          grid: {{ display: false }}
        }},
        y: {{
          title: {{ display: true, text: 'H\\u00f8yde (m)', font: {{ size: 11, family: 'Inter' }} }},
          ticks: {{ font: {{ size: 10 }} }},
          grid: {{ color: '#eee' }}
        }}
      }},
      interaction: {{
        intersect: false,
        mode: 'index'
      }}
    }}
  }});
  charts.push(chart);
}}

// ===== BUILD UI =====
function buildNav() {{
  const nav = document.getElementById('segNav');
  SEGMENTS.forEach((seg, i) => {{
    const btn = document.createElement('button');
    btn.textContent = seg.name;
    btn.addEventListener('click', () => {{
      document.getElementById('seg-' + seg.id).scrollIntoView({{ behavior: 'smooth' }});
      focusSegment(i);
      updateActiveNav(i);
    }});
    nav.appendChild(btn);
  }});
  // "Show all" button
  const allBtn = document.createElement('button');
  allBtn.textContent = '\\U0001F5FA Alle';
  allBtn.addEventListener('click', () => {{
    resetMapView();
    updateActiveNav(-1);
  }});
  nav.appendChild(allBtn);
}}

function updateActiveNav(idx) {{
  const buttons = document.querySelectorAll('.seg-nav button');
  buttons.forEach((btn, i) => btn.classList.toggle('active', i === idx));
}}

function symToIcon(sym) {{
  switch(sym) {{
    case 'Lodge': return ['\\U0001F3D4', 'lodge'];
    case 'Hotel': return ['\\U0001F3E8', 'lodge'];
    case 'Shelter': return ['\\u26FA', 'shelter'];
    case 'Alert': return ['\\u26A0\\uFE0F', 'alert'];
    case 'Drinking Water': return ['\\U0001F4A7', 'water'];
    case 'Restaurant': return ['\\U0001F37D', 'restaurant'];
    default: return ['\\U0001F4CD', 'landmark'];
  }}
}}

function symToNorwegian(sym) {{
  switch(sym) {{
    case 'Lodge': return 'Hytte';
    case 'Hotel': return 'Hotell';
    case 'Shelter': return 'Bivakk/Ly';
    case 'Alert': return 'Klatrestige';
    case 'Drinking Water': return 'Vannkilde';
    case 'Restaurant': return 'Restaurant';
    default: return '';
  }}
}}

function formatTime(hours) {{
  const h = Math.floor(hours);
  const m = Math.round((hours - h) * 60);
  return h + 't ' + m + 'min';
}}

function buildSegmentCards() {{
  const container = document.getElementById('segments');

  SEGMENTS.forEach((seg, idx) => {{
    const card = document.createElement('div');
    card.className = 'seg-card';
    card.id = 'seg-' + seg.id;

    const d = seg.data;
    const canvasId = 'chart-' + seg.id;

    // Separate POIs by type
    const huts = seg.pois.filter(p => p.sym === 'Lodge' || p.sym === 'Hotel');
    const waters = seg.pois.filter(p => p.sym === 'Drinking Water');
    const alerts = seg.pois.filter(p => p.sym === 'Alert');
    const shelters = seg.pois.filter(p => p.sym === 'Shelter');
    const restaurants = seg.pois.filter(p => p.sym === 'Restaurant');

    let poisHTML = '';

    // Landmarks (from our hardcoded data)
    if (seg.landmarks && seg.landmarks.length > 0) {{
      poisHTML += '<div class="poi-section"><h4 onclick="togglePOI(this)">\\U0001F3D4\\uFE0F Landemerker</h4><ul class="poi-list">';
      seg.landmarks.forEach(lm => {{
        poisHTML += '<li class="poi-item"><span class="poi-icon landmark">\\U0001F3D4\\uFE0F</span><div><strong>' + lm.name + '</strong><br><span style="font-size:0.82rem;color:var(--text-muted);">' + lm.desc + '</span></div></li>';
      }});
      poisHTML += '</ul></div>';
    }}

    // Huts along segment
    if (huts.length > 0) {{
      poisHTML += '<div class="poi-section"><h4 onclick="togglePOI(this)">\\U0001F6D6 Hytter og overnatting</h4><ul class="poi-list">';
      huts.forEach(h => {{
        const [icon, cls] = symToIcon(h.sym);
        poisHTML += '<li class="poi-item"><span class="poi-icon ' + cls + '">' + icon + '</span><span>' + h.name + '</span><span class="poi-ele">' + Math.round(h.ele) + ' moh</span></li>';
      }});
      poisHTML += '</ul></div>';
    }}

    // Via Ferrata
    if (alerts.length > 0) {{
      poisHTML += '<div class="poi-section"><h4 onclick="togglePOI(this)">\\u26A0\\uFE0F Klatrestiger (Via Ferrata)</h4><ul class="poi-list">';
      alerts.forEach(a => {{
        poisHTML += '<li class="poi-item"><span class="poi-icon alert">\\u26A0\\uFE0F</span><span>' + a.name + '</span><span class="poi-ele">' + Math.round(a.ele) + ' moh</span></li>';
      }});
      poisHTML += '</ul></div>';
    }}

    // Shelters
    if (shelters.length > 0) {{
      poisHTML += '<div class="poi-section"><h4 onclick="togglePOI(this)">\\u26FA Bivakker og ly</h4><ul class="poi-list">';
      shelters.forEach(s => {{
        let extra = s.desc ? ' <em style="font-size:0.78rem;color:var(--text-muted);">(' + s.desc + ')</em>' : '';
        poisHTML += '<li class="poi-item"><span class="poi-icon shelter">\\u26FA</span><span>' + s.name + extra + '</span><span class="poi-ele">' + Math.round(s.ele) + ' moh</span></li>';
      }});
      poisHTML += '</ul></div>';
    }}

    // Water sources
    if (waters.length > 0) {{
      poisHTML += '<div class="poi-section"><h4 onclick="togglePOI(this)" class="collapsed">\\U0001F4A7 Vannkilder (' + waters.length + ')</h4><ul class="poi-list hidden">';
      waters.forEach(w => {{
        poisHTML += '<li class="poi-item"><span class="poi-icon water">\\U0001F4A7</span><span>Vannkilde</span><span class="poi-ele">' + Math.round(w.ele) + ' moh</span></li>';
      }});
      poisHTML += '</ul></div>';
    }}

    // Restaurants
    if (restaurants.length > 0) {{
      poisHTML += '<div class="poi-section"><h4 onclick="togglePOI(this)">\\U0001F37D\\uFE0F Restauranter</h4><ul class="poi-list">';
      restaurants.forEach(r => {{
        poisHTML += '<li class="poi-item"><span class="poi-icon restaurant">\\U0001F37D\\uFE0F</span><span>' + r.name + '</span><span class="poi-ele">' + Math.round(r.ele) + ' moh</span></li>';
      }});
      poisHTML += '</ul></div>';
    }}

    card.innerHTML = `
      <div class="seg-card-header" onclick="toggleCard(${{idx}})">
        <div>
          <h3>${{seg.name}}: ${{seg.from}} \\u2192 ${{seg.to}}</h3>
          <span class="seg-route">${{formatDist(d.dist)}} \\u2022 \\u2191${{formatElev(d.asc)}} \\u2193${{formatElev(d.desc)}} \\u2022 ~${{formatTime(d.timeH)}}</span>
        </div>
        <span class="seg-arrow" id="arrow-${{idx}}">\\u25BC</span>
      </div>
      <div class="seg-card-body" id="body-${{idx}}">
        <div class="stats-grid">
          <div class="stat-box"><span class="stat-val">${{formatDist(d.dist)}}</span><span class="stat-lbl">Avstand</span></div>
          <div class="stat-box ascent"><span class="stat-val">\\u2191 ${{formatElev(d.asc)}}</span><span class="stat-lbl">Stigning</span></div>
          <div class="stat-box descent"><span class="stat-val">\\u2193 ${{formatElev(d.desc)}}</span><span class="stat-lbl">Nedstigning</span></div>
          <div class="stat-box"><span class="stat-val">${{Math.round(d.minEle)}} m</span><span class="stat-lbl">Laveste punkt</span></div>
          <div class="stat-box"><span class="stat-val">${{Math.round(d.maxEle)}} m</span><span class="stat-lbl">H\\u00f8yeste punkt</span></div>
          <div class="stat-box"><span class="stat-val">~${{formatTime(d.timeH)}}</span><span class="stat-lbl">Estimert tid</span></div>
        </div>

        <div class="elevation-wrap">
          <canvas id="${{canvasId}}" height="160"></canvas>
        </div>

        <div class="landmark-desc">${{seg.description}}</div>

        ${{poisHTML}}

        <button class="btn-map" onclick="focusSegment(${{idx}}); document.getElementById('map').scrollIntoView({{behavior:'smooth',block:'center'}});">
          \\U0001F5FA Vis p\\u00e5 kart
        </button>
      </div>
    `;

    container.appendChild(card);
  }});

  // Initialize charts after DOM update
  requestAnimationFrame(() => {{
    SEGMENTS.forEach(seg => {{
      createElevationChart('chart-' + seg.id, seg);
    }});
  }});
}}

// ===== INTERACTIVITY =====
function toggleCard(idx) {{
  const body = document.getElementById('body-' + idx);
  const arrow = document.getElementById('arrow-' + idx);
  const isHidden = body.style.display === 'none';
  body.style.display = isHidden ? 'block' : 'none';
  arrow.style.transform = isHidden ? 'rotate(0deg)' : 'rotate(-90deg)';
}}

function togglePOI(header) {{
  header.classList.toggle('collapsed');
  const list = header.nextElementSibling;
  list.classList.toggle('hidden');
}}

// Scroll spy for nav
function setupScrollSpy() {{
  const observer = new IntersectionObserver((entries) => {{
    entries.forEach(entry => {{
      if (entry.isIntersecting) {{
        const id = parseInt(entry.target.id.replace('seg-', ''));
        const idx = SEGMENTS.findIndex(s => s.id === id);
        updateActiveNav(idx);
      }}
    }});
  }}, {{ threshold: 0.3, rootMargin: '-60px 0px 0px 0px' }});

  SEGMENTS.forEach(seg => {{
    const el = document.getElementById('seg-' + seg.id);
    if (el) observer.observe(el);
  }});
}}

// ===== INIT =====
function init() {{
  computeSegments();
  buildNav();
  initMap();
  buildSegmentCards();
  setupScrollSpy();
}}

document.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>'''

# Write the HTML file
output_path = os.path.join(SCRIPT_DIR, 'Alta Via 4 - Turguide.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

file_size = os.path.getsize(output_path)
print(f"Generated: {output_path}")
print(f"File size: {file_size / 1024:.1f} KB")
print("Done!")

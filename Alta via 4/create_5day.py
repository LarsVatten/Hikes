#!/usr/bin/env python3
"""Create a 5-day variant of the Alta Via 4 trail guide."""

import re

with open('Alta Via 4 - Turguide.html', 'r', encoding='utf-8') as f:
    content = f.read()

# New 5-day SEGMENTS definition
new_segments = r"""const SEGMENTS = [
        {
          id: 1,
          name: "Dag 1",
          from: "San Candido",
          to: "Rifugio Auronzo",
          endWpt: "Rifugio Auronzo",
          color: "#E74C3C",
          landmarks: [
            {
              name: "Haunold / Monte Baranci",
              desc: "Utsiktspunkt over Pustertal-dalen med panorama mot Sextner-Dolomittene."
            },
            {
              name: "Innichen / San Candido",
              desc: "Sjarmerende s\u00f8rtirolsk landsby med barokk stiftskirke fra 1200-tallet."
            },
            {
              name: "Tre Cime di Lavaredo (nordsiden)",
              desc: "Verdens mest ikoniske fjellformasjon i Dolomittene \u2013 tre majestetiske s\u00f8yler som reiser seg over 2999 moh. Unesco verdensarv."
            },
            {
              name: "Sextner Sonnenuhr",
              desc: "De tolv toppene i Sextner-Dolomittene som danner et naturlig solur."
            },
            {
              name: "Paternkofel / Monte Paterno",
              desc: "Dramatisk 2744 m h\u00f8y topp rett ved Locatelli-hytta, kjent fra f\u00f8rste verdenskrig."
            },
            {
              name: "Rifugio Tre Scarperi (Dreischusterh\u00fctte)",
              desc: "F\u00f8rste hytte p\u00e5 ruten, 1634 moh. Tradisjonell S\u00f8r-Tirol-hytte med panoramautsikt."
            }
          ],
          description:
            "En lang og ambisi\u00f8s f\u00f8rstedag! Fra San Candido (1175 m) g\u00e5r ruten s\u00f8rover gjennom skoger til Rifugio Tre Scarperi (1634 m), videre opp til Rifugio Antonio Locatelli (2398 m) med spektakul\u00e6r utsikt mot Tre Cime di Lavaredo fra nordsiden. Derfra fortsetter stien via Langalm og ned til Rifugio Auronzo (2313 m) ved foten av Tre Cime. En krevende dag med stor stigning, men bel\u00f8nningen er verdensklasse-panorama."
        },
        {
          id: 2,
          name: "Dag 2",
          from: "Rifugio Auronzo",
          to: "Rifugio Citt\u00e0 di Carpi",
          endWpt: "Rifugio Citt\u00e0 di Carpi",
          color: "#E67E22",
          landmarks: [
            {
              name: "Tre Cime di Lavaredo (s\u00f8rsiden)",
              desc: "Ruten passerer t\u00e6t forbi den s\u00f8rlige siden av Tre Cime \u2013 en helt annen og villere opplevelse."
            },
            {
              name: "Forcella Lavaredo",
              desc: "H\u00f8yt fjellpass (2454 m) med \u00e5pen utsikt mot Cadini-gruppen og Auronzo-dalen."
            },
            {
              name: "Cadini di Misurina",
              desc: "Spektakul\u00e6r gruppe av spisse kalktinder som gradvis \u00e5pner seg s\u00f8rover."
            }
          ],
          description:
            "Andre dag f\u00f8rer fra Rifugio Auronzo langs h\u00f8ydedraget forbi Rifugio Lavaredo og gjennom en utstyrt klatreseksjon (Via Ferrata B). Du passerer Rifugio Fonda Savio (2344 m) f\u00f8r ruten fortsetter s\u00f8rover til Rifugio Citt\u00e0 di Carpi (2111 m). Underveis har du fantastisk utsikt mot Cadini di Misurina. Medbring klatresele for Via Ferrata-seksjonen!"
        },
        {
          id: 3,
          name: "Dag 3",
          from: "Rifugio Citt\u00e0 di Carpi",
          to: "Rifugio Vandelli",
          endWpt: "Rifugio Vandelli",
          color: "#2ECC71",
          landmarks: [
            {
              name: "Monte Cristallo (3221 m)",
              desc: "En av de h\u00f8yeste toppene i Dolomittene, synlig mot nordvest. Massiv gletsjer p\u00e5 nordsiden."
            },
            {
              name: "Misurina-sj\u00f8en",
              desc: "Ikonisk alpesj\u00f8 p\u00e5 1754 moh, kjent for sitt speilbilde av Sorapiss og Cadini-tindene."
            },
            {
              name: "Sorapiss-gruppen",
              desc: "Dramatisk fjellmassiv dominert av Punta Sorapiss (3205 m) med imponerende glasialer."
            },
            {
              name: "Lago di Sorapiss",
              desc: "Eventyrlig turkis alpesj\u00f8 p\u00e5 1925 moh \u2013 en av Dolomittenes mest fotograferte sj\u00f8er."
            }
          ],
          description:
            "En variert dag med nedstigning og stigning. Fra Citt\u00e0 di Carpi (2111 m) g\u00e5r ruten ned til Misurina-omr\u00e5det via Albergo Cristallo (1372 m), den laveste overnatting p\u00e5 ruten. Derfra stiger stien opp igjen gjennom vakre alpeskoger mot Rifugio Vandelli (1931 m) ved foten av Sorapiss-massivet. Utsikten mot Monte Cristallo og Lago di Sorapiss er up\u00e5klagelig."
        },
        {
          id: 4,
          name: "Dag 4",
          from: "Rifugio Vandelli",
          to: "Rifugio Galassi",
          endWpt: "Rifugio Pietro Galassi",
          color: "#3498DB",
          landmarks: [
            {
              name: "Marmarole-kjeden",
              desc: "En av de mest avsidesliggende fjellkjedene i Dolomittene, med tinder opp til 2932 m. F\u00e6rre turister, villere natur."
            },
            {
              name: "Croda Marcora (2932 m)",
              desc: "Marmarole-kjedens h\u00f8yeste topp, synlig som en mektig veiviser gjennom hele etappen."
            },
            {
              name: "Bivacco Slataper (2575 m)",
              desc: "H\u00f8yeste punkt p\u00e5 hele Alta Via 4 \u2013 en enkel bivakk med fantastisk panorama."
            },
            {
              name: "Val d\u2019Ansiei",
              desc: "Vakker alpin dal som strekker seg gjennom Marmarole-gruppen med rike blomsterenger."
            }
          ],
          description:
            "Den mest krevende dagen p\u00e5 hele Alta Via 4! Fra Vandelli g\u00e5r ruten over to Via Ferrata-seksjoner (grad C og A), forbi Bivacco Comici og opp til rutens h\u00f8yeste punkt ved Bivacco Slataper (2575 m). Klatresele og hjelm er obligatorisk. Deretter lang nedstigning via Rifugio San Marco (1818 m) og Rifugio Scotter-Palatini (1571 m) f\u00f8r siste stigning til Rifugio Galassi (2014 m). Kun for erfarne fjellvandrere."
        },
        {
          id: 5,
          name: "Dag 5",
          from: "Rifugio Galassi",
          to: "Pieve di Cadore",
          endWpt: null,
          color: "#9B59B6",
          landmarks: [
            {
              name: "Monte Antelao (3264 m)",
              desc: "\u00abDolomittenes Konge\u00bb \u2013 den nest h\u00f8yeste toppen i Dolomittene. Dominerer horisonten med sin majestetiske pyramideform."
            },
            {
              name: "Monte Pelmo (3168 m)",
              desc: "Massiv \u00abtafelberg\u00bb synlig mot vest \u2013 en av Dolomittenes mest gjenkjennelige silhuetter."
            },
            {
              name: "Centro Cadore-panorama",
              desc: "Utsikt over den historiske Cadore-dalen med sj\u00f8en Lago di Centro Cadore."
            },
            {
              name: "Pieve di Cadore",
              desc: "F\u00f8deby for renessansemaleren Tizian (Titian). Sjarmerende gamlebydel med historiske kirker og museer."
            }
          ],
          description:
            "Siste dag \u2013 en lang nedstigning til sivilisasjonen! Fra Galassi g\u00e5r ruten via Rifugio Capanna degli Alpini (1397 m), deretter opp med en Via Ferrata B-seksjon forbi Rifugio Antelao (1797 m). Monte Antelao (3264 m), \u00abDolomittenes Konge\u00bb, dominerer utsikten. Via Rifugio Costa Piana (1568 m) og Capanna Tita Panciera f\u00f8rer stien ned gjennom skoger til Pieve di Cadore (884 m). En verdig avslutning p\u00e5 denne episke fjellturen."
        }
      ];"""

# Replace SEGMENTS block
old_start = content.find('const SEGMENTS = [')
# Find the end: look for the SEG_COLORS line or the next const after SEGMENTS
old_end = content.find('// Segment color palette')
if old_end == -1:
    # Fallback: find the closing '];\n' pattern after the segments
    old_end = content.find('const SEG_COLORS')

old_block = content[old_start:old_end]
content = content[:old_start] + new_segments + '\n\n      ' + content[old_end:]

# Update title
content = content.replace(
    '<title>Alta Via 4 \u2014 Turguide</title>',
    '<title>Alta Via 4 \u2014 5-dagers turguide</title>'
)

# Update hero section subtitle if present
content = content.replace(
    'Interaktiv turguide gjennom Dolomittene',
    '5-dagers turguide gjennom Dolomittene'
)

# Update days count
content = content.replace(
    '<span class="val" id="total-days">5</span><span class="lbl">Etapper</span>',
    '<span class="val" id="total-days">5</span><span class="lbl">Dager</span>'
)

# Write new file
with open('Alta Via 4 - 5 dager.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Created: Alta Via 4 - 5 dager.html')
print('Size:', len(content), 'chars')


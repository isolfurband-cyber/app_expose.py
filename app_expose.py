from datetime import datetime
from io import BytesIO
import os
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(
    page_title="KARE-Immobilien – Jobcenter Exposé Generator",
    page_icon="📄",
    layout="centered",
)

# --- OFFIZIELLE GERAER RICHTLINIEN (Gültig ab 01.01.2026) ---
RICHTLINIEN_GERA = {
    1: {"max_qm": 45, "max_bruttokalt": 320.40},
    2: {"max_qm": 60, "max_bruttokalt": 405.00},
    3: {"max_qm": 75, "max_bruttokalt": 495.00},
    4: {"max_qm": 90, "max_bruttokalt": 581.40},
    5: {"max_qm": 105, "max_bruttokalt": 765.45},
}
WEITERE_PERSON_QM = 15
WEITERE_PERSON_BETRAG = 109.35

# Richtwerte Heizkosten (Höchstwerte je m² angemessener Wohnfläche laut Bundesheizspiegel in der Richtlinie)
HEIZKOSTEN_RICHTWERTE = {
    "Erdgas": 23.21,  # EUR pro m² im Jahr (Kategorie 80-150 m²)
    "Fernwärme": 32.51,
    "Heizöl": 26.11,
    "Wärmepumpe": 21.11,
    "Holzpellets / Sonstige": 14.81,
}

# --- PDF GENERIERUNGS-FUNKTION ---


def generate_pdf(
    strasse,
    hausnummer,
    plz_ort,
    personen,
    raeume,
    qm,
    kaltmiete,
    kalte_bk,
    bruttokalt,
    heizkosten,
    bruttowarm,
    energietraeger,
    angemessen_kalt,
    max_erlaubt_kalt,
):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Briefkopf / Absender
    c.setFont("Helvetica-Bold", 10)
    c.drawString(
        50,
        height - 40,
        "KARE-Immobilien | Talstr. 32 | 07545 Gera | Tel.: 0365 / 800 49 37",
    )
    c.setLineWidth(1)
    c.line(50, height - 48, width - 50, height - 48)

    # Empfänger (Jobcenter)
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 75, "An das")
    c.drawString(50, height - 90, "Jobcenter Gera")
    c.drawString(50, height - 105, "Leistungsabteilung / Unterkunft")

    # Datum
    aktuelles_datum = datetime.now().strftime("%d.%m.%Y")
    c.drawRightString(width - 50, height - 75, f"Gera, den {aktuelles_datum}")

    # Titel
    c.setFont("Helvetica-Bold", 13)
    c.drawString(
        50, height - 140, "Mietangebot / Wohnungsexpose' zur Vorlage beim Jobcenter"
    )

    c.setFont("Helvetica", 10)
    c.drawString(
        50,
        height - 165,
        "Sehr geehrte Damen und Herren,",
        suppress_warnings=True,
    )
    c.drawString(
        50,
        height - 180,
        "für den oben genannten Mietinteressenten bieten wir hiermit folgende Mietwohnung an:",
    )

    # Box mit Objektdaten
    c.rect(50, height - 310, width - 100, 110)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(70, height - 205, "Objektdaten & Anschrift:")
    c.setFont("Helvetica", 10)
    c.drawString(
        70, height - 225, f"Straße & Hausnummer: {strasse} {hausnummer}"
    )
    c.drawString(70, height - 242, f"Ort: {plz_ort}")
    c.drawString(
        70, height - 259, f"Wohnungsgröße: {qm} m² ({raeume} Räume)"
    )
    c.drawString(70, height - 276, f"Haushaltsgröße: {personen} Person(en)")

    # Finanzielle Details & Angemessenheit
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 335, "Kosten der Unterkunft (KdU):")
    c.setFont("Helvetica", 10)
    c.drawString(
        70, height - 355, f"Nettokaltmiete (Grundmiete): {kaltmiete:.2f} EUR"
    )
    c.drawString(
        70, height - 372, f"Kalte Betriebskosten: {kalte_bk:.2f} EUR"
    )
    c.setFont("Helvetica-Bold", 10)
    c.drawString(
        70, height - 392, f"Bruttokaltmiete (Summe): {bruttokalt:.2f} EUR"
    )

    c.setFont("Helvetica", 10)
    c.drawString(
        70,
        height - 412,
        f"Heizkosten / Warme Betriebskosten: {heizkosten:.2f} EUR (Heizungsart:"
        f" {energietraeger})",
    )
    c.setFont("Helvetica-Bold", 10)
    c.drawString(70, height - 432, f"Gesamte Bruttowarmmiete: {bruttowarm:.2f} EUR")

    # Prüf-Ergebnis
    c.setFont("Helvetica-Bold", 10)
    if angemessen_kalt:
        c.setFillColorRGB(0, 0.5, 0)
        ergebnis_text = (
            f"Prüfung Bruttokaltmiete nach Richtlinie Gera 2026: ANGESESSEN"
            f" (Höchstgrenze: {max_erlaubt_kalt:.2f} EUR)"
        )
    else:
        c.setFillColorRGB(0.8, 0, 0)
        ergebnis_text = (
            f"Prüfung Bruttokaltmiete nach Richtlinie Gera 2026: ÜBERSTEIGT"
            f" RICHTWERT (Höchstgrenze: {max_erlaubt_kalt:.2f} EUR)"
        )

    c.drawString(50, height - 470, ergebnis_text)
    c.setFillColorRGB(0, 0, 0)

    # Hinweis
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(
        50,
        height - 510,
        "Hinweis: Gemäß Richtlinie wird die Angemessenheit primär über die"
        " Bruttokaltmiete",
    )
    c.drawString(
        50,
        height - 525,
        "sowie den Bundesheizspiegel für die Heizkosten bewertet.",
    )

    # Unterschrift
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 575, "Mit freundlichen Grüßen")
    c.drawString(50, height - 610, "KARE-Immobilien")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# --- BENUTZEROBERFLÄCHE (STREAMLIT) ---

st.markdown("### 🏢 KARE-Immobilien — Jobcenter Exposé & Angemessenheitsprüfer")
st.markdown("Prüfung nach dem **Leitfaden der Stadt Gera (gültig ab 01.01.2026)**[cite: 1].")

with st.form("expose_form"):
    st.subheader("1. Objektdaten")
    col1, col2 = st.columns(2)
    with col1:
        strasse = st.text_input("Straße", "Talstr.")
        hausnummer = st.text_input("Hausnummer", "32")
    with col2:
        plz_ort = st.text_input("PLZ / Ort", "07545 Gera")

    st.subheader("2. Mieter- & Wohnungsdaten")
    col3, col4, col5 = st.columns(3)
    with col3:
        personen = st.number_input(
            "Anzahl Personen", min_value=1, max_value=15, value=1
        )
    with col4:
        raeume = st.number_input(
            "Anzahl Räume", min_value=1, max_value=10, value=2
        )
    with col5:
        qm = st.number_input("Wohnfläche in m²", min_value=10.0, value=45.0)

    st.subheader("3. Finanzielle Angaben (Miete & Nebenkosten)")
    col6, col7, col8 = st.columns(3)
    with col6:
        kaltmiete = st.number_input("Nettokaltmiete (EUR)", value=220.0)
    with col7:
        kalte_bk = st.number_input("Kalte Betriebskosten (EUR)", value=80.0)
    with col8:
        heizkosten = st.number_input(
            "Heizkosten / Warme BK (EUR)", value=70.0
        )

    st.subheader("4. Heizungsart (für Richtwert-Check)")
    energietraeger = st.selectbox(
        "Hauptenergieträger",
        ["Erdgas", "Fernwärme", "Heizöl", "Wärmepumpe", "Holzpellets / Sonstige"],
    )

    submitted = st.form_submit_button(
        "Prüfen & Exposé als PDF generieren"
    )

if submitted:
    # Berechnungen
    bruttokalt = kaltmiete + kalte_bk
    bruttowarm = bruttokalt + heizkosten

    # Richtwert ermitteln basierend auf der offiziellen Tabelle für Bruttokaltmiete
    if personen <= 5:
        max_qm_erlaubt = RICHTLINIEN_GERA[personen]["max_qm"]
        max_brutto_erlaubt = RICHTLINIEN_GERA[personen]["max_bruttokalt"]
    else:
        max_qm_erlaubt = 105 + (personen - 5) * WEITERE_PERSON_QM
        max_brutto_erlaubt = 765.45 + (personen - 5) * WEITERE_PERSON_BETRAG

    # Angemessenheitsprüfung
    is_angemessen_kalt = bruttokalt <= max_brutto_erlaubt

    st.markdown("---")
    st.subheader("📊 Prüfungsergebnis & Kostenübersicht:")

    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric(label="Nettokaltmiete", value=f"{kaltmiete:.2f} EUR")
    with col_res2:
        st.metric(label="Kalte Betriebskosten", value=f"{kalte_bk:.2f} EUR")
    with col_res3:
        st.metric(label="Bruttokaltmiete", value=f"{bruttokalt:.2f} EUR")

    col_res4, col_res5 = st.columns(2)
    with col_res4:
        st.metric(label="Heizkosten (warm)", value=f"{heizkosten:.2f} EUR")
    with col_res5:
        st.metric(label="Gesamt-Bruttowarmmiete", value=f"{bruttowarm:.2f} EUR")

    st.markdown("### Angemessenheits-Check (Jobcenter Gera):")
    if is_angemessen_kalt:
        st.success(
            f"✅ **Bruttokaltmiete ist ANGESESSEN!** Mit {bruttokalt:.2f} EUR"
            f" liegt sie unter dem Höchstwert von {max_brutto_erlaubt:.2f} EUR"
            f" für einen {personen}-Personen-Haushalt[cite: 1]."
        )
    else:
        st.error(
            f"❌ **Bruttokaltmiete überschreitet den Richtwert** für einen"
            f" {personen}-Personen-Haushalt um"
            f" {(bruttokalt - max_brutto_erlaubt):.2f} EUR (Erlaubt sind max."
            f" {max_brutto_erlaubt:.2f} EUR)[cite: 1]."
        )

    # PDF Download Button bereitstellen
    pdf_file = generate_pdf(
        strasse,
        hausnummer,
        plz_ort,
        personen,
        raeume,
        qm,
        kaltmiete,
        kalte_bk,
        bruttokalt,
        heizkosten,
        bruttowarm,
        energietraeger,
        is_angemessen_kalt,
        max_brutto_erlaubt,
    )

    st.download_button(
        label="📥 Offizielles Jobcenter-Exposé (PDF) herunterladen",
        data=pdf_file,
        file_name=f"Expose_{strasse}_{hausnummer}_Gera.pdf",
        mime="application/pdf",
    )

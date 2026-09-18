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


# Hilfsfunktion für deutsches Zahlenformat (Komma statt Punkt)
def fmt(val):
    return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Hilfsfunktion um Text-Eingaben mit Komma sicher in Float umzuwandeln
def parse_de_float(val_str, default=0.0):
    try:
        cleaned = val_str.strip().replace(".", "").replace(",", ".")
        return float(cleaned)
    except ValueError:
        return default


# --- PDF GENERIERUNGS-FUNKTION ---


def generate_pdf(
    strasse,
    hausnummer,
    plz_ort,
    mieter_name,
    personen,
    raeume,
    qm,
    kaltmiete,
    kalte_bk,
    bruttokalt,
    heizkosten,
    bruttowarm,
    kaution,
    energietraeger,
    angemessen_kalt,
    max_erlaubt_kalt,
):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Logo oben links einfügen (sucht nach logo.png oder kare_logo.png im Repository)
    logo_path = "logo.png"
    if not os.path.exists(logo_path) and os.path.exists("kare_logo.png"):
        logo_path = "kare_logo.png"

    if os.path.exists(logo_path):
        c.drawImage(logo_path, 50, height - 52, width=110, height=35, preserveAspectRatio=True, mask='auto')

    # Briefkopf / Absender-Text rechts daneben
    c.setFont("Helvetica-Bold", 9)
    c.drawString(
        170,
        height - 35,
        "KARE-Immobilien | Talstr. 32 | 07545 Gera | Tel.: 0365 / 800 49 37",
    )
    c.setLineWidth(1)
    c.line(50, height - 60, width - 50, height - 60)

    # Empfänger (Jobcenter)
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 85, "An das")
    c.drawString(50, height - 100, "Jobcenter Gera")
    c.drawString(50, height - 115, "Leistungsabteilung / Unterkunft")

    # Datum
    aktuelles_datum = datetime.now().strftime("%d.%m.%Y")
    c.drawRightString(width - 50, height - 85, f"Gera, den {aktuelles_datum}")

    # Titel
    c.setFont("Helvetica-Bold", 13)
    c.drawString(
        50, height - 150, "Mietangebot / Wohnungsexpose' zur Vorlage beim Jobcenter"
    )

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 175, "Sehr geehrte Damen und Herren,")
    
    # Text mit Mietername
    mieter_text = mieter_name if mieter_name.strip() else "[Name des Mieters]"
    c.drawString(
        50,
        height - 190,
        f"für den Mietinteressenten {mieter_text} bieten wir hiermit folgende Mietwohnung an:",
    )

    # Box mit Objektdaten
    c.rect(50, height - 350, width - 100, 130)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(70, height - 215, "Objektdaten & Interessent:")
    c.setFont("Helvetica", 10)
    c.drawString(70, height - 235, f"Mietinteressent(in): {mieter_text}")
    c.drawString(
        70, height - 255, f"Straße & Hausnummer: {strasse} {hausnummer}"
    )
    c.drawString(70, height - 275, f"Ort: {plz_ort}")
    c.drawString(
        70, height - 295, f"Wohnungsgröße: {fmt(qm)} m² ({raeume} Räume)"
    )
    c.drawString(70, height - 315, f"Haushaltsgröße: {personen} Person(en)")

    # Finanzielle Details & Angemessenheit
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 375, "Kosten der Unterkunft (KdU):")
    c.setFont("Helvetica", 10)
    c.drawString(
        70, height - 395, f"Nettokaltmiete (Grundmiete): {fmt(kaltmiete)} EUR"
    )
    c.drawString(
        70, height - 413, f"Kalte Betriebskosten: {fmt(kalte_bk)} EUR"
    )
    c.setFont("Helvetica-Bold", 10)
    c.drawString(
        70, height - 433, f"Bruttokaltmiete (Summe): {fmt(bruttokalt)} EUR"
    )

    c.setFont("Helvetica", 10)
    c.drawString(
        70,
        height - 453,
        f"Heizkosten / Warme Betriebskosten: {fmt(heizkosten)} EUR"
        f" (Heizungsart: {energietraeger})",
    )
    c.setFont("Helvetica-Bold", 10)
    c.drawString(
        70, height - 473, f"Gesamte Bruttowarmmiete: {fmt(bruttowarm)} EUR"
    )
    c.drawString(70, height - 491, f"Mietkaution: {fmt(kaution)} EUR")

    # Prüf-Ergebnis
    c.setFont("Helvetica-Bold", 10)
    if angemessen_kalt:
        c.setFillColorRGB(0, 0.5, 0)
        ergebnis_text = (
            f"Prüfung Bruttokaltmiete nach Richtlinie Gera 2026: ANGESESSEN"
            f" (Höchstgrenze: {fmt(max_erlaubt_kalt)} EUR)"
        )
    else:
        c.setFillColorRGB(0.8, 0, 0)
        ergebnis_text = (
            f"Prüfung Bruttokaltmiete nach Richtlinie Gera 2026: ÜBERSTEIGT"
            f" RICHTWERT (Höchstgrenze: {fmt(max_erlaubt_kalt)} EUR)"
        )

    c.drawString(50, height - 530, ergebnis_text)
    c.setFillColorRGB(0, 0, 0)

    # Hinweis
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(
        50,
        height - 565,
        "Hinweis: Gemäß Richtlinie wird die Angemessenheit primär über die"
        " Bruttokaltmiete",
    )
    c.drawString(
        50,
        height - 580,
        "sowie den Bundesheizspiegel für die Heizkosten bewertet.",
    )

    # Unterschrift
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 625, "Mit freundlichen Grüßen")
    c.drawString(50, height - 660, "KARE-Immobilien")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# --- BENUTZEROBERFLÄCHE (STREAMLIT) ---

st.markdown("### 🏢 KARE-Immobilien — Jobcenter Exposé & Angemessenheitsprüfer")
st.markdown(
    "Prüfung nach dem **Leitfaden der Stadt Gera (gültig ab 01.01.2026)**."
)

with st.form("expose_form"):
    st.subheader("1. Objektdaten")
    col1, col2 = st.columns(2)
    with col1:
        strasse = st.text_input("Straße", "Talstr.")
        hausnummer = st.text_input("Hausnummer", "32")
    with col2:
        plz_ort = st.text_input("PLZ / Ort", "07545 Gera")

    st.subheader("2. Mieter- & Wohnungsdaten")
    
    mieter_name = st.text_input("Name des Mietinteressenten", placeholder="Vor- und Nachname")

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
        qm_input = st.text_input("Wohnfläche in m²", value="45,00")

    st.subheader("3. Finanzielle Angaben (Miete, Nebenkosten & Kaution)")
    col6, col7, col8, col9 = st.columns(4)
    with col6:
        kaltmiete_input = st.text_input("Nettokaltmiete (€)", value="220,00")
    with col7:
        kalte_bk_input = st.text_input("Kalte Betriebskosten (€)", value="80,00")
    with col8:
        heizkosten_input = st.text_input("Heizkosten (€)", value="70,00")
    with col9:
        kaution_input = st.text_input("Kaution (€)", value="660,00")

    st.subheader("4. Heizungsart (für Richtwert-Check)")
    energietraeger = st.selectbox(
        "Hauptenergieträger",
        ["Erdgas", "Fernwärme", "Heizöl", "Wärmepumpe", "Holzpellets / Sonstige"],
    )

    submitted = st.form_submit_button(
        "Prüfen & Exposé als PDF generieren"
    )

if submitted:
    qm = parse_de_float(qm_input, 45.0)
    kaltmiete = parse_de_float(kaltmiete_input, 220.0)
    kalte_bk = parse_de_float(kalte_bk_input, 80.0)
    heizkosten = parse_de_float(heizkosten_input, 70.0)
    kaution = parse_de_float(kaution_input, 660.0)

    bruttokalt = kaltmiete + kalte_bk
    bruttowarm = bruttokalt + heizkosten

    if personen <= 5:
        max_qm_erlaubt = RICHTLINIEN_GERA[personen]["max_qm"]
        max_brutto_erlaubt = RICHTLINIEN_GERA[personen]["max_bruttokalt"]
    else:
        max_qm_erlaubt = 105 + (personen - 5) * WEITERE_PERSON_QM
        max_brutto_erlaubt = 765.45 + (personen - 5) * WEITERE_PERSON_BETRAG

    is_angemessen_kalt = bruttokalt <= max_brutto_erlaubt

    st.markdown("---")
    st.subheader("📊 Prüfungsergebnis & Kostenübersicht:")

    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric(label="Nettokaltmiete", value=f"{fmt(kaltmiete)} EUR")
    with col_res2:
        st.metric(label="Kalte Betriebskosten", value=f"{fmt(kalte_bk)} EUR")
    with col_res3:
        st.metric(label="Bruttokaltmiete", value=f"{fmt(bruttokalt)} EUR")

    col_res4, col_res5, col_res6 = st.columns(3)
    with col_res4:
        st.metric(label="Heizkosten", value=f"{fmt(heizkosten)} EUR")
    with col_res5:
        st.metric(label="Bruttowarmmiete", value=f"{fmt(bruttowarm)} EUR")
    with col_res6:
        st.metric(label="Kaution", value=f"{fmt(kaution)} EUR")

    st.markdown("### Angemessenheits-Check (Jobcenter Gera):")
    if is_angemessen_kalt:
        st.success(
            f"✅ **Bruttokaltmiete ist ANGESESSEN!** Mit {fmt(bruttokalt)} EUR"
            f" liegt sie unter dem Höchstwert von {fmt(max_brutto_erlaubt)} EUR"
            f" für einen {personen}-Personen-Haushalt."
        )
    else:
        st.error(
            f"❌ **Bruttokaltmiete überschreitet den Richtwert** für einen"
            f" {personen}-Personen-Haushalt um"
            f" {fmt(bruttokalt - max_brutto_erlaubt)} EUR (Erlaubt sind max."
            f" {fmt(max_brutto_erlaubt)} EUR)."
        )

    pdf_file = generate_pdf(
        strasse,
        hausnummer,
        plz_ort,
        mieter_name,
        personen,
        raeume,
        qm,
        kaltmiete,
        kalte_bk,
        bruttokalt,
        heizkosten,
        bruttowarm,
        kaution,
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

import requests
import xml.etree.ElementTree as ET
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT
from datetime import datetime, timedelta
import pytz
import os

def semana_iso_siguiente():
    hoy = datetime.now(pytz.timezone("Europe/Madrid"))
    semana_actual = hoy.isocalendar().week
    return semana_actual + 1

def generar_pdf():
    base_url = "https://www.aemet.es"

    municipalities = {
        "Zaragoza": "/xml/municipios/localidad_50297.xml",
        "Cariñena": "/xml/municipios/localidad_50073.xml",
        "Calamocha": "/xml/municipios/localidad_44050.xml",
        "Huesca": "/xml/municipios/localidad_22125.xml",
        "Jaca": "/xml/municipios/localidad_22130.xml",
        "Canfranc": "/xml/municipios/localidad_22078.xml",
        "Caspe": "/xml/municipios/localidad_50074.xml",
        "Fayón": "/xml/municipios/localidad_50105.xml",
        "Lleida": "/xml/municipios/localidad_25120.xml",
        "Calaf": "/xml/municipios/localidad_08031.xml",
        "Vinaixa": "/xml/municipios/localidad_25255.xml"
    }

    semana = semana_iso_siguiente()
    os.makedirs("outputs", exist_ok=True)

    pdf_file = f"outputs/Predicción meteorológica semana {semana}.pdf"
    titulo = f"Predicción meteorológica semana {semana}"

    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        leftMargin=1.3 * cm,
        rightMargin=0.8 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Titulo", fontSize=12, alignment=1))
    styles.add(ParagraphStyle(name="Subtitulo", fontSize=8, alignment=TA_LEFT))

    story = []
    story.append(Paragraph(f"<b>{titulo}</b>", styles["Titulo"]))
    story.append(Spacer(1, 10))

    bloques = 0

    for nombre, path in municipalities.items():
        if bloques == 4:
            story.append(PageBreak())
            bloques = 0

        xml = requests.get(base_url + path)
        xml.raise_for_status()
        root = ET.fromstring(xml.content)

        story.append(Paragraph(f"<b>{nombre}</b>", styles["Subtitulo"]))
        story.append(Spacer(1, 4))

        tabla = [["Fecha", "Tª. Máx", "Tª. Mín", "Prob. precip. (%)", "Cielo", "Dir. viento", "Viento km/h"]]

        for dia in root.findall(".//dia"):
            fecha = dia.get("fecha", "-")
            fecha = "/".join(reversed(fecha.split("-")))

            def t(x): return x.text if x is not None else "-"

            tabla.append([
                fecha,
                t(dia.find(".//maxima")),
                t(dia.find(".//minima")),
                t(dia.find(".//prob_precipitacion")),
                dia.find(".//estado_cielo").get("descripcion", "-"),
                t(dia.find(".//viento/direccion")),
                t(dia.find(".//viento/velocidad")),
            ])

        t_obj = Table(tabla, colWidths=[2*cm,1.02*cm,1.02*cm,2.02*cm,5*cm,1.6*cm,1.8*cm])
        t_obj.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("FONTSIZE", (0,0), (-1,-1), 7),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ]))

        story.append(t_obj)
        story.append(Spacer(1, 12))
        bloques += 1

    doc.build(story)
    return pdf_file

if __name__ == "__main__":
    generar_pdf()

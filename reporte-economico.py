import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from datetime import datetime

def cargar_datos_json(filename="reporte.json"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return {}

def dibujar_costo_maestria(c, width, y_pos, datos):
    """Dibuja la sección de costos de la maestría en el PDF"""
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_pos, "COSTOS DE LA MAESTRÍA")
    y_pos -= 20

    c.setFont("Helvetica", 11)
    datos_costos = [
        ("COSTO PENSIÓN", f"S/ {datos.get('costo_pension', 0):.2f}", f"{datos.get('num_cuotas', 0)} CUOTAS X S/ {datos.get('monto_pension', 0):.2f}"),
        ("MATRÍCULA", f"S/ {datos.get('costo_matricula', 0):.2f}", f"{datos.get('num_matriculas', 0)} MATRÍCULAS X S/ {datos.get('monto_matricula', 0):.2f}"),
        ("PAGOS PENSIÓN X CICLO", f"{datos.get('pagos_por_ciclo', 0)} CUOTAS", ""),
        ("COSTO TOTAL MAESTRÍA", f"S/ {datos.get('costo_total', 0):.2f}", ""),
        ("PENSIÓN A LA FECHA", f"{datos.get('num_cuotas', 0)} CUOTAS", ""),
        ("MATRÍCULAS A LA FECHA", f"{datos.get('num_matriculas', 0)} MATRÍCULAS", "")
    ]

    for concepto, monto, detalle in datos_costos:
        c.drawString(50, y_pos, concepto)
        c.drawString(250, y_pos, monto)
        c.drawString(400, y_pos, detalle)
        y_pos -= 20
    
    return y_pos - 20

def crear_tabla(c, title, table_data, y_pos, page_width):
    """Crea y dibuja una tabla en el PDF"""
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(page_width / 2, y_pos, title)
    
    table = Table(table_data)
    table.setStyle(TableStyle([ 
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    table_width, table_height = table.wrapOn(c, 0, 0)
    x_pos = (page_width - table_width) / 2
    table.drawOn(c, x_pos, y_pos - table_height - 20)

    return y_pos - table_height - 40

def agregar_firma(c, width, y_pos):
    """Agrega una sección para la firma centrada en la parte inferior del reporte"""
    c.setFont("Helvetica-Bold", 12)
    
    # Texto de la firma centrado
    c.drawCentredString(width / 2, y_pos, "Firma del Responsable:")
    
    # Espacio para la firma centrado
    c.setLineWidth(1)
    c.line(20, y_pos - 20, width - 50, y_pos - 20)  # Línea para la firma
    
    # Nombre, cargo y fecha centrados
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, y_pos - 40, "Nombre: ________________________________")#ejemplo
    c.drawCentredString(width / 2, y_pos - 60, "Cargo: ________________________________")
    c.drawCentredString(width / 2, y_pos - 80, "Fecha: ________________________________")
    
    return y_pos - 100

def generar_reporte_economico(datos, filename="reporte_economico_mejorado.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Encabezado
    c.setFillColor(colors.darkgrey)
    c.rect(0, height - 80, width, 80, fill=True)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 35, "UNIVERSIDAD NACIONAL DE LA AMAZONIA PERUANA")
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(width / 2, height - 55, "ESCUELA DE POSTGRADO JOSE TORRES VASQUEZ")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, height - 75, "REPORTE ECONÓMICO")

    # Información básica
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    y_position = height - 100
    c.drawString(50, y_position, f"INFORME ECONÓMICO N° -2025-OAE-EPG-UNAP")
    y_position -= 20
    c.drawString(50, y_position, f"ALUMNO: {datos['alumno']}")
    y_position -= 20
    c.drawString(50, y_position, f"PROGRAMA: {datos['programa']}")
    y_position -= 20
    c.drawString(50, y_position, f"PROMOCIÓN: {datos['promocion']}")
    y_position -= 40

    # Dibujar costos de la maestría
    y_position = dibujar_costo_maestria(c, width, y_position, datos)

    # Tablas
    tablas = [
        ("PENSIÓN", [["N°", "AÑO", "FECHA", "COD. BCO.", "CUOTAS", "CONCEPTO", "PAGO"]] +
         [[p["n"], p["año"], p["fecha"], p["codigo"], p["cuotas"], p["concepto"], p["monto"]] for p in datos['historial_pagos']]), 
        ("MATRÍCULA", [["CONCEPTO", "MONTO"]] +
         [[p["concepto"], p["monto"]] for p in datos['pensiones'] if p["concepto"] == "Matrícula"]),
        ("REPORTE INFORMATIVO DE DEUDAS", [["CONCEPTO", "MONTO PENDIENTE"]] +
         [[d["concepto"], d["monto"]] for d in datos['deudas']])
    ]

    for titulo, data in tablas:
        if y_position < 200:
            c.showPage()
            y_position = height - 50
        y_position = crear_tabla(c, titulo, data, y_position, width)

    # Agregar la sección de firma
    y_position = agregar_firma(c, width, y_position)

    c.save()
    print(f"📄 Reporte generado: {filename}")

# Cargar datos y generar reporte
datos_json = cargar_datos_json("reporte.json")
if datos_json:
    generar_reporte_economico(datos_json)

#python reporte-economico.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="Control de Transporte y Casetas", layout="wide")

st.title("🚚 Control de Flota y Análisis de Operadores")
st.write("Registra los datos del vehículo y casetas para generar el reporte en PDF para tu jefe.")

# --- FORMULARIO DE INGRESO DE DATOS ---
st.header("1. Registro de Viaje y Combustible")
col1, col2, col3 = st.columns(3)

with col1:
    operador = st.text_input("Nombre del Operador", "Juan Pérez")
    eco = st.text_input("Unidad / Placa", "28-BE-4K")
    fecha = st.date_input("Fecha del Viaje")

with col2:
    litros_inicio = st.number_input("Combustible Inicial (L)", value=388.16, step=0.1)
    litros_fin = st.number_input("Combustible Final (L)", value=308.30, step=0.1)
    km_recorridos = st.number_input("Kilómetros Recorridos (Km)", value=250.0, step=1.0)

with col3:
    num_casetas = st.number_input("Número de Casetas Pasadas", value=4, step=1)
    gasto_iave = st.number_input("Gasto Total IAVE / Casetas ($)", value=680.0, step=10.0)
    evaluacion_ruta = st.selectbox("Evaluación de Toma de Decisiones", ["Ruta Óptima / Buenan Decisión", "Ruta Con Desvíos", "Gasto Excesivo en Peaje"])

# --- CÁLCULOS AUTOMÁTICOS ---
litros_consumidos = round(litros_inicio - litros_fin, 2)
rendimiento = round(km_recorridos / litros_consumidos, 2) if litros_consumidos > 0 else 0
costo_caseta_km = round(gasto_iave / km_recorridos, 2) if km_recorridos > 0 else 0

st.subheader("📊 Métricas Calculadas del Viaje")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Litros Consumidos", f"{litros_consumidos} L")
m2.metric("Rendimiento", f"{rendimiento} Km/L")
m3.metric("Gasto Casetas", f"${gasto_iave} MXN")
m4.metric("Costo Caseta/Km", f"${costo_caseta_km} MXN")

st.markdown("---")

# --- CLASE PARA GENERAR EL PDF ---
class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.set_fill_color(30, 60, 90)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, "  REPORTE EJECUTIVO DE RENDIMIENTO Y PEAJES", ln=True, fill=True)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

def generar_pdf():
    pdf = PDFReport()
    pdf.add_page()
    
    # Información General
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Detalles del Viaje - Fecha: {fecha}", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, f"Operador: {operador} | Unidad: {eco}", ln=True)
    pdf.cell(0, 6, f"Evaluacion de Ruta: {evaluacion_ruta}", ln=True)
    pdf.ln(5)

    # Tabla de Resumen
    pdf.set_font("Arial", "B", 11)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(95, 8, "Concepto", border=1, fill=True)
    pdf.cell(95, 8, "Valor", border=1, fill=True, ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.cell(95, 7, "Combustible Inicial", border=1)
    pdf.cell(95, 7, f"{litros_inicio} Litros", border=1, ln=True)
    pdf.cell(95, 7, "Combustible Final", border=1)
    pdf.cell(95, 7, f"{litros_fin} Litros", border=1, ln=True)
    pdf.cell(95, 7, "Total Combustible Consumido", border=1)
    pdf.cell(95, 7, f"{litros_consumidos} Litros", border=1, ln=True)
    pdf.cell(95, 7, "Kilometros Recorridos", border=1)
    pdf.cell(95, 7, f"{km_recorridos} Km", border=1, ln=True)
    pdf.cell(95, 7, "Rendimiento Obtenido", border=1)
    pdf.cell(95, 7, f"{rendimiento} Km/L", border=1, ln=True)
    pdf.cell(95, 7, "Numero de Casetas Pasadas", border=1)
    pdf.cell(95, 7, f"{num_casetas} casetas", border=1, ln=True)
    pdf.cell(95, 7, "Monto Total en Casetas (IAVE)", border=1)
    pdf.cell(95, 7, f"${gasto_iave} MXN", border=1, ln=True)
    pdf.cell(95, 7, "Costo Promedio Caseta por Km", border=1)
    pdf.cell(95, 7, f"${costo_caseta_km} MXN/Km", border=1, ln=True)
    
    pdf.ln(10)

    # Generar Gráfica Temporal para incluir en el PDF
    fig, ax = plt.subplots(figsize=(6, 3))
    categorias = ['Combustible (L)', 'Casetas ($)', 'Rendimiento (x10)']
    valores = [litros_consumidos, gasto_iave, rendimiento * 10]
    ax.bar(categorias, valores, color=['#3498db', '#e74c3c', '#2ecc71'])
    ax.set_title("Resumen Visual del Viaje")
    
    # Guardar gráfica temporal
    temp_dir = tempfile.gettempdir()
    chart_path = os.path.join(temp_dir, "chart.png")
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()

    # Agregar gráfica al PDF
    pdf.image(chart_path, x=40, w=130)

    # Guardar PDF temporal
    pdf_path = os.path.join(temp_dir, "Reporte_Operador.pdf")
    pdf.output(pdf_path)
    return pdf_path

# --- BOTÓN PARA GENERAR Y DESCARGAR PDF ---
st.header("2. Descargar Reporte PDF para Dirección")
if st.button("📄 Generar Dashboard en PDF"):
    ruta_pdf = generar_pdf()
    with open(ruta_pdf, "rb") as file:
        st.download_button(
            label="⬇️ Descargar PDF Completo",
            data=file,
            file_name=f"Reporte_{operador.replace(' ', '_')}_{fecha}.pdf",
            mime="application/pdf"
        )
    st.success("¡Reporte PDF generado exitosamente!")
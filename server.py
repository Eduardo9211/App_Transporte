import json
import os
import tempfile
import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt

class PDFReporteReal(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.set_fill_color(30, 60, 90)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "  REPORTE EJECUTIVO DE DATOS REALES DE OPERACION", ln=True, fill=True)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

def procesar_datos_reales():
    archivo_json = "datos_transporte.json"
    
    if not os.path.exists(archivo_json):
        print("⚠️ No se encontro 'datos_transporte.json'. Exportalo desde la app para generar el PDF real.")
        return

    with open(archivo_json, "r", encoding="utf-8") as f:
        datos = json.load(f)

    df = pd.DataFrame(datos)
    
    pdf = PDFReporteReal()
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Resumen Consolidado de Registros Capturados", ln=True)
    pdf.ln(3)

    # Filtrar Casetas IAVE
    df_iave = df[df['tipo'] == 'iave'] if 'tipo' in df.columns else pd.DataFrame()
    
    if not df_iave.empty:
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(40, 7, "Operador", border=1, fill=True)
        pdf.cell(50, 7, "Caseta / Ruta", border=1, fill=True)
        pdf.cell(45, 7, "Monto Peaje ($)", border=1, fill=True)
        pdf.cell(55, 7, "Fecha/Hora", border=1, fill=True, ln=True)

        pdf.set_font("Arial", "", 9)
        for _, row in df_iave.iterrows():
            pdf.cell(40, 6, str(row.get('operador', '-')), border=1)
            pdf.cell(50, 6, str(row.get('detalles', '-'))[:25], border=1)
            pdf.cell(45, 6, f"${row.get('monto', 0):.2f} MXN", border=1)
            pdf.cell(55, 6, str(row.get('fecha', '-'))[:16], border=1, ln=True)
        pdf.ln(6)

        # Gráfica Real por Operador
        resumen_gastos = df_iave.groupby('operador')['monto'].sum()
        
        fig, ax = plt.subplots(figsize=(6, 2.8))
        resumen_gastos.plot(kind='bar', color='#1e3c72', ax=ax)
        ax.set_title("Gasto Acumulado Real en Peajes por Operador ($ MXN)")
        ax.set_ylabel("Monto Total ($)")
        plt.xticks(rotation=0)

        temp_dir = tempfile.gettempdir()
        chart_path = os.path.join(temp_dir, "grafica_real.png")
        plt.savefig(chart_path, bbox_inches='tight')
        plt.close()

        pdf.image(chart_path, x=35, w=135)

    pdf_output = os.path.join(temp_dir, "Reporte_Ejecutivo_Real.pdf")
    pdf.output(pdf_output)
    print(f"✅ ¡PDF Ejecutivo Generado con exito usando tus DATOS REALES! Ubicacion: {pdf_output}")

if __name__ == "__main__":
    procesar_datos_reales()
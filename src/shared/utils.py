import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os
from PIL import Image, ImageDraw, ImageFont

class PDFReport(FPDF):
    def header(self):
        if os.path.exists(st.session_state.LOGO_PATH):
            self.image(st.session_state.LOGO_PATH, 10, 8, 33)

        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, st.session_state.nome_hospital, ln=True, align="R")
        self.ln(5)

    def footer(self):
        self.set_y(-35)
        self.set_font("DejaVu", size=9)
        self.multi_cell(0, 6, "Profissional responsável: __________________________")
        self.ln(2)
        self.multi_cell(0, 6, "Assinatura: ________________________________________")
        self.ln(5)
        self.cell(0, 10, "Documento gerado automaticamente pelo sistema clínico", align="C")

def generate_pdf(patient_name, inputs, mensagem, probabilidade):
    pdf = PDFReport()

    # Fonte Unicode
    pdf.add_font("DejaVu", "", st.session_state.FONT_PATH, uni=True)
    pdf.add_font("DejaVu", "B", st.session_state.FONT_PATH, uni=True)
    pdf.set_font("DejaVu", size=12)

    pdf.add_page()

    # Título
    pdf.cell(0, 10, f"Relatório de Avaliação — {patient_name}", ln=True)

    # Data BR
    dt = datetime.now()
    formatted_date = dt.strftime("%d/%m/%Y - %H:%M")

    pdf.ln(4)
    pdf.set_font("DejaVu", size=10)
    pdf.cell(0, 8, f"Data: {formatted_date}", ln=True)

    # BLOCO — DADOS DO PACIENTE
    pdf.ln(6)
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 8, "Dados do paciente:", ln=True)

    pdf.set_font("DejaVu", size=10)
    for k, v in inputs.items():

        field_name = st.session_state.FIELD_MAPPING.get(k, k)

        # Traduz valores categóricos
        if isinstance(v, str) and v in st.session_state.CATEGORY_TRANSLATION:
            display_value = st.session_state.CATEGORY_TRANSLATION[v]
        else:
            display_value = v

        # Se tiver explicação numérica
        if k in st.session_state.EXPLAIN_NUMERIC:
            meaning = st.session_state.EXPLAIN_NUMERIC[k].get(v)
            if meaning:
                display_value = f"{v} — {meaning}"

        pdf.multi_cell(0, 6, f" • {field_name}: {display_value}")

    # BLOCO — RESULTADO
    pdf.ln(4)
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 8, "Resultado da predição:", ln=True)

    pdf.set_font("DejaVu", size=11)
    pdf.multi_cell(0, 6, f"Mensagem: {mensagem}")
    pdf.ln(2)
    pdf.multi_cell(0, 6, f"Probabilidade estimada: {probabilidade:.2f}%")

    return pdf.output(dest="S").encode("latin1", "replace")

def recommend_nutrition_profile(inputs):
    # heurísticas simples para sugestão
    recs = []
    if inputs.get('FAVC') == 'yes':
        recs.append('Reduzir alimentos de alta caloria; priorizar fontes proteicas magras e fibras.')
    if inputs.get('FCVC', 3) <= 2:
        recs.append('Aumentar consumo de vegetais (>=3 porções/dia).')
    if inputs.get('CH2O', 2) <= 1:
        recs.append('Aumentar ingestão de água para 1-2 L/dia ou mais.')
    if inputs.get('FAF', 0) == 0:
        recs.append('Iniciar programa de atividade física gradual (ex.: 3x/sem 30 min).')
    if inputs.get('SMOKE') == 'yes':
        recs.append('Considerar cessação do tabaco; avaliar suporte médico.')
    if not recs:
        recs.append('Manter hábitos saudáveis; alimentação balanceada e atividade física regular.')
    return recs

def create_logo(path=st.session_state.LOGO_PATH, hospital=st.session_state.HOSPITAL_NAME):
    if os.path.exists(path):
        return path
    img = Image.new("RGBA", (400, 100), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    # Desenho simples: cruz + texto
    # cross
    draw.rectangle((20, 20, 70, 80), fill=st.session_state.PRIMARY_COLOR)
    draw.rectangle((40, 0, 50, 100), fill=st.session_state.ACCENT_COLOR)
    # texto
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    draw.text((90, 30), hospital, fill=st.session_state.PRIMARY_COLOR, font=font)
    img.save(path)
    return path
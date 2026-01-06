import re
from typing import Any, Dict
import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os
from PIL import Image, ImageDraw, ImageFont

class PDFReport(FPDF):
    """Classe de relatório PDF customizada com cabeçalho/rodapé e tratamento de fontes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font_registered = False
        # Try explicit config then fallback to system fonts
        font_path = _find_system_font(st.session_state.get("FONT_PATH", "DejaVuSans.ttf"))
        if font_path and os.path.exists(font_path):
            try:
                self.add_font("DejaVu", "", font_path, uni=True)
                self.add_font("DejaVu", "B", font_path, uni=True)
                self.font_registered = True
            except Exception:
                self.font_registered = False

    def header(self):
        """Adiciona cabeçalho com logo e nome do hospital."""
        logo_path = st.session_state.get("LOGO_PATH", "logo.png")
        hospital_name = st.session_state.get("HOSPITAL_NAME", "Hospital Padrão")
        # Header background rectangle: use a light background to keep logo visible
        # Default: white; use a slightly off-white to keep contrast with content.
        bg = st.session_state.get("HEADER_BG", (255, 255, 255))
        try:
            r, g, b = bg
        except Exception:
            r, g, b = (255, 255, 255)
        try:
            self.set_fill_color(r, g, b)
            self.rect(0, 0, self.w, 28, style='F')
        except Exception:
            pass
        # Logo on the left: larger to improve visibility
        if os.path.exists(logo_path):
            try:
                # Increase width to 36 to make the logo more visible
                self.image(logo_path, 12, 4, 36)
            except Exception:
                pass
        # Hospital name on header (white text)
        try:
            self.set_text_color(255, 255, 255)
            if self.font_registered:
                # Increase title size for prominence
                self.set_font("DejaVu", "B", 20)
                self.set_text_color(25, 25, 25)
                self.set_xy(54, 8)
                self.cell(0, 10, hospital_name)
            else:
                self.set_font("Arial", "B", 20)
                self.set_text_color(25, 25, 25)
                self.set_xy(54, 8)
                self.cell(0, 10, clean_ascii(hospital_name))
        except Exception:
            pass
        # Reset colors and spacing
        try:
            self.set_text_color(0, 0, 0)
        except Exception:
            pass
        self.ln(18)

    def footer(self) -> None:
        """Adiciona rodapé com linhas para assinatura."""
        try:
            self.set_y(-35)
            if self.font_registered:
                self.set_font("DejaVu", size=9)
                _safe_multi_cell(self, 0, 6, "Profissional responsável: __________________________")
                self.ln(2)
                _safe_multi_cell(self, 0, 6, "Assinatura: ________________________________________")
                self.ln(5)
                _safe_multi_cell(self, 0, 6, "Documento gerado automaticamente pelo sistema clínico")
            else:
                self.set_font("Arial", size=9)
                _safe_multi_cell(self, 0, 6, clean_ascii("Profissional responsável: __________________________"))
                self.ln(2)
                _safe_multi_cell(self, 0, 6, clean_ascii("Assinatura: ________________________________________"))
                self.ln(5)
                _safe_multi_cell(self, 0, 6, clean_ascii("Documento gerado automaticamente pelo sistema clínico"))
            # Page number on the right
            try:
                self.set_font("Arial", size=8)
                self.set_y(-15)
                page_text = f"Página {self.page_no()}"
                self.cell(0, 10, page_text, align='R')
            except Exception:
                pass
        except Exception:
            # Footer must not break PDF generation
            return

def _find_system_font(preferred: str | None = None) -> str | None:
    """Tenta localizar uma fonte TrueType do sistema que suporte Unicode (ex.: DejaVu/Arial).

    Pesquisa em caminhos comuns de fontes e retorna o primeiro caminho TTF encontrado ou `None`.
    """
    if preferred and os.path.exists(preferred):
        return preferred

    # Common font names to try
    candidates = [
        "DejaVuSans.ttf",
        "DejaVuSans-Bold.ttf",
        "Arial.ttf",
        "Arial Unicode.ttf",
        "Arial Unicode MS.ttf",
        "LiberationSans-Regular.ttf",
        "NotoSans-Regular.ttf",
    ]

    # Try session config path first
    font_path = st.session_state.get("FONT_PATH")
    if font_path and os.path.exists(font_path):
        return font_path

    # Check typical system font directories
    font_dirs = [
        os.path.join(os.getenv("WINDIR", "C:\\Windows"), "Fonts"),
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/truetype/liberation",
        "/usr/share/fonts/truetype/noto",
        "/usr/share/fonts/truetype/freefont",
        "/usr/local/share/fonts",
        os.path.expanduser("~/.local/share/fonts"),
    ]

    for d in font_dirs:
        try:
            if not d or not os.path.isdir(d):
                continue
            for cand in candidates:
                path = os.path.join(d, cand)
                if os.path.exists(path):
                    return path
        except Exception:
            continue

    # As last attempt, search recursively under /usr/share/fonts (may be slow)
    try:
        for root, dirs, files in os.walk("/usr/share/fonts"):
            for f in files:
                if f.lower().endswith('.ttf'):
                    for cand in candidates:
                        if cand.lower().startswith(f.lower().split('.')[0]):
                            return os.path.join(root, f)
    except Exception:
        pass

    return None

def _safe_multi_cell(pdf: FPDF, w: float, h: float, txt: str, min_font_size: int = 6) -> None:
    """Escreve `txt` com segurança usando `multi_cell`, tratando problemas de largura/fonte do FPDF.

    Estratégia:
    - Tenta escrever normalmente.
    - Se o FPDF levantar exceção por largura, reduz o tamanho da fonte gradualmente e tenta novamente.
    - Se ainda falhar, reduz as margens esquerda/direita e tenta mais uma vez.
    - Como último recurso, escreve um traço '-' para evitar falha na geração do PDF.
    """
    if not isinstance(txt, str):
        txt = str(txt)
    txt = txt or "-"
    try:
        pdf.multi_cell(w, h, txt)
        return
    except Exception:
        # Try reducing font size progressively
        current_size = pdf.font_size_pt
        for reduced_size in range(int(current_size) - 1, min_font_size - 1, -1):
            try:
                pdf.set_font_size(reduced_size)
                pdf.multi_cell(w, h, txt)
                return
            except Exception:
                continue
        # If still failing, reduce margins and retry once
        try:
            l_margin, r_margin = pdf.l_margin, pdf.r_margin
            pdf.set_left_margin(2)
            pdf.set_right_margin(2)
            pdf.multi_cell(w, h, txt)
            pdf.set_left_margin(l_margin)
            pdf.set_right_margin(r_margin)
            return
        except Exception:
            # As a final fallback, just write a dash
            try:
                pdf.set_font_size(min_font_size)
                pdf.multi_cell(w, h, "-")
            except Exception:
                pass

def clean_ascii(text: Any) -> str:
    """Retorna uma string compatível com Latin-1 adequada para fontes FPDF sem suporte a Unicode.

    - Substitui pontuação Unicode comum por equivalentes ASCII.
    - Remove caracteres não imprimíveis, preservando caracteres acentuados em Latin-1.
    - Garante que o resultado não fique vazio.
    """
    if text is None:
        return "-"
    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception:
            return "-"
    # Replace some unicode punctuation and smart quotes
    text = text.replace("—", "-").replace("–", "-")
    # replace smart/open/close quotes with plain ASCII equivalents
    text = (text.replace("“", '"')
                .replace("”", '"')
                .replace("‘", "'")
                .replace("’", "'"))
    # Remove non-printable characters but preserve Latin-1 characters (accented letters)
    text = re.sub(r"[^\x20-\xFF]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if text else "-"

def generate_pdf(patient_name: str, inputs: Dict[str, Any], mensagem: str, probabilidade: float) -> bytes:
    """Gera um relatório em PDF e retorna os bytes.

    - Usa a fonte Unicode `DejaVu` se disponível (registre via `st.session_state['FONT_PATH']`).
    - Caso contrário, utiliza texto compatível com ASCII/Latin-1.
    """
    pdf = PDFReport()
    # Choose base font
    if pdf.font_registered:
        pdf.set_font("DejaVu", size=12)
    else:
        pdf.set_font("Arial", size=12)

    pdf.add_page()

    # Title area
    titulo = f"Relatório de Avaliação — {patient_name}"
    pdf.ln(2)
    if pdf.font_registered:
        pdf.set_font("DejaVu", "B", 18)
        pdf.set_text_color(25, 25, 25)
        pdf.cell(0, 10, titulo, ln=1, align='C')
    else:
        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(25, 25, 25)
        pdf.cell(0, 10, clean_ascii(titulo), ln=1, align='C')

    # Date (right aligned)
    dt = datetime.now().strftime("%d/%m/%Y - %H:%M")
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Data: {dt}", ln=1, align='R')

    pdf.ln(4)
    # Message and probability summary with visual badge
    # Risk color
    try:
        if probabilidade >= 60:
            rfill = (220, 53, 69)
        elif probabilidade >= 30:
            rfill = (255, 159, 67)
        else:
            rfill = (76, 175, 80)
    except Exception:
        rfill = (76, 175, 80)

    # Draw a colored badge with probability
    try:
        pdf.set_fill_color(*rfill)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 11)
        badge_text = f"Probabilidade: {probabilidade:.2f}%"
        bw = pdf.get_string_width(badge_text) + 10
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.rect(x, y, bw, 8, style='F')
        pdf.set_xy(x + 2, y + 1)
        pdf.cell(bw, 8, badge_text, border=0, align='C')
        pdf.ln(10)
    except Exception:
        # Fallback textual display
        pdf.set_text_color(25, 25, 25)
        pdf.set_font("Arial", size=10)
        _safe_multi_cell(pdf, 0, 6, clean_ascii(mensagem) if not pdf.font_registered else mensagem)

    pdf.ln(2)

    # Patient block (two-column key/value table)
    pdf.set_text_color(25, 25, 25)
    if pdf.font_registered:
        pdf.set_font("DejaVu", "B", 12)
        _safe_multi_cell(pdf, 0, 8, "Dados do paciente:")
        pdf.set_font("DejaVu", size=10)
    else:
        pdf.set_font("Arial", "B", 12)
        _safe_multi_cell(pdf, 0, 8, clean_ascii("Dados do paciente:"))
        pdf.set_font("Arial", size=10)

    # top-level patient info: prefer 'Nome' from inputs
    name_display = inputs.get('Nome', patient_name)
    try:
        pdf.cell(95, 6, ("Nome:" if pdf.font_registered else clean_ascii("Nome:")), border=0)
        pdf.cell(0, 6, (str(name_display) if pdf.font_registered else clean_ascii(str(name_display))), ln=1)
    except Exception:
        _safe_multi_cell(pdf, 0, 6, clean_ascii(f"Nome: {name_display}"))

    pdf.ln(2)

    # Inputs / features as alternating rows
    pdf.set_font("Arial", size=10)
    # Start with session translations but ensure common Portuguese mappings exist
    category_translation = dict(st.session_state.get("CATEGORY_TRANSLATION", {}))
    _fallback = {
        'yes': 'Sim',
        'no': 'Não',
        'automobile': 'Automóvel',
        'Automobile': 'Automóvel',
        'motorbike': 'Moto',
        'Motorbike': 'Moto',
        'public_transportation': 'Transporte Público',
        'Public_Transportation': 'Transporte Público',
        'bike': 'Bicicleta',
        'Bike': 'Bicicleta',
        'walking': 'A pé',
        'Walking': 'A pé'
    }
    for kk, vv in _fallback.items():
        category_translation.setdefault(kk, vv)
    explain_numeric = st.session_state.get("EXPLAIN_NUMERIC", {})
    field_map = dict(st.session_state.get("FIELD_NAME_MAP", {}))
    # Fallback Portuguese labels if session map not provided
    _field_fallback = {
        'family_history': 'Histórico familiar de obesidade',
        'FAVC': 'Consome alimentos de alta caloria',
        'FCVC': 'Consumo de verduras',
        'NCP': 'Refeições por dia',
        'CAEC': 'Lanches entre refeições',
        'SMOKE': 'Fuma',
        'CH2O': 'Ingestão de água',
        'SCC': 'Controla calorias',
        'FAF': 'Atividade física',
        'TUE': 'Uso de tecnologia',
        'CALC': 'Consumo de álcool',
        'MTRANS': 'Meio de transporte'
    }
    for kk, vv in _field_fallback.items():
        field_map.setdefault(kk, vv)

    if isinstance(inputs, dict):
        fill = False
        for k, v in inputs.items():
            if k == 'Nome':
                continue
            try:
                field_name = field_map.get(k, k)
                display_value = v
                # Map categorical translations (handle common case-insensitive keys like 'yes'/'no')
                if isinstance(v, str):
                    if v in category_translation:
                        display_value = category_translation[v]
                    elif v.lower() in category_translation:
                        display_value = category_translation[v.lower()]
                # Numeric explanation: prefer the human-friendly meaning alone (no leading number)
                if k in explain_numeric:
                    meaning = explain_numeric[k].get(v)
                    if meaning:
                        display_value = meaning

                safe_field = clean_ascii(str(field_name))[:60]
                safe_value = clean_ascii(str(display_value))[:140]

                # alternating light fill for rows
                if fill:
                    pdf.set_fill_color(245, 245, 245)
                    pdf.cell(95, 6, safe_field, border=0, fill=True)
                    pdf.cell(0, 6, safe_value, border=0, ln=1, fill=True)
                else:
                    pdf.cell(95, 6, safe_field, border=0)
                    pdf.cell(0, 6, safe_value, border=0, ln=1)
                fill = not fill
            except Exception:
                try:
                    _safe_multi_cell(pdf, 0, 6, clean_ascii(f"{k}: {v}"))
                except Exception:
                    _safe_multi_cell(pdf, 0, 6, "-")

    pdf.ln(4)

    # Result block with progress bar
    if pdf.font_registered:
        pdf.set_font("DejaVu", "B", 12)
        _safe_multi_cell(pdf, 0, 8, "Resultado da predição:")
        pdf.set_font("DejaVu", size=11)
        _safe_multi_cell(pdf, 0, 6, mensagem)
    else:
        pdf.set_font("Arial", "B", 12)
        _safe_multi_cell(pdf, 0, 8, clean_ascii("Resultado da predição:"))
        pdf.set_font("Arial", size=11)
        _safe_multi_cell(pdf, 0, 6, clean_ascii(mensagem))

    # Visual probability bar
    try:
        bar_width = 140
        x = pdf.get_x()
        y = pdf.get_y()
        # Outline
        pdf.set_draw_color(180, 180, 180)
        pdf.rect(x, y, bar_width, 6)
        # Filled part
        fill_w = max(2, min(bar_width, int(bar_width * (probabilidade / 100.0))))
        pdf.set_fill_color(*rfill)
        pdf.rect(x + 1, y + 1, fill_w - 2, 4, style='F')
        # Percentage label
        pdf.set_xy(x + bar_width + 4, y)
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(25, 25, 25)
        pdf.cell(0, 6, f"{probabilidade:.2f}%", ln=1)
    except Exception:
        pdf.ln(6)

    pdf.ln(6)
    # Recommendations (short list)
    try:
        recs = recommend_nutrition_profile(inputs)
        pdf.set_font("Arial", "B", 11)
        _safe_multi_cell(pdf, 0, 8, "Recomendações nutricionais:")
        pdf.set_font("Arial", size=10)
        for r in recs:
            _safe_multi_cell(pdf, 0, 6, "- " + r)
    except Exception:
        pass

    # Return bytes (pdf.output(dest="S") already returns bytes)
    try:
        output = pdf.output(dest="S")
        # Ensure we always return raw bytes without corrupting binary PDF data.
        # FPDF may return `bytes` or a `str` containing byte values (0-255).
        # Use Latin-1 encoding when converting `str` to `bytes` to preserve
        # the original byte values exactly.
        if isinstance(output, bytes):
            return output
        return output.encode("latin1", "replace")
    except Exception:
        return b""
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
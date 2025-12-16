import os
import re
from datetime import datetime
from typing import Any, Dict

import streamlit as st
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont


@st.cache_resource
def load_ml_model(model_path: str):
    """Load an ML model from disk with caching and safe fallbacks.

    Supports `.joblib` and `.pkl`. Returns None on failure and logs a Streamlit warning.
    """
    try:
        if model_path.endswith(".joblib"):
            import joblib

            return joblib.load(model_path)
        elif model_path.endswith(".pkl"):
            import pickle

            with open(model_path, "rb") as f:
                return pickle.load(f)
        else:
            st.warning("Formato de modelo não suportado. Use .joblib ou .pkl")
            return None
    except Exception as e:
        st.warning(f"Não foi possível carregar o modelo: {e}")
        return None


def clean_ascii(text: Any) -> str:
    """Return a Latin-1-safe string suitable for non-Unicode FPDF fonts.

    - Replaces common Unicode punctuation with ASCII equivalents.
    - Removes any remaining non-printable characters but keeps Latin-1 accented characters.
    - Ensures non-empty result.
    """
    if text is None:
        return "-"
    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception:
            return "-"
    # Replace some unicode punctuation
    text = text.replace("—", "-").replace("–", "-")
    text = text.replace(""", '"').replace(""", '"').replace("'", "'")
    # Remove non-printable characters but preserve Latin-1 characters (accented letters)
    text = re.sub(r"[^\x20-\xFF]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if text else "-"


def _find_system_font(preferred: str | None = None) -> str | None:
    """Try to locate a system TrueType font that supports Unicode (e.g. DejaVu/Arial).

    Searches common system font paths and returns the first found TTF path or None.
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
    """Safely write `txt` using `multi_cell`, handling FPDF width/font issues.

    Strategy:
    - Try to write normally.
    - If FPDF raises an exception about width, reduce font size stepwise and retry.
    - If it still fails, set small left/right margins and retry once.
    - As a last resort, write a single dash '-' so PDF generation doesn't fail.
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


class PDFReport(FPDF):
    """Custom PDF report class with header/footer and font handling."""

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
        """Add header with logo and hospital name."""
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
        """Add footer with signature lines."""
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


def generate_pdf(patient_name: str, inputs: Dict[str, Any], mensagem: str, probabilidade: float) -> bytes:
    """Generate a PDF report and return bytes.

    - Uses `DejaVu` Unicode font if available (register via `st.session_state['FONT_PATH']`).
    - Falls back to ASCII-safe text when necessary.
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


def recommend_nutrition_profile(inputs: Dict[str, Any]) -> list:
    """Provide simple nutrition recommendations based on input values."""
    recs = []
    if inputs.get("FAVC") == "yes":
        recs.append("Reduzir alimentos de alta caloria; priorizar fontes proteicas magras e fibras.")
    if inputs.get("FCVC", 3) <= 2:
        recs.append("Aumentar consumo de vegetais (>=3 porções/dia).")
    if inputs.get("CH2O", 2) <= 1:
        recs.append("Aumentar ingestão de água para 1-2 L/dia ou mais.")
    if inputs.get("FAF", 0) == 0:
        recs.append("Iniciar programa de atividade física gradual (ex.: 3x/sem 30 min).")
    if inputs.get("SMOKE") == "yes":
        recs.append("Considerar cessação do tabaco; avaliar suporte médico.")
    if not recs:
        recs.append("Manter hábitos saudáveis; alimentação balanceada e atividade física regular.")
    return recs


def create_logo(path: str | None = None, hospital: str | None = None) -> str:
    """Create a simple logo image if `path` doesn't exist and return the path.

    Uses session_state defaults when arguments are not provided.
    """
    if path is None:
        path = st.session_state.get("LOGO_PATH", "logo.png")
    if hospital is None:
        hospital = st.session_state.get("HOSPITAL_NAME", "Hospital Padrão")
    if os.path.exists(path):
        return path

    try:
        img = Image.new("RGBA", (400, 100), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        primary_color = st.session_state.get("PRIMARY_COLOR", (25, 118, 210))
        accent_color = st.session_state.get("ACCENT_COLOR", (255, 152, 0))
        draw.rectangle((20, 20, 70, 80), fill=primary_color)
        draw.rectangle((40, 0, 50, 100), fill=accent_color)
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except Exception:
            font = ImageFont.load_default()
        draw.text((90, 30), hospital, fill=primary_color, font=font)
        img.save(path)
        return path
    except Exception:
        return path

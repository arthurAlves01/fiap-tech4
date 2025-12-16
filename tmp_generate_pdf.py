from pathlib import Path
import sys
root = Path('.').resolve()
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
try:
    import src.utils.utils as u
    import streamlit as st
except Exception as e:
    print('IMPORT_ERROR', e)
    raise SystemExit(1)
# Prepara sessão para evitar erros
st.session_state['HOSPITAL_NAME'] = 'Hospital Teste'
st.session_state['LOGO_PATH'] = 'logo.png'  # coloque um logo se desejar
st.session_state['FONT_PATH'] = ''
st.session_state['PRIMARY_COLOR'] = (25, 118, 210)
st.session_state['ACCENT_COLOR'] = (255, 152, 0)
# translation and explanation mapping (as in Prever.py) to simulate environment
st.session_state['CATEGORY_TRANSLATION'] = {'yes':'Sim', 'no':'Não', 'Sometimes':'Às vezes', 'Frequently':'Frequentemente', 'Always':'Sempre'}
st.session_state['FIELD_NAME_MAP'] = {'FCVC': 'Consumo de verduras', 'NCP':'Refeições por dia'}
st.session_state['EXPLAIN_NUMERIC'] = {'FCVC': {1:'Raramente',2:'Ocasionalmente',3:'Frequentemente'},'NCP': {1:'1 refeição',2:'2 refeições',3:'3 refeições',4:'4 refeições'}}

inputs = {'Nome': 'João Silva', 'family_history': 'yes', 'FAVC': 'no', 'FCVC': 3, 'NCP': 3}
pdf_bytes = u.generate_pdf('João Silva', inputs, 'Paciente com risco moderado de obesidade', 45.67)
print('PDF_BYTES_LEN', len(pdf_bytes))
open('tmp_test_relatorio.pdf','wb').write(pdf_bytes)
print('WROTE tmp_test_relatorio.pdf')

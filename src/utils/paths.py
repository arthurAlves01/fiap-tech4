from pathlib import Path

# Caminho absoluto para a raiz do projeto
ROOT = Path(__file__).resolve().parents[2]

# Caminho para a pasta data
DATA_DIR = ROOT / "data"
 
# Caminho padrão para o banco de dados de histórico
DB_PATH = ROOT / "records.db"

# Caminhos padrão para ativos (logo / fontes)
LOGO_PATH = ROOT / "logo.png"
FONT_PATH = ROOT / "assets" / "DejaVuSans.ttf"
"""Paths used throughout the project (project root, data folder, assets)."""
from pathlib import Path

# Caminho absoluto para a raiz do projeto
ROOT: Path = Path(__file__).resolve().parents[2]

# Caminho para a pasta data
DATA_DIR: Path = ROOT / "data"
 
# Caminho padrão para o banco de dados de histórico
DB_PATH: Path = ROOT / "records.db"

# Caminhos padrão para ativos (logo / fontes)
LOGO_PATH: Path = ROOT / "logo.png"
FONT_PATH: Path = ROOT / "assets" / "DejaVuSans.ttf"
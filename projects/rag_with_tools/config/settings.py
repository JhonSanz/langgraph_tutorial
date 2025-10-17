import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = Path(__file__).parent.parent / "datasources.yaml"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    DATA_SOURCES = yaml.safe_load(f)

MAX_RETRIES = 2

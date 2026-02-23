# AI Restaurant Recommendation Service

Phase 1: Data Acquisition | Phase 2: Data Processing | Phase 3: API & Backend Service

## Setup

```bash
cd ai-restaurant-recommender
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` with `GROQ_API_KEY` before running the API.

## Run API Server (Phase 3)

```bash
cd ai-restaurant-recommender
source .venv/bin/activate
PYTHONPATH=. uvicorn src.phase3_api_service.app:app --reload
```

API available at `http://127.0.0.1:8000`. Docs at `http://127.0.0.1:8000/docs`.

## Usage

**Phase 1 - Load and validate:**
```python
from src.phase1_data_acquisition import load_dataset_from_hf, validate_dataset_schema

df = load_dataset_from_hf()
validate_dataset_schema(df)
```

**Phase 2 - Process and engineer features:**
```python
from src.phase1_data_acquisition import load_dataset_from_hf
from src.phase2_data_processing import process_data

df = load_dataset_from_hf()
processed = process_data(df)
```

Dataset is downloaded from Hugging Face and cached in `.cache/huggingface/datasets`. Raw data is saved to `data/raw/zomato_restaurants_raw.parquet`.

## Tests

```bash
cd ai-restaurant-recommender
source .venv/bin/activate
PYTHONPATH=. pytest tests/ -v
```

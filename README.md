# fb-analysis
Dashboard to explore your personal Facebook data dump.

## Setup

1. Download your facebook messages in `.json` format, and unzip.
2. Edit `DATA_DIR` and `MY_NAME` in `config.py`. `DATA_DIR` should be the full path to the `"data"` directory.
3. Install the required packages in a clean virtual environment:

```bash
pip install -r requirements.txt
```

## Run the app

```bash
python app.py
```

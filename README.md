# fb-analysis
Interactive dashboard to explore your personal Facebook Messenger data dump.

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

The Plotly Dash webserver will load at [http://127.0.0.1:8050](http://127.0.0.1:8050).

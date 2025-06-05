from dashboard import app  # assumes dashboard.py has app = Dash(__name__)

server = app.server  # required for gunicorn and AWS App Runner

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=False)

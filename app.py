from dashboard import app  # assumes dashboard.py has app = Dash(__name__)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)


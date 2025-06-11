import sys
import traceback

try:
    from dashboard import app
except Exception:
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8080)
    except Exception:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

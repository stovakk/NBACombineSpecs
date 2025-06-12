import os
from dashboard import app

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)

from flask_cors import CORS

from app import app as application
app = application

if __name__ == '__main__':
    # app.debug = True
    CORS(app)
    app.run(host="0.0.0.0", port=5001, use_reloader=True)

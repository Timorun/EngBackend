from app import app as application
app = application

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, use_reloader=True)
import logging
from flask import Flask, render_template, request
# from flask_cors import CORS


from api import api_blueprint

app = Flask(__name__, static_folder="./root/static", template_folder="./root")
app.register_blueprint(api_blueprint)

# CORS(app, supports_credentials=True)


@app.route('/')
def root():
    return render_template("index.html")


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    FORMAT = "%(message)s"
    app.run(debug=False, host='0.0.0.0', port=23818)

from flask import Flask, jsonify


application= app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello. This is a test of GitHub Actions!'



if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, world! (ver3 생성)"

if __name__ == '__main__':
    app.run(debug=True)
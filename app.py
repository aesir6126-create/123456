from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
  return "Hello, Render! 我的第一個 Python 網頁成功上傳了！"


if __name__ == "__main__":
  app.run(debug=True)
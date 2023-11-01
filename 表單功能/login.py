# login.py
from flask import Flask, request, render_template

app = Flask(__name__)


def authenticate(username, password):
    valid_credentials = {
        '123': '00000',
        '456': '11111'
    }

    if username in valid_credentials and valid_credentials[username] == password:
        return True
    else:
        return False


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if authenticate(username, password):
            return render_template('welcome.html', username=username)
        else:
            return "失败"

    return render_template('login.html')


if __name__ == '__main__':
    app.run(port=8080)

# login.py
from flask import Flask, request, render_template

app = Flask(__name__, static_folder='static')


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
def home():
    return render_template('home.html')


@app.route('/logins', methods=['GET', 'POST'])
def logins():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if authenticate(username, password):
            return render_template('welcomes.html', username=username)
        else:
            return "失败"

    return render_template('login.html')


@app.route('/logint', methods=['GET', 'POST'])
def logint():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if authenticate(username, password):
            return render_template('welcomet.html', username=username)
        else:
            return "失败"

    return render_template('login.html')


@app.route('/other_chose')  # 首頁
def other_chose():
    return render_template('chose.html')


@app.route('/other_logint')  # chose
def other_logint():
    return render_template('logint.html')


@app.route('/other_logins')  # chose
def other_logins():
    return render_template('logins.html')


@app.route('/other_page1')  # welcome
def other_page1():
    return render_template('p1.html')


@app.route('/other_page2')  # p1
def other_page2():
    return render_template('p2.html')


@app.route('/other_page3')  # welcome
def other_page3():
    return render_template('p3.html')


@app.route('/other_page4')  # p1
def other_page4():
    return render_template('p4.html')


@app.route('/other_welcome')  # p4
def other_welcome():
    return render_template('welcome.html')


if __name__ == '__main__':
    app.run(port=8080)

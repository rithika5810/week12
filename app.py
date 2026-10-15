from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('registration.html')


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']

    return render_template('success.html', name=name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
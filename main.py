from website import create_app
from flask import Flask, render_template
from flask_login import login_required, current_user

app = Flask(__name__)

app = create_app()
@app.route('/')
def index():
    return render_template("index.html", user=current_user)

if __name__ == '__main__':
    app.run(debug=True)
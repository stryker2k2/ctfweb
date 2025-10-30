from flask import Flask, render_template, Blueprint
import logging

main = Blueprint("main", __name__)

logger = logging.getLogger(__name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/machines')
def machines():
    return render_template('machines.html')

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
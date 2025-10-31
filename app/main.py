from flask import Flask, render_template, Blueprint, redirect, url_for, request, flash
import logging, json
from pathlib import Path
from .proxmox import getContainers, createTarget

main = Blueprint("main", __name__)
logger = logging.getLogger(__name__)

classes_path = "app/data/classes.json"

@main.route('/')
def index():
    with open(classes_path, 'r') as file:
        data = json.load(file)
    return render_template('index.html', navtab="home", data=data)

@main.route('/machines')
def machines():
    containers = getContainers()
    return render_template('machines.html', navtab="machines", containers=containers)

@main.route('/walkthru')
def walkthru():
    return render_template('walkthru.html', navtab="walkthru")

@main.route("/spinup", methods=["POST", "GET"])
def spinup():
    if request.method == "POST":
        msg = createTarget()
        flash(msg)
        return redirect(url_for('main.machines'))
    return "<h1>ERROR: 404</h1>"

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, render_template, Blueprint, redirect, url_for, request, flash
import logging, json
from pathlib import Path
from .proxmox import getContainers, createTarget
from markdown_it import MarkdownIt

bronze_md = """
```c
#include <stdio.h>
#include <string.h>

void printSecret() {
    int encoded_secret[] = {0x134C, 0x1375, 0x135B, 0x1342, 0x1304, 0x131A, 0x1303, 0x1359, 0x1353, 0x131A, 0x1307, 0x1345, 0x1356, 0x1359, 0x1350, 0x1304, 0x134A, 0x1337};

    int key = 0x1337;
    int i = 0;

    printf("CTF-KEY ");
    while ((encoded_secret[i] ^ key) != 0) {
        printf("%c", (char)(encoded_secret[i] ^ key));
        i++;
    }
    printf("\\n");
}

int logToFile(char *logTxt)
{ 
    char tmpLog[64];
    printf("[+] logging to file\\n");
    sprintf(tmpLog, "[+] %s", logTxt);
    FILE *logFile = fopen("log.txt", "w");
    if (logFile == NULL)
    {
        return 1;
    }

    fprintf(logFile, "%s\\n", tmpLog);
    fclose(logFile);

    return 0;
}

int main(int argc, char *argv[])
{
    logToFile(argv[1]);
}
```
"""

python_md = """
```python
# Bronze CTF

import subprocess
import os

# The name of the executable file in the current directory
EXECUTABLE_NAME = './bronze'

# The specific string parameter: 'A' repeated 16 times
PARAMETER_STRING = 'A' * 16

def run_program_with_parameter():

    command = [EXECUTABLE_NAME, PARAMETER_STRING]
    
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False 
    )

    # Display the results
    if result.stdout:
        print(result.stdout)

    if result.returncode < 0:
        if result.returncode == -11:
            print("SEGMENT FAULT!")
            exit(-11)
        print(f"Error!")

if __name__ == "__main__":
    run_program_with_parameter()
"""

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

@main.route('/challenge/<medal>')
def challenge(medal):
    markdown_content = "None"
    if medal == 'bronze':
        logger.info("[+] Bronze Challenge")

        md = MarkdownIt().enable('table').enable('strikethrough').enable('linkify') # Enable desired extensions
        markdown_content = md.render(bronze_md)
        python_content = md.render(python_md)
    return render_template('challenge.html', medal=medal, navtab="challenges", markdown_content=markdown_content, python_content=python_content)

@main.route('/walkthru')
def walkthru():
    return render_template('walkthru.html', navtab="walkthru")

@main.route("/spinup", methods=["POST"])
def spinup():
    if request.method == "POST":
        msg = createTarget()
        flash(msg)
        return redirect(url_for('main.machines'))

# TODO: @main.route("/powerOn", methods=["POST"])

# TODO: @main.route("/powerOff", methods=["POST"])

# TODO: @main.route("/deleteVM", methods=["POST"])

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
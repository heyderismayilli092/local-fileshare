# Local FileShare -- Server Software

from flask import Flask, request, redirect, render_template, jsonify, send_from_directory, session
from functools import wraps
from datetime import timedelta
import os
import sys
import subprocess
import socket
import locale
import gettext
import bcrypt
from network import get_ip_address, find_active_interface

locale.setlocale(locale.LC_ALL, '')  # category is being set
locale.bindtextdomain('local-fileshare', '/usr/share/locale')
# translation is provide
gettext.bindtextdomain('local-fileshare', '/usr/share/locale')
gettext.textdomain('local-fileshare')
_ = gettext.gettext

# translatable interface texts
main_interface_texts = {
    "label0": _("Local FileShare"),
    "label1": _("Drag the files here"),
    "label2": _("or select from your device"),
    "label3": _("Uploading..."),
    "label4": _("Shared by User:"),
    "label5": _("Shared Files"),
    "label6": _("No files yet")
}

login_interface_texts = {
    "label0": _("Login Window"),
    "label1": _("Enter the password you set:"),
    "label2": _("Login"),
}


app = Flask(__name__)
app.secret_key = "729c3031cc6726a12263e10e1fa442d65966fd52ca7a82c2"  # secret key
app.permanent_session_lifetime = timedelta(minutes=30)  # 30-minute session duration
UPLOAD_FOLDER = os.getenv("MOD")
CHUNK_FOLDER = "/tmp/fileshare-chunks"  # chunk folder

icons = os.path.dirname(os.path.abspath(__file__)) + "/icons"
passhash_file = "/tmp/local-fileshare_passhash"  # hash info file

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect("/")
        return func(*args, **kwargs)
    return wrapper


# login screen
@app.route('/')
def login():
  return render_template('login.html',
      label0=login_interface_texts["label0"],
      label1=login_interface_texts["label1"],
      label2=login_interface_texts["label2"]
  )
@app.route('/login/', methods=["POST"])
def login_check():
    raw_password = request.form.get('password')
    password_bytes = raw_password.encode('utf-8')

    # write password hash file
    tmpfile = open(passhash_file, 'rb')
    stored = tmpfile.read().strip()
    if bcrypt.checkpw(password_bytes, stored):
      session["logged_in"] = True
      return redirect("/fileshare")
    else:
      return redirect("/")


# index screen
@app.route('/fileshare')
@login_required
def index():
    compuser = subprocess.run(['whoami'], capture_output=True, text=True).stdout  # retrieve system user
    return render_template('index.html', compuser=compuser,
        label0=main_interface_texts["label0"],
        label1=main_interface_texts["label1"],
        label2=main_interface_texts["label2"],
        label3=main_interface_texts["label3"],
        label4=main_interface_texts["label4"],
        label5=main_interface_texts["label5"],
        label6=main_interface_texts["label6"]
    )


# Uploads incoming files to the server
@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if not os.path.exists(CHUNK_FOLDER):  # chunk folder check
      os.makedirs(CHUNK_FOLDER)

    file     = request.files['file']
    filename = request.form['filename']
    custom_name = request.form.get('custom_name')
    save_as     = custom_name if custom_name else filename
    total_chunks = int(request.form['total_chunks'])
    chunk_index  = int(request.form['chunk_index'])

    # Save chunk file
    chunk_path = os.path.join(CHUNK_FOLDER, f"{save_as}_part{chunk_index}")
    file.save(chunk_path)
    # All chunks are checked
    uploaded_chunks = [f for f in os.listdir(CHUNK_FOLDER) if f.startswith(save_as)]

    if len(uploaded_chunks) == total_chunks:
        # Merge sequentially
        uploaded_chunks = sorted(uploaded_chunks, key=lambda x: int(x.split("_part")[-1]))
        final_path = os.path.join(UPLOAD_FOLDER, save_as)
        with open(final_path, 'wb') as final_file:
            for part_file_name in uploaded_chunks:
                part_path = os.path.join(CHUNK_FOLDER, part_file_name)
                with open(part_path, 'rb') as part_file:
                    while True:
                        chunk = part_file.read(1024*1024)  # Read in 1 MB blocks
                        if not chunk:
                            break
                        final_file.write(chunk)
                os.remove(part_path)  # remove chunk
    return jsonify({'status': 'ok'})


# Lists files
@app.route('/files')
@login_required
def files():
    files_list = []  # files list
    for dt in os.listdir(UPLOAD_FOLDER):
        directory = os.path.join(UPLOAD_FOLDER, dt)
        if os.path.isfile(directory):
            files_list.append(dt)
    return jsonify(files_list)


# Downloading uploaded files
@app.route('/download/<path:filename>')
@login_required
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


# load requirement icons
@app.route('/icon/<iconname>')
@login_required
def iconload(iconname):
    if not os.path.exists(icons+"/"+iconname):
      return send_from_directory(icons, "unknown.png")
    return send_from_directory(icons, iconname)


if __name__ == '__main__':
    app.run(debug=False, port=9339, host="127.0.0.1")


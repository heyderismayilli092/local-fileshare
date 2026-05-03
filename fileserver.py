# Pardus Fileshare Software

from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import sys
import socket
from network import get_ip_address, find_active_interface


app = Flask(__name__)
UPLOAD_FOLDER = sys.argv[1]
CHUNK_FOLDER = "/tmp/fileshare-chunks"


# index screen
@app.route('/')
def index():
    return render_template('index.html')


# Uploads incoming files to the server
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = request.form['filename']
    custom_name = request.form.get('custom_name')
    save_as = custom_name if custom_name else filename
    total_chunks = int(request.form['total_chunks'])
    chunk_index = int(request.form['chunk_index'])
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
def files():
    fileslist = os.listdir(UPLOAD_FOLDER)
    return jsonify(fayllar_list)


# Downloading uploaded files
@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    iface, host_ip = find_active_interface()
    print(f"Active interface: {iface} ({host_ip})")
    app.run(debug=True, port=9339, host=host_ip)


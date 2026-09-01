import os
import re
import socket
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)
BASE_DIR = os.path.expanduser("~/Hasil_Print")
os.makedirs(BASE_DIR, exist_ok=True)

HTML_PAGE = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kirim Dokumen Cetak</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #0f172a; color: #f8fafc; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 16px; }
        .container { background: #1e293b; width: 100%; max-width: 440px; padding: 26px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #334155; }
        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { font-size: 22px; color: #38bdf8; margin-bottom: 6px; }
        .header p { font-size: 13px; color: #94a3b8; }
        .form-group { margin-bottom: 16px; }
        label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; color: #cbd5e1; }
        input[type="text"] { width: 100%; padding: 12px; border-radius: 8px; border: 1.5px solid #475569; background: #0f172a; color: #fff; font-size: 15px; outline: none; }
        input[type="text"]:focus { border-color: #38bdf8; }
        .file-box { border: 2px dashed #475569; border-radius: 10px; padding: 22px; text-align: center; background: #0f172a; cursor: pointer; }
        .file-box input { display: none; }
        .file-label { color: #38bdf8; font-weight: bold; }
        .file-info { font-size: 13px; color: #94a3b8; margin-top: 6px; }
        button.btn { width: 100%; padding: 14px; background: #0284c7; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; transition: background 0.2s; }
        button.btn:hover { background: #0369a1; }
        button.btn:disabled { background: #475569; cursor: not-allowed; }
        .progress-box { margin-top: 15px; display: none; background: #334155; border-radius: 6px; overflow: hidden; height: 10px; }
        .progress-bar { width: 0%; height: 100%; background: #22c55e; transition: width 0.1s; }
        .alert { margin-top: 15px; padding: 14px; border-radius: 8px; display: none; font-size: 14px; text-align: center; line-height: 1.5; }
        .alert-success { background: rgba(34, 197, 94, 0.2); border: 1px solid #22c55e; color: #4ade80; }
        .alert-error { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #f87171; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🖨️ Kirim File Cetak</h1>
        <p>File langsung terkirim cepat ke komputer kasir</p>
    </div>
    <form id="uploadForm">
        <div class="form-group">
            <label>Nama Anda / No. Antrian:</label>
            <input type="text" id="nama" name="nama" placeholder="Contoh: Pak Budi" required autocomplete="name">
        </div>
        <div class="form-group">
            <label>Pilih File Dokumen / Foto:</label>
            <div class="file-box" onclick="document.getElementById('fileInput').click()">
                <div class="file-label">📁 Ketuk untuk Pilih File</div>
                <input type="file" id="fileInput" name="files" multiple required onchange="onFileSelected()">
                <div class="file-info" id="fileInfo">Bisa pilih banyak file sekaligus (PDF, Word, JPG, dll)</div>
            </div>
        </div>
        <button type="submit" class="btn" id="btnSubmit">🚀 Kirim File ke Kasir</button>
    </form>
    <div class="progress-box" id="pBox"><div class="progress-bar" id="pBar"></div></div>
    <div class="alert" id="alertBox"></div>
</div>
<script>
    function onFileSelected() {
        const input = document.getElementById('fileInput');
        const info = document.getElementById('fileInfo');
        if (input.files.length > 0) info.innerHTML = "<b>" + input.files.length + " file dipilih</b>";
    }
    document.getElementById('uploadForm').onsubmit = function(e) {
        e.preventDefault();
        const nama = document.getElementById('nama').value.trim();
        const files = document.getElementById('fileInput').files;
        if (!nama || files.length === 0) return;

        const formData = new FormData();
        formData.append('nama', nama);
        for(let i=0; i<files.length; i++) formData.append('files', files[i]);

        const btn = document.getElementById('btnSubmit');
        const pBox = document.getElementById('pBox');
        const pBar = document.getElementById('pBar');
        const alertBox = document.getElementById('alertBox');

        btn.disabled = true;
        btn.innerText = 'Mengirim...';
        pBox.style.display = 'block';
        alertBox.style.display = 'none';

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);
        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) pBar.style.width = Math.round((e.loaded / e.total) * 100) + '%';
        };
        xhr.onload = () => {
            btn.disabled = false;
            btn.innerText = '🚀 Kirim File ke Kasir';
            if (xhr.status === 200) {
                const res = JSON.parse(xhr.responseText);
                alertBox.className = 'alert alert-success';
                alertBox.innerHTML = '✅ <b>Berhasil Terkirim!</b><br>' + res.count + ' file masuk ke folder: <b>' + res.folder + '</b>.<br>Silakan infokan ke kasir.';
                alertBox.style.display = 'block';
                document.getElementById('fileInput').value = '';
                document.getElementById('fileInfo').innerText = 'Bisa pilih banyak file sekaligus';
            } else {
                alertBox.className = 'alert alert-error';
                alertBox.innerText = '❌ Terjadi kesalahan saat mengirim file.';
                alertBox.style.display = 'block';
            }
        };
        xhr.onerror = () => {
            btn.disabled = false;
            btn.innerText = '🚀 Kirim File ke Kasir';
            alertBox.className = 'alert alert-error';
            alertBox.innerText = '❌ Gagal terhubung ke komputer kasir.';
            alertBox.style.display = 'block';
        };
        xhr.send(formData);
    };
</script>
</body>
</html>"""

def get_unique_path(folder, filename):
    name, ext = os.path.splitext(filename)
    counter = 1
    target = os.path.join(folder, filename)
    while os.path.exists(target):
        target = os.path.join(folder, f"{name} ({counter}){ext}")
        counter += 1
    return target

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/upload", methods=["POST"])
def upload():
    nama = request.form.get("nama", "").strip()
    clean_nama = re.sub(r'[/\\:*?"<>|]', "", nama).strip() or "Tanpa_Nama"
    folder_tujuan = os.path.join(BASE_DIR, clean_nama)
    os.makedirs(folder_tujuan, exist_ok=True)

    files = request.files.getlist("files")
    saved = 0
    for f in files:
        if f.filename:
            path = get_unique_path(folder_tujuan, os.path.basename(f.filename))
            f.save(path)
            saved += 1

    return jsonify({"status": "ok", "folder": clean_nama, "count": saved})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)

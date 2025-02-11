from flask import Flask, render_template, request, flash, redirect, Response, url_for
from werkzeug.utils import secure_filename
import os
import subprocess
from flask_cors import CORS

upload_folder = r"D:\our_cloud\uploads"
allowed_extensions = ['txt', 'pdf', 'gif', 'jpeg', 'jpg', 'png', 'py', 'pptx', 'docx', 'c']

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
app.config['UPLOAD_FOLDER'] = upload_folder

# Starting the C file as a subprocess through POPEN, since our file is an event and should be running indefinitely.
result = subprocess.Popen(
    ["dirh.exe"],
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE,
    bufsize=1,
    text = True
)

L=[]
def file_valid(filename):
    formed_filename = secure_filename(filename)
    return ('.' in formed_filename) and (formed_filename.split('.')[1].lower() in allowed_extensions)

@app.route('/events')
def get_update():
    def sse():
        global L
        for line in result.stdout:
            L.append(line)
            if L:
                yield f"data: {L[0]}\n\n"
                print(line, " 1st check")
                print(L[0], " push check")
                #works fine, as expected
                L.clear()
    return Response(sse(), mimetype="text/event-stream")

@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        if 'chosenuserfile' not in request.files:
            flash("No filepart received.")
            return redirect(request.url)
        file = request.files['chosenuserfile']
        print(file)
        if file.filename == '':
            flash("Please select a file before uploading.")
            return redirect(request.url)
        filename_list = request.files.getlist('chosenuserfile')
        print(filename_list)
        for fileobj in filename_list:
            filesname = fileobj.filename
            if file_valid(filesname):
                fileobj.save(os.path.join(app.config['UPLOAD_FOLDER'], filesname))
    return render_template('homepage.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001, host = '0.0.0.0')

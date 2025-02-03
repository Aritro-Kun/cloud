from flask import Flask, render_template, request, flash, redirect
from werkzeug.utils import secure_filename
import os

upload_folder = r"D:\our_cloud\uploads"
allowed_extensions = ['txt', 'pdf', 'gif', 'jpeg', 'jpg', 'png', 'py', 'pptx', 'docx', 'c']

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = upload_folder

def file_valid(filename):
    formed_filename = secure_filename(filename)
    return ('.' in formed_filename) and (formed_filename.split('.')[1].lower() in allowed_extensions)

@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        #in case no filepart was sent, file part is beacuse we are using multipart, so it sends a multi-dict, consisting of key value pairs.
        if 'chosenuserfile' not in request.files:
            flash("No filepart, received.")
            return redirect(request.url)
        file = request.files['chosenuserfile']
        print(file)
        #in case, the submit button is clicked, without choosing a file
        if file.filename == '':
            flash("Please select a file, before uploading.")
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
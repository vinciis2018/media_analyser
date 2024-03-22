# GET A MEDIA FILE DETAILS
from flask import Flask, request, render_template_string, redirect, url_for
import subprocess
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit uploads to 16MB

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

HTML_TEMPLATE = '''
<!doctype html>
<title>Upload new Video</title>
<h1>Upload new Video</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
{% if metadata %}
    <h2>Metadata:</h2>
    <pre>{{ metadata }}</pre>
{% endif %}
'''

def get_video_metadata(file_path):
    command = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file_path]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        metadata = json.loads(result.stdout.decode('utf-8'))
        return json.dumps(metadata, indent=4)
    else:
        return "Error extracting metadata"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            metadata = get_video_metadata(file_path)
            return render_template_string(HTML_TEMPLATE, metadata=metadata)
    return render_template_string(HTML_TEMPLATE, metadata=None)

if __name__ == '__main__':
    app.run(debug=True)

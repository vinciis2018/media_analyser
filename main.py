# CONVERT ONE VIDEO AS ANOTHER VIDEO'S FORMAT
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import ffmpeg

app = Flask(__name__, template_folder='templates')

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_video_details(filename):
    try:
        probe = ffmpeg.probe(filename)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
        if video_stream is None:
            raise ffmpeg.Error('No video stream found')
        details = {
            'format': probe['format']['format_name'],
            'codec': video_stream['codec_name'],
            'bitrate': video_stream.get('bit_rate', 'N/A'),
            'fps': eval(video_stream['r_frame_rate']) if 'r_frame_rate' in video_stream else 'N/A',  # simplified calculation of fps
            'audio_codec': audio_stream['codec_name'] if audio_stream else 'N/A'
        }
        return details
    except ffmpeg.Error as e:
        print(e.stderr)
        return None

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file1' not in request.files or 'file2' not in request.files:
        return redirect(url_for('index'))
    file1 = request.files['file1']
    file2 = request.files['file2']
    if file1.filename == '' or file2.filename == '':
        return redirect(url_for('index'))
    if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
        filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
        file1.save(filepath1)
        file2.save(filepath2)

        video1_details = get_video_details(filepath1)
        video2_details = get_video_details(filepath2)

        output_file = os.path.join(app.config['OUTPUT_FOLDER'], 'output_' + file2.filename)
        if video1_details and video2_details:
            # Convert video2 to match video1 details
            stream = ffmpeg.input(filepath2)
            stream = ffmpeg.output(stream, output_file, vcodec=video1_details['codec'], r=video1_details['fps'], acodec=video1_details.get('audio_codec', 'copy'), format=video1_details['format'].split(',')[0])  # Simplified conversion, assumes first format if multiple
            ffmpeg.run(stream)

        return send_from_directory(directory=app.config['OUTPUT_FOLDER'], path='output_' + file2.filename, as_attachment=True)

    return 'File upload failed', 400

if __name__ == '__main__':
    app.run(debug=True, port=8080)

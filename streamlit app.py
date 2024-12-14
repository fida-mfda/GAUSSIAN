from flask import Flask, render_template, request, jsonify, send_file
import os
import cv2
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Folder configurations
UPLOAD_FOLDER = 'static/images/uploaded'
RESULT_FOLDER = 'static/images/results'
VIDEO_FOLDER = 'static/videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Homepage route
@app.route('/')
def home():
    return render_template('index.html')

# Upload and process route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'filename': filename, 'filepath': filepath}), 200
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/process', methods=['POST'])
def process_image():
    data = request.get_json()
    filename = data.get('filename')
    filter_type = data.get('filter_type', 'median_blur')
    level = int(data.get('level', 5))
    rotation = int(data.get('rotation', 0))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    img = cv2.imread(filepath)

    # Apply filter
    if filter_type == 'median_blur':
        level = level if level % 2 == 1 else level + 1
        processed_img = cv2.medianBlur(img, level)
    elif filter_type == 'bilateral_filter':
        processed_img = cv2.bilateralFilter(img, level * 2 + 1, level * 10, level * 10)
    else:
        return jsonify({'error': 'Invalid filter type'}), 400

    # Apply rotation
    if rotation != 0:
        center = (processed_img.shape[1] // 2, processed_img.shape[0] // 2)
        M = cv2.getRotationMatrix2D(center, rotation, 1.0)
        processed_img = cv2.warpAffine(processed_img, M, (processed_img.shape[1], processed_img.shape[0]))

    # Save result
    result_filename = 'result_' + filename
    result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
    cv2.imwrite(result_path, processed_img)

    return jsonify({'result_filename': result_filename, 'result_path': result_path}), 200

@app.route('/download/<filename>')
def download_file(filename):
    result_path = os.path.join(app.config['RESULT_FOLDER'], filename)
    if os.path.exists(result_path):
        return send_file(result_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)

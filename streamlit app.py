from flask import Flask, render_template_string, request, send_file, redirect, url_for
import os
import cv2
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Folder untuk menyimpan file yang diunggah dan hasil
UPLOAD_FOLDER = 'images/uploaded'
RESULT_FOLDER = 'static/results'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Fungsi untuk memeriksa file yang diizinkan
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route untuk homepage
@app.route('/')
def home():
    return render_template_string('''  
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Homepage</title>
        <style>
            body {
                font-family: 'Poppins', sans-serif;
                color: #ffffff;
                margin: 0;
                padding: 0;
                overflow-x: hidden;
            }
            video {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
                z-index: -1;
            }
            h1 {
                font-size: 4em;
                font-weight: bold;
                text-shadow: 3px 3px 10px #ff0000;
                margin: 20px 0;
                text-align: center;
                animation: popOut 1s ease forwards;
                transform: scale(0);
            }
            @keyframes popOut {
                0% {
                    transform: scale(0);
                    opacity: 0;
                }
                100% {
                    transform: scale(1);
                    opacity: 1;
                }
            }
            button {
                background: linear-gradient(90deg, #ff0000, #ffffff);
                color: #000000;
                border: none;
                padding: 15px 30px;
                margin-top: 20px;
                cursor: pointer;
                font-size: 18px;
                font-weight: bold;
                text-transform: uppercase;
                border-radius: 50px;
                box-shadow: 0px 4px 15px rgba(255, 0, 0, 0.5);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            button:hover {
                transform: scale(1.1);
                box-shadow: 0px 6px 20px rgba(255, 0, 0, 0.8);
            }
            a {
                text-decoration: none;
            }
            .section {
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                text-align: center;
                opacity: 0;
                transform: translateY(50px);
                transition: opacity 1s ease, transform 1s ease;
            }
            .section.visible {
                opacity: 1;
                transform: translateY(0);
            }
            .about-us {
                margin-top: 50px;
                padding: 20px;
                background: #000000;
                border-radius: 15px;
                box-shadow: 0px 4px 15px rgba(255, 255, 255, 0.2);
                transform: translateY(100px);
                transition: transform 1s ease, opacity 1s ease;
                opacity: 0;
            }
            .about-us.visible {
                transform: translateY(0);
                opacity: 1;
            }
            p {
                font-size: 1.2em;
                line-height: 1.8;
            }
        </style>
    </head>
    <body>
        <video autoplay loop muted>
            <source src="{{ url_for('static', filename='background.mp4') }}" type="video/mp4">
            Your browser does not support the video tag.
        </video>

        <div class="section">
            <h1>Welcome To Our Website</h1>
            <a href="/gaussian-blur-tool">
                <button>Gaussian Blur Tool</button>
            </a>
        </div>

        <div class="section">
            <div class="about-us">
                <h1>About Us</h1>
                <p>Welcome to our website! Our mission is to provide innovative tools for everyone.</p>
            </div>
        </div>

        <script>
            const sections = document.querySelectorAll('.section, .about-us');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            }, { threshold: 0.5 });

            sections.forEach(section => observer.observe(section));
        </script>
    </body>
    </html>
    ''')

# Route untuk Gaussian Blur Tool
@app.route('/gaussian-blur-tool', methods=['GET', 'POST'])
def gaussian_blur_tool():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            filter_type = request.form.get('filter_type')
            level = int(request.form.get('level', 5))
            if not (1 <= level <= 50):
                level = 5
            return redirect(url_for('process_image', filename=filename, filter_type=filter_type, level=level))

    return render_template_string('''  
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gaussian Blur Tool</title>
        <style>
            body {
                font-family: 'Poppins', sans-serif;
                background-color: #000000;
                background-image: radial-gradient(circle, #800000, #550000);
                color: white;
                text-align: center;
                margin: 0;
                padding: 0;
            }
            h1 {
                font-size: 2.5em;
                margin-top: 50px;
                text-shadow: 3px 3px 10px #ff0000;
            }
            form {
                margin: 20px auto;
                padding: 20px;
                max-width: 600px;
                text-align: center;
            }
            input[type="file"], input[type="number"], button {
                margin: 10px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                text-transform: uppercase;
                border-radius: 50px;
                border: none;
                cursor: pointer;
            }
            input[type="file"], input[type="number"] {
                color: white;
                background: #550000;
            }
            button {
                background: linear-gradient(90deg, #ff0000, #ffffff);
                color: #000000;
                box-shadow: 0px 4px 15px rgba(255, 0, 0, 0.5);
            }
            button:hover {
                transform: scale(1.1);
                box-shadow: 0px 6px 20px rgba(255, 0, 0, 0.8);
            }
        </style>
    </head>
    <body>
        <h1>Gaussian Blur Tool</h1>
        <form action="/gaussian-blur-tool" method="POST" enctype="multipart/form-data">
            <input type="file" name="file" accept="image/*" required>
            <br>
            <label for="level">Blur/Noise Level (1-50):</label>
            <br>
            <input type="number" name="level" id="level" min="1" max="50" required>
            <br>
            <button type="submit" name="filter_type" value="median_blur">Apply Median Blur</button>
            <button type="submit" name="filter_type" value="bilateral_filter">Apply Bilateral Filter</button>
        </form>
    </body>
    </html>
    ''')

# Route untuk memproses gambar dan menampilkan hasil di halaman baru
@app.route('/process/<filename>/<filter_type>/<int:level>')
def process_image(filename, filter_type, level):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    result_filename = 'result_' + filename
    result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)

    # Proses filter
    img = cv2.imread(filepath)
    if filter_type == 'median_blur':
        level = level if level % 2 == 1 else level + 1  # Pastikan level adalah angka ganjil
        processed_img = cv2.medianBlur(img, level)
    elif filter_type == 'bilateral_filter':
        processed_img = cv2.bilateralFilter(img, level * 2 + 1, level * 10, level * 10)
    cv2.imwrite(result_path, processed_img)

    return render_template_string('''  
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Processed Image</title>
        <style>
            body {
                font-family: 'Poppins', sans-serif;
                background-color: #000000;
                background-image: radial-gradient(circle, #800000, #550000);
                color: white;
                text-align: center;
            }
            img {
                margin: 20px;
                max-width: 90%;
                border: 2px solid white;
                box-shadow: 0px 4px 15px rgba(255, 255, 255, 0.5);
            }
            button {
                background: linear-gradient(90deg, #ff0000, #ffffff);
                color: #000000;
                padding: 15px 30px;
                margin: 20px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 50px;
                border: none;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <h1>Here for the result!</h1>
        <img src="{{ url_for('static', filename='results/' + result_filename) }}" alt="Processed Image">
        <br>
        <a href="/download/{{ result_filename }}">
            <button>Download Image</button>
        </a>
        <br>
        <a href="/">Back to Homepage</a>
    </body>
    </html>
    ''', result_filename=result_filename)

# Route untuk mengunduh hasil
@app.route('/download/<filename>')
def download_file(filename):
    result_path = os.path.join(app.config['RESULT_FOLDER'], filename)
    return send_file(result_path, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(RESULT_FOLDER, exist_ok=True)
    app.run(debug=True)


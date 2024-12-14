from flask import Flask, render_template_string, request, send_file, redirect, url_for
import os
import cv2
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'images/uploaded'
RESULT_FOLDER = 'static/results'  # Simpan gambar hasil di folder static/results
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
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
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
                position: absolute;
                top: 50px;
                left: 50%;
                transform: translateX(-50%); /* Menyesuaikan posisi ke tengah */
                width: 85%; /* Sedikit lebih lebar */
                height: calc(100vh - 50px); /* Kotak hitam hanya untuk ke bawah */
                background: #000000;
                padding: 20px;
                border-radius: 0;
                box-shadow: none;
                opacity: 0.9;
                overflow-y: auto;
                max-width: 10000px; /* Membatasi lebar maksimal */
                transition: all 0.5s ease-in-out; /* Efek transisi lebih lambat */
            }
            .content-container {
                overflow-y: auto;
                max-height: calc(100vh - 100px);
                padding: 20px text-align: center;
            }
            .close-btn {
                position: absolute;
                top: 20px;
                right: 20px;
                background: transparent;
                border: none;
                color: white;
                font-size: 30px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <video autoplay loop muted>
            <source src="{{ url_for('static', filename='background.mp4') }}" type="video/mp4">
            Your browser does not support the video tag.
        </video>

        <div class="content-container">
            <div class="section">
                <h1>Welcome To Our Website</h1>
                <a href="/gaussian-blur-tool">
                    <button>Gaussian Blur Tool</button>
                </a>
            </div>

            <div class="section">
                <div class="about-us" id="about-us">
                    <button class="close-btn" onclick="document.getElementById('about-us').style.display='none';">✖</button>
                    <h1>About Us</h1>
                    <p>
                        Welcome to our website! Our mission is to provide innovative and user-friendly tools for everyone.
                        This platform combines functionality and creativity, offering features like image processing
                        and interactive tools for everyday needs.
                    </p>
                </div>
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
            level = int(request.form.get('level', 5))  # Default level adalah 5 jika tidak diisi
            rotation = int(request.form.get('rotation', 0))  # Ambil nilai rotasi
            if not (1 <= level <= 50):  # Validasi level
                level = 5
            return redirect(url_for('process_image', filename=filename, filter_type=filter_type, level=level, rotation=rotation))

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
            margin: 0;
            padding: 0;
            color: white;
            text-align: center;
            line-height: 1.5;
        }

        /* Video Background */
        video {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: -1; /* Tetap di belakang semua elemen */
        }

        /* Kontainer untuk Konten */
        .content {
            position: relative;
            z-index: 1; /* Pastikan konten berada di atas video */
            padding: 20px;
        }

        form {
            background: rgba(0, 0, 0, 0.5); /* Transparansi */
            border: 1px solid #ff0000;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0px 10px 30px rgba(255, 0, 0, 0.5);
            text-align: center;
            width: 90%;
            max-width: 500px;
            margin: 50px auto;
        }

        h1 {
            font-size: 2.5em;
            margin-top: 50px;
            text-shadow: 3px 3px 10px #ff0000;
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

        /* Tambahan untuk Konten Panjang */
        .extra-content {
            height: 2000px; /* Simulasi konten panjang */
            padding: 20px;
        }

        .extra-content p {
            font-size: 1.2em;
            margin: 20px auto;
            max-width: 800px;
        }
    </style>
</head>
<body>
    <!-- Video Background -->
    <video autoplay loop muted>
        <source src="{{ url_for('static', filename='background.mp4') }}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    
    </head>
    <body>
        <h1>Gaussian Blur Tool</h1>
        <form action="/gaussian-blur-tool" method="POST" enctype="multipart/form-data">
            <input type="file" name="file" accept="image/* ```html
" required>
            <br>
            <label for="level">Blur/Noise Level (1-50):</label>
            <br>
            <input type="number" name="level" id="level" min="1" max="50" required>
            <br>
            <input type="hidden" name="rotation" id="rotation" value="0">
            <button type="submit" name="filter_type" value="median_blur">Apply Median Blur</button>
            <button type="submit" name="filter_type" value="bilateral_filter">Apply Bilateral Filter</button>
        </form>
        <h2>Rotate Uploaded Image</h2>
        <img id="uploadedImage" style="display:none; max-width: 100%; transition: transform 0.5s ease;">
        <button id="rotateButton" style="display:none;">Rotate Image</button>
        <script>
            const rotateButton = document.getElementById('rotateButton');
            const uploadedImage = document.getElementById('uploadedImage');
            let angle = 0;

            document.querySelector('input[type="file"]').addEventListener('change', function(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        uploadedImage.src = e.target.result;
                        uploadedImage.style.display = 'block'; // Show the image
                        rotateButton.style.display = 'inline'; // Show the rotate button
                        angle = 0; // Reset rotation angle
                    };
                    reader.readAsDataURL(file);
                }
            });

            rotateButton.addEventListener('click', function() {
                angle = (angle + 90) % 360; // Rotate 90 degrees
                uploadedImage.style.transform = `rotate(${angle}deg)`;
                document.getElementById('rotation').value = angle; // Update hidden input
            });
        </script>
    </body>
    </html>
    ''')

# Route untuk memproses gambar dan menampilkan hasil di halaman baru
@app.route('/process/<filename>/<filter_type>/<int:level>/<int:rotation>')
def process_image(filename, filter_type, level, rotation):
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

    # Terapkan rotasi
    if rotation != 0:
        # Hitung pusat gambar
        center = (processed_img.shape[1] // 2, processed_img.shape[0] // 2)
        # Buat matriks rotasi
        M = cv2.getRotationMatrix2D(center, rotation, 1.0)
        processed_img = cv2.warpAffine(processed_img, M, (processed_img.shape[1], processed_img.shape[0]))

    # Resize image to standard size (e.g., max width or height of 800 pixels)
    max_size = 800
    height, width = processed_img.shape[:2]
    if height > max_size or width > max_size:
        scaling_factor = max_size / max(height, width)
        new_size = (int(width * scaling_factor), int(height * scaling_factor))
        processed_img = cv2.resize(processed_img, new_size, interpolation=cv2.INTER_AREA)

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
                padding: 20px;
            }
            h1 {
                margin-bottom: 20px; /* Jarak dari gambar */
                font-size: 2.5em;
                text-shadow: 3px 3px 10px #ff0000;
            }
            .result-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin: 20px auto;
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
                margin: 10px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 50px;
                border: none;
                cursor: pointer;
            }
            button:hover {
                transform: scale(1.1);
                box-shadow: 0px 6px 20px rgba(255, 0, 0, 0.8);
            }
        </style>
    </head>
    <body>
        <h1>Here for the result!</h1>
        <div class="result-container">
            <img src="{{ url_for('static', filename='results/' + result_filename) }}" alt="Processed Image">
            <a href="/download/{{ result_filename }}">
                <button>Download Image</button>
            </a>
        </div>
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

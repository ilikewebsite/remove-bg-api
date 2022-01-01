from flask import Flask, request, jsonify
import os
import uuid
from rembg.bg import remove
import numpy as np
import io
from PIL import Image, ImageFile

HOST_URL = "http://127.0.0.1:5000"

ImageFile.LOAD_TRUNCATED_IMAGES = True

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['upload'] = os.path.join(basedir, 'upload')
app.config['images'] = os.path.join(basedir, 'images')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/process-image', methods=['POST'])
def upload_image():
    if request.method == 'POST':
        if 'photo' not in request.files:
            return jsonify(error={"Message": "No photo key in the body"}), 404

        file = request.files['photo']

        if file.filename == '':
            return jsonify(error={"Message": "No image selected for uploading"}), 404

        if file and allowed_file(file.filename):
            extension = os.path.splitext(file.filename)[1]
            f_name = str(uuid.uuid4())
            file.save(os.path.join(app.config['upload'], f_name + extension))
            f = np.fromfile(os.path.join(app.config['upload'], f_name + extension))
            result = remove(f)
            img = Image.open(io.BytesIO(result)).convert("RGBA")
            img.save(os.path.join(app.config['images'], f_name + '.png'))
            if os.path.exists(os.path.join(app.config['upload'], f_name + extension)):
                os.remove(os.path.join(app.config['upload'], f_name + extension))
            return jsonify(response={"success": HOST_URL + "/images/" + f_name + '.png'})
        else:
            return jsonify(error={"Message": "Allowed image types are -> png, jpg, jpeg"}), 404


@app.route('/images/<filename>', methods=['GET'])
def view_image(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["images"], filename)


if __name__ == '__main__':
    app.run(debug=True)

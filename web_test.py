"""web test a trained model, user upload an image,
got a result image with predict lable with probability
"""
from flask import Flask, request, redirect
from werkzeug.utils import secure_filename
import cv2
import os

from download_images import ensure_dir
from test_network import predict, load_tcnn, parse_args


ARGS = None

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"


@app.route("/")
def index():
    "default page is index.html"
    return redirect("static/index.html")


@app.route("/sendfile", methods=["POST"])
def send_file():
    "save uploaded file and predict result image"
    save_dir = app.config["UPLOAD_FOLDER"]
    fileob = request.files["file2upload"]
    filename = secure_filename(fileob.filename)
    save_path = "{}/{}".format(save_dir, filename)
    ensure_dir(save_dir)
    fileob.save(save_path)

    ARGS["image"] = save_path

    result_image = predict(ARGS)
    filename = "result_{}".format(filename)
    result_path = "{}/{}".format(save_dir, filename)
    save_path = "{}/{}/{}".format("static", save_dir, filename)
    ensure_dir(os.path.dirname(save_path))
    cv2.imwrite(save_path, result_image)

    # open and close to update the access time.
    with open(save_path, "r") as f:
        pass

    return result_path  # "successful_upload"


if __name__ == '__main__':
    ARGS = parse_args()
    ARGS["m"] = load_tcnn(ARGS["model"])
    app.run(debug=False，host="0.0.0.0")

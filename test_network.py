
# import the necessary packages
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import numpy as np
import argparse
import imutils
import cv2
from train_network import DEFAULT_TRAIN_IMAGE_SIZE


def parse_args():
    "parse the arguments"
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--model", required=True,
                    help="path to trained model model")
    ap.add_argument("-i", "--image", required=False,
                    help="path to input image")
    ap.add_argument("-l", "--label", required=True,
                    help="label of target image")
    ap.add_argument("-s", "--train_image_size", required=False, type=int, default=DEFAULT_TRAIN_IMAGE_SIZE,
                help="size of training image, default: {}".format(DEFAULT_TRAIN_IMAGE_SIZE))
    args = vars(ap.parse_args())
    return args


def load_image(path, image_size):
    "load the test image"
    image = cv2.imread(path)
    orig = image.copy()

    image = cv2.resize(image, (image_size, image_size))
    image = image.astype("float") / 255.0
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    return image, orig


def load_tcnn(model_path):
    "load the trained convolutional neural network"
    print("[INFO] loading network...")
    model = load_model(model_path)
    return model


def build_label(prob_yes, prob_no, label_yes):
    "show the result "
    label = "Not {}".format(label_yes) if prob_no > prob_yes else label_yes
    proba = prob_no if prob_no > prob_yes else prob_yes
    label = "{}: {:.2f}%".format(label, proba * 100)
    return label


def build_result(image, label):
    # draw the label on the image
    output = imutils.resize(image, width=400)
    cv2.putText(output, label, (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    return output


def show_result(output):
    # show the output image
    cv2.imshow("Output", output)
    cv2.waitKey(0)


def do_it(args, wait_key=False):
    result = predict(args)
    show_result(result)

def predict(args):
    "all logic execute here"
    (image, orig) = load_image(args["image"], args["train_image_size"])
    model = args["m"] if "m" in args else load_tcnn(args["model"])
    label = args["label"]
    print("input label is:{}".format(label))

    # classify the input image
    (noProb, yesProb) = model.predict(image)[0]
    print("prob is:{}, {}".format(noProb, yesProb))
    # print(str((noProb, yesProb)))
    label = build_label(yesProb, noProb, label)
    print(label)

    result = build_result(orig, label)
    return result


if __name__ == "__main__":
    ARGS = parse_args()
    if "image" in ARGS and ARGS["image"] is not None:
        # print("image is:{}".format(ARGS["image"]))
        do_it(ARGS)
    else:
        ARGS["m"] = load_tcnn(ARGS["model"])
        img = None
        while img != "q":
            img = raw_input("image path('q' for quit):")
            if img == "q":
                break
            ARGS["image"] = img
            do_it(ARGS)

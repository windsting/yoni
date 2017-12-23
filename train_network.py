# set the matplotlib backend so figures can be saved in the background
import matplotlib
matplotlib.use("Agg")

# import the necessary packages
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from keras.preprocessing.image import img_to_array
from keras.utils import to_categorical
from imutils import paths
import matplotlib.pyplot as plt
import numpy as np
import argparse
import random
import cv2
import os

from nn.mycnn import MyCNN
from download_images import ensure_dir


# set labels for datas
train_labels = {"yes": 1}
DEFAULT_TRAIN_IMAGE_SIZE = 28
DEFAULT_OUTPUT = "output"


def parse_args():
    "parse the arguments"

    # default values
    DEFAULT_EPOCHS = 25
    DEFAULT_LEARNING_RATE = 1e-3
    DEFAULT_BATCH_SIZE = 32

    # construct the argument parse
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--dataset", required=True,
                    help="path to input dataset")
    ap.add_argument("-m", "--model", required=True,
                    help="name of the output model")
    ap.add_argument("-o", "--output", type=str, default=DEFAULT_OUTPUT,
                    help="path to output the model, default: {}".format(DEFAULT_OUTPUT))
    ap.add_argument("-e", "--epochs", required=False, type=int, default=DEFAULT_EPOCHS,
                    help="epochs of training, default: {}".format(DEFAULT_EPOCHS))
    ap.add_argument("-l", "--learn_rate", required=False, type=float, default=DEFAULT_LEARNING_RATE,
                    help="learning rate of training, default: {}".format(DEFAULT_LEARNING_RATE))
    ap.add_argument("-b", "--batch_size", required=False, type=int, default=DEFAULT_BATCH_SIZE,
                    help="batch size of training, default: {}".format(DEFAULT_BATCH_SIZE))
    ap.add_argument("-s", "--train_image_size", required=False, type=int, default=DEFAULT_TRAIN_IMAGE_SIZE,
                    help="size of training image, default: {}".format(DEFAULT_TRAIN_IMAGE_SIZE))
    ap.add_argument("-p", "--plot", type=str, default=None,
                    help="path to output accuracy/loss plot")

    return vars(ap.parse_args())


def load_image(path, size):
    "Load image at path, resize it to (size,size), and convert to an array"
    try:
        image = cv2.imread(path)
        image = cv2.resize(image, (size, size))
        image = img_to_array(image)
    except:
        if path.endswith(".jpg"):
            print("removing invalid file: {}".format(path))
            os.remove(path)
        return None
    return image


def extract_label(path, label_dict, label_pos=-2):
    "extract the class label from the image path"
    label = path.split(os.path.sep)[label_pos]
    if label in label_dict:
        label = label_dict[label]
    else:
        label = 0
    return label


def plot(epochs, H, fig_file):
    "plot the training loss and acuracy"
    plt.style.use("ggplot")
    plt.figure()
    N = epochs
    plt.plot(np.arange(0, N), H.history["loss"], label="train_loss")
    plt.plot(np.arange(0, N), H.history["val_loss"], label="test_loss")
    plt.plot(np.arange(0, N), H.history["acc"], label="train_acc")
    plt.plot(np.arange(0, N), H.history["val_acc"], label="test_acc")
    plt.title("Training Loss and Accuracy on Yes/No")
    plt.xlabel("Epoch #")
    plt.ylabel("Loss/Accuracy")
    plt.legend(loc="lower left")
    plt.savefig(fig_file)


def do_it(args):
    # initialize the number of epochs to train for, initial learning rate,
    # and batch size
    EPOCHS = args["epochs"]
    INIT_LR = args["learn_rate"]
    BS = args["batch_size"]

    image_size = args["train_image_size"]

    filepath = args["output"]
    path_valid = ensure_dir(filepath)
    if path_valid is not None:
        print("Invalid output dir: {} -- {}".format(filepath, path_valid))
        return


    # initialize the data and labels
    print("[INFO] loading images...")
    dataset_path = args["dataset"]

    # grab the image paths and randomly shuffle them
    data, labels = args["data"] if "data" in args else load_data(dataset_path, image_size)

    dataset_size = len(data)

    print("[INFO] EPOCHS: {}".format(EPOCHS))
    print("[INFO] INIT_LR: {}".format(INIT_LR))
    print("[INFO] BATCH_SIZE: {}".format(BS))
    print("[INFO] DATASET_SIZE: {}".format(dataset_size))

    params_info = "_EPOCHS{}_LR{}_BS{}_TIS{}_DSS{}".format(EPOCHS, INIT_LR, BS, image_size, dataset_size)
    model_name = "{}{}".format(args["model"], params_info)
    model_name = os.path.sep.join((filepath, model_name))
    print("[INFO] model file name: {}".format(model_name))
    plot_name = args["model"] if args["plot"] is None else args["plot"]
    plot_name = "{}{}.png".format(plot_name, params_info)
    plot_name = os.path.sep.join((filepath, plot_name))
    print("[INFO] plot file name: {}".format(plot_name))

    # partition the data into trainint and testing splits using 75% of
    # the data for training and the remaining 25% for testing
    (trainX, testX, trainY, testY) = train_test_split(
        data, labels, test_size=0.25, random_state=42)

    # convert the labels from integers to vectors
    class_num = len(train_labels) + 1
    trainY = to_categorical(trainY, num_classes=class_num)
    testY = to_categorical(testY, num_classes=class_num)

    # construct the image generator for data augmentation
    aug = ImageDataGenerator(
        rotation_range=30, width_shift_range=0.1, height_shift_range=0.1,
        shear_range=0.2, zoom_range=0.2, horizontal_flip=True,
        fill_mode='nearest')

    # initial the model
    print("[INFO] compiling model...")
    model = MyCNN.build(width=image_size, height=image_size,
                        depth=3, classes=class_num)
    opt = Adam(lr=INIT_LR, decay=INIT_LR / EPOCHS)
    model.compile(loss="binary_crossentropy",
                  optimizer=opt, metrics=["accuracy"])

    # train the network
    print("[INFO] training network...")
    H = model.fit_generator(aug.flow(trainX, trainY, batch_size=BS), validation_data=(
        testX, testY), steps_per_epoch=len(trainX), epochs=EPOCHS, verbose=1)

    # save the model to disk
    print("[INFO] serializing network...")
    model.save(model_name)

    plot(EPOCHS, H, plot_name)


def load_data(dataset_path, load_size):
    "load data and create labels from dataset_path"
    print("gonna load data in [{}] with size:{}".format(dataset_path, load_size))
    # grab the image paths and randomly shuffle them
    image_paths = sorted(list(paths.list_images(dataset_path)))
    random.seed(42)
    random.shuffle(image_paths)

    data = []
    labels = []
    for image_path in image_paths:
        # store image in the data list
        image = load_image(image_path, load_size)
        if image is None:
            continue
        data.append(image)

        # store the label
        labels.append(extract_label(image_path, train_labels))

    # scale the raw pixel intensities to the range [0. 1]
    data = np.array(data, dtype='float') / 255.0
    labels = np.array(labels)
    return data, labels


if __name__ == "__main__":
    args = parse_args()
    do_it(args)

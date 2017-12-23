# import the necessary packages
from imutils import paths
import argparse
import requests
import cv2
import os
from threading import Thread
from collections import deque
import threading
import hashlib


def parse_args():
    "construct the argument parse and parse the arguments"
    ap = argparse.ArgumentParser()
    ap.add_argument("-u", "--urls", required=True, help="path to file containing image URLs")
    ap.add_argument("-o", "--output", required=True, help="path to output directory of images")
    ap.add_argument("-i", "--index", required=False, type=int, default=0, help="start index of saved images")
    ap.add_argument("-t", "--threads", required=False, type=int, default=8, help="download thread count")
    return vars(ap.parse_args())


def download(queue, output, request_wait_seconds=30):
    "download file in queue, and save them to output"
    while True:
        entry = None
        try:
            entry = queue.pop()
        except:
            # pop() failed, the queue is empty
            break
        if entry is None:
            break

        url = entry["url"]
        index = entry["index"]
        # print("{} gonna download:{}".format(threading.current_thread(), url))
        try:
            # try to download the image
            req = requests.get(url, timeout=request_wait_seconds)

            # save the image to disk
            filename = "{}.jpg".format(str(index).zfill(8))
            p = os.path.sep.join([output, filename])
            f = open(p, "wb")
            f.write(req.content)
            f.close()

            # update the counter
            print("[INFO] downloaded: {}".format(p))

        # handle if any exceptions are thrown during the download process
        except:
            print("[INFO] error downloading {}".format(url))


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()



def prune_folder(path):
    """prune the folder, remove invalid(can not be cv2.imread) images,
    and for duplicated(same MD5) images, remove the duplicate.
    """
    digests = set()
    file_count = 0
    delete_count = 0
    # loop over the image paths we just downloaded
    for image_path in paths.list_images(path):
        # initialize if the image should be deleted or not
        file_count += 1

        delete = None
        digest = md5(image_path)
        if digest in digests:
            delete = "duplicate"
        else:
            digests.add(digest)
            # try to load the image
            try:
                image = cv2.imread(image_path)

                # if the image is `None` then we could not properly load it
                # from disk, so delete it
                if image is None:
                    delete = "imread got None"

            # if OpenCV cannot load the image then the image is likely
            # corrupt so we should delete it
            except:
                delete = "Can not imread"

        # check to see if the image should be deleted
        if delete is not None:
            delete_count += 1
            # print("[INFO] [{}] deleting {}".format(delete, image_path))
            os.remove(image_path)
    print("{} in {} files removed.".format(delete_count, file_count))

def ensure_dir(path):
    "Ensure the directory of 'path' is valid"
    if os.path.exists(path):
        if not os.path.isdir(path):
            return "it is not a directory"
        if not os.access(path, os.W_OK):
            return "it is not writable"
    else:
        os.makedirs(path)
        if not os.path.exists(path):
            return "Can't create directory: {}".format(path)
    return None


def do_it(args):
    # grab the list of URLs from the input file, then initialize the
    # total number of images downloaded thus far
    rows = open(args["urls"]).read().strip().split("\n")

    filepath = args["output"]
    path_valid = ensure_dir(filepath)
    if path_valid is not None:
        print("Invalid output dir: {} -- {}".format(filepath, path_valid))
        return
    print("gonna save to: {}".format(filepath))

    print("file line count: {}".format(len(rows)))

    rows = set(sorted(rows))
    print("url count: {}".format(len(rows)))

    entries = []
    start_index = args["index"]
    for index, url in enumerate(rows):
        entries.append({"url": url, "index": index + start_index})

    entries = deque(entries)

    threads = []
    for i in range(10):
        t = Thread(target=download, args=(entries,filepath,args["threads"]))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    prune_folder(filepath)


if __name__ == "__main__":
    print("hello from download_images.py")
    ARGS = parse_args()
    do_it(ARGS)

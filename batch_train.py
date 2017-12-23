
from train_network import load_data, do_it, DEFAULT_TRAIN_IMAGE_SIZE


dataset_path = "asset/santa"
model = "santa"
train_image_size = DEFAULT_TRAIN_IMAGE_SIZE

EPOCHS = (15, 25, 50)
LEARN_RATES = (0.001, 0.0001)
BATCH_SIZES = (32, 64, 100)
TRAIN_IMAGE_SIZES = (DEFAULT_TRAIN_IMAGE_SIZE,)


def train():
    for tis in TRAIN_IMAGE_SIZES:
        data_label = load_data(dataset_path, tis)
        for e in EPOCHS:
            for lr in LEARN_RATES:
                for bs in BATCH_SIZES:
                    ARGS = {
                        "dataset" : dataset_path,
                        "model": model,
                        "epochs" : e,
                        "learn_rate" : lr,
                        "batch_size" : bs,
                        "train_image_size" : tis,
                        "plot" : None,
                        "data": data_label
                    }
                    do_it(ARGS)


if __name__ == "__main__":
    train()

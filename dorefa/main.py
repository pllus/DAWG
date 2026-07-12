#!/usr/bin/env python3
import sys
from resnet_dorefa import Model, run_image
from tensorpack import SmartInit


def main():
    # Configuration
    MODEL_PATH = "ResNet-18-14f.npz"
    IMAGES = [
        "a.jpg",
        "b.jpg",
    ]

    run_image(
        model=Model(),
        sess_init=SmartInit(MODEL_PATH),
        inputs=IMAGES,
    )


if __name__ == "__main__":
    main()
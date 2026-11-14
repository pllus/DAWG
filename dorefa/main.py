#!/usr/bin/env python3
import os
import tensorflow as tf

from tensorpack import SmartInit
from tensorpack.tfutils import varmanip

import tensorflow as tf

tf.variable_scope = tf.compat.v1.variable_scope
tf.placeholder = tf.compat.v1.placeholder
tf.Session = tf.compat.v1.Session
tf.get_variable = tf.compat.v1.get_variable
tf.global_variables_initializer = tf.compat.v1.global_variables_initializer

tf.compat.v1.disable_eager_execution()

from resnet_dorefa import Model, run_image

MODEL_PATH = "ResNet-18-14f.npz"


def make_fake_model():
    print(f"{MODEL_PATH} not found. Creating fake pretrained model...")

    tf.compat.v1.reset_default_graph()
    tf.compat.v1.disable_eager_execution()

    model = Model()

    input_tensor = tf.compat.v1.placeholder(
        tf.float32, [1, 224, 224, 3], name="input")
    label_tensor = tf.compat.v1.placeholder(
        tf.int32, [1], name="label")

    model.build_graph(input_tensor, label_tensor)

    with tf.compat.v1.Session() as sess:
        sess.run(tf.compat.v1.global_variables_initializer())
        varmanip.dump_session_params(MODEL_PATH)

    print(f"Fake model saved to {MODEL_PATH}")


def main():
    if not os.path.exists(MODEL_PATH):
        make_fake_model()

    run_image(
        model=Model(),
        sess_init=SmartInit(MODEL_PATH),
        inputs=[
            "a.jpg",
            "b.jpg",
        ],
    )


if __name__ == "__main__":
    main()
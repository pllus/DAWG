import os
import finn.builder.build_dataflow as build
import finn.builder.build_dataflow_config as build_cfg
from finn.transformation.move_reshape import RemoveCNVtoFCFlatten
from finn.transformation.streamline.reorder import AbsorbConsecutiveTransposes
from finn.transformation.infer_data_layouts import InferDataLayouts

# 1. Define a custom step to strip out the brown Reshape/Flatten node
def custom_remove_reshape_step(model, cfg):
    model = model.transform(RemoveCNVtoFCFlatten())
    model = model.transform(AbsorbConsecutiveTransposes())
    model = model.transform(InferDataLayouts())
    return model

# 2. Copy the default 19 steps and inject our custom step right before partitioning
steps = list(build_cfg.default_build_dataflow_steps)
partition_idx = steps.index("step_create_dataflow_partition")
steps.insert(partition_idx, custom_remove_reshape_step)

# 3. Set up your build configuration
cfg = build.DataflowBuildConfig(
    output_dir="output_my_accelerator",
    synth_clk_period_ns=10.0,
    board="KV260",                          # Make sure board is set
    fpga_part="xck26-sfvc784-2LV-c",        # Must match your KV260 part
    steps=steps,
    generate_outputs=[
        build_cfg.DataflowOutputType.STITCHED_IP,
        build_cfg.DataflowOutputType.BITFILE,
    ]
)

# 4. Execute the build pipeline
model_file = "/mnt/c/pluz/Coding/DAWG/dorefa/converter/model.onnx"
build.build_dataflow_cfg(model_file, cfg)
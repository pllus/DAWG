import os
from finn.builder.build_dataflow import build_dataflow_config
from finn.builder.build_dataflow_config import DataflowBuildConfig, DataflowOutputType

def main(): 
    # 1. Define your target hardware configuration
    cfg = DataflowBuildConfig(
        output_dir="output_my_accelerator",
        synth_clk_period_ns=10.0,            # Target clock frequency (e.g., 100 MHz)
        board="KV260",                       # Target board (or leave None and specify fpga_part)
        fpga_part="xck26-sfvc784-2LV-c",     # KV260 part number if not using full board automation
        auto_fifo_depths=True,               # Automatically size data-streaming FIFOs
        generate_outputs=[
            DataflowOutputType.STITCHED_IP,  # Packages the whole net into a single Vivado IP block
            DataflowOutputType.VIVADO_PROJECT # Creates the actual Vivado IPI project directory
        ]
    )

    # 2. Point to your exported Brevitas/ONNX model
    # (By default, FINN expects the model at this path or specified via config)
    model_file = "resnet50-v2-7.onnx" 

    print("Starting FINN dataflow build to generate HDL/IP...")
    
    # 3. Run the automated compiler pipeline
    build_dataflow(model_file, cfg)
    
    print("Build complete! Check the 'output_my_accelerator' folder.")

if __name__ == "__main__":
    main()
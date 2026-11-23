import os
import glob

INPUT_DIR  = "./fpga_weights"
OUTPUT_DIR = "./fpga_ready_files"

os.makedirs(OUTPUT_DIR, exist_ok=True)

txt_files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.txt")))

# This list will become your metadata
layer_configs = []

for txt_path in txt_files:
    filename = os.path.basename(txt_path)
    name_no_ext = os.path.splitext(filename)[0]

    shape = []
    weights = []

    with open(txt_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                if 'shape:' in line:
                    shape_str = line.split('shape:')[1].strip()
                    shape = [int(x) for x in shape_str.split()]
                continue
            weights.append(float(line))

    if len(shape) < 4:
        print(f"[!] SKIP {filename}: bad shape")
        continue

    out_ch, in_ch, kh, kw = shape
    kernel_size = kh * kw
    total_kernels = out_ch * in_ch
    expected = total_kernels * kernel_size

    if len(weights) != expected:
        print(f"[!] ERROR {filename}: expected {expected}, got {len(weights)}")
        continue

    # Quantize to 1-bit
    bits = [1 if w >= 0 else 0 for w in weights]

    # Pack into kernel_size-bit words
    words = []
    for k in range(total_kernels):
        w = 0
        for i in range(kernel_size):
            w |= (bits[k * kernel_size + i] << i)
        words.append(w)

    # Write COE (packed, width = kernel_size)
    coe_path = os.path.join(OUTPUT_DIR, f"{name_no_ext}.coe")
    with open(coe_path, 'w') as f:
        f.write("memory_initialization_radix=2;\n")
        f.write("memory_initialization_vector=\n")
        for i, w in enumerate(words):
            sep = "," if i < len(words) - 1 else ";"
            f.write(f"{w:0{kernel_size}b}{sep}\n")

    # Store metadata
    layer_configs.append({
        'name': name_no_ext,
        'out_ch': out_ch,
        'in_ch': in_ch,
        'kh': kh,
        'kw': kw,
        'kernel_size': kernel_size,
        'total_kernels': total_kernels,
        'coe_file': f"{name_no_ext}.coe"
    })

    print(f"[+] {filename:<45s} kernel={kh}x{kw}  "
          f"width={kernel_size}  depth={total_kernels}")

# ============================================
config_path = os.path.join(OUTPUT_DIR, "layer_config.txt")
with open(config_path, 'w') as f:
    f.write("# name out_ch in_ch kh kw kernel_size total_kernels coe_file\n")
    for cfg in layer_configs:
        f.write(f"{cfg['name']} "
                f"{cfg['out_ch']} {cfg['in_ch']} "
                f"{cfg['kh']} {cfg['kw']} "
                f"{cfg['kernel_size']} "
                f"{cfg['total_kernels']} "
                f"{cfg['coe_file']}\n")

print(f"\n[SUCCESS] {len(layer_configs)} layers converted")
print(f"[SUCCESS] Config written to: {config_path}")
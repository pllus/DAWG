import os
import torch 


def dump_layer0_vectors(model, image, out_dir, abits=4):
    os.makedirs(out_dir, exist_ok=True)
    model.eval()
    n = 2**abits - 1
    blk = model.layers[0]

    with torch.no_grad():
        # 1) integer input activations
        x = model.conv0(image.unsqueeze(0).to(device))
        a = blk.act_q(F.relu(blk.bn0(x)))
        a_int = torch.round(a * n).to(torch.int64)                 # [1,16,32,32]
        assert (a_int.double() / n - a.double()).abs().max() < 1e-5

        # 2) binary weights and raw integer accumulators
        w = blk.conv0.weight                                       # [16,16,3,3]
        E = w.abs().mean().item()
        w_sign = torch.where(w >= 0, torch.ones_like(w), -torch.ones_like(w))
        acc = F.conv2d(a_int.double(), w_sign.double(), padding=1).round().to(torch.int64)

        conv_ref = blk.conv0(a)                                    # float reference from the model
        err = (acc.double() * E / n - conv_ref.double()).abs().max().item()
        print(f'check conv: max |acc*E/n - model conv| = {err:.2e}   (want ~1e-5 or less)')

        # 3) BN folding and expected block output
        bn = blk.bn1
        inv = 1.0 / torch.sqrt(bn.running_var.double() + bn.eps)
        S = bn.weight.double() * inv * E / n
        B = bn.bias.double() - bn.weight.double() * bn.running_mean.double() * inv
        y = acc.double() * S.view(1, -1, 1, 1) + B.view(1, -1, 1, 1)
        out_int = torch.clamp(torch.round(y * n), 0, n).to(torch.int64)
        ref_out = torch.round(blk.act_q(F.relu(bn(conv_ref))) * n).to(torch.int64)
        print('check BN fold: mismatching outputs =', (out_int != ref_out).sum().item(), 'of', out_int.numel())

    C, H, W = 16, 32, 32
    hexw = C * abits // 4

    def pack(t):                      # t: [1,C,H,W] ints -> one hex word per pixel, channel 0 in the LSBs
        arr = t[0].permute(1, 2, 0).cpu().numpy()          # [H,W,C]
        return [format(sum(int(arr[yy, xx, c]) << (abits * c) for c in range(C)), f'0{hexw}x')
                for yy in range(H) for xx in range(W)]     # raster order: row by row

    open(f'{out_dir}/input_act.hex', 'w').write('\n'.join(pack(a_int)) + '\n')
    open(f'{out_dir}/expected_out.hex', 'w').write('\n'.join(pack(out_int)) + '\n')
    np.savetxt(f'{out_dir}/expected_acc.txt',
               acc[0].permute(1, 2, 0).reshape(-1, C).cpu().numpy(), fmt='%d')   # 1024 lines x 16 signed ints

    json.dump({'E': E, 'n': n,
               'S': S.tolist(), 'B': B.tolist(),
               'gamma': bn.weight.tolist(), 'beta': bn.bias.tolist(),
               'mean': bn.running_mean.tolist(), 'var': bn.running_var.tolist(), 'eps': bn.eps},
              open(f'{out_dir}/bn_params.json', 'w'), indent=2)

    # 4) regenerate the packed COE from the NEW weights: 16 words x 144 bits (1 = +1, 0 = -1)
    bits = (w_sign > 0).int().cpu().numpy().reshape(16, -1)    # [out, ci*9+ky*3+kx]
    words = [''.join(str(b) for b in row[::-1]) for row in bits]   # LSB = weight 0
    open(f'{out_dir}/layers_0_conv0_weight_q_packed.coe', 'w').write(
        'memory_initialization_radix=2;\nmemory_initialization_vector=\n' + ',\n'.join(words) + ';\n')

    print('acc range:', acc.min().item(), acc.max().item(), '| E =', E)

img, label = eval_dataset[0]
dump_layer0_vectors(model, img, os.path.join(WEIGHT_DIR, 'fpga_ready_files'), abits=ABITS)
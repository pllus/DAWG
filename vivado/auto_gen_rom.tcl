# Define your layers: {name width depth coe_file}
set layers {
    {layers_0_conv0   9 4096  "layers.0.conv0.coe"}
    {layers_0_conv1   9 4096  "layers.0.conv1.coe"}
    {layers_1_conv0   9 4096  "layers.1.conv0.coe"}
    {layers_1_conv1   9 4096  "layers.1.conv1.coe"}
    {layers_2_conv0   9 4096  "layers.2.conv0.coe"}
    {layers_2_conv1   9 4096  "layers.2.conv1.coe"}
    {layers_3_conv0   9 4096  "layers.3.conv0.coe"}
    {layers_3_conv1   9 4096  "layers.3.conv1.coe"}
    {layers_3_skip    9 4096  "layers.3.skip_conv.coe"}
    {layers_4_conv0   9 4096  "layers.4.conv0.coe"}
    {layers_4_conv1   9 4096  "layers.4.conv1.coe"}
    {layers_5_conv0   9 4096  "layers.5.conv0.coe"}
    {layers_5_conv1   9 4096  "layers.5.conv1.coe"}
    {layers_6_conv0   9 4096  "layers.6.conv0.coe"}
    {layers_6_conv1   9 4096  "layers.6.conv1.coe"}
    {layers_6_skip    9 4096  "layers.6.skip_conv.coe"}
    {layers_7_conv0   9 4096  "layers.7.conv0.coe"}
    {layers_7_conv1   9 4096  "layers.7.conv1.coe"}
    {layers_8_conv0   9 4096  "layers.8.conv0.coe"}
    {layers_8_conv1   9 4096  "layers.8.conv1.coe"}
}

foreach layer $layers {
    lassign $layer name width depth coe

    create_ip -name blk_mem_gen -vendor xilinx.com -library ip \
        -module_name wrom_${name}

    set_property -dict [list \
        CONFIG.Memory_Type {Single_Port_ROM} \
        CONFIG.Write_Width_A $width \
        CONFIG.Write_Depth_A $depth \
        CONFIG.Load_Init_File {true} \
        CONFIG.Coe_File [file normalize $coe] \
    ] [get_ips wrom_${name}]

    generate_target all [get_ips wrom_${name}]
    puts "Generated wrom_${name}"
}

puts "All weight ROMs generated!"
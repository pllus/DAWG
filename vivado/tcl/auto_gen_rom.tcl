
set CONFIG_FILE "./fpga_ready_files/layer_config.txt"
set COE_DIR     "./fpga_ready_files"

# Read config file
set fp [open $CONFIG_FILE r]
set file_data [read $fp]
close $fp

foreach line [split $file_data "\n"] {
    # Skip comments and empty lines
    if {[string match "#*" $line] || [string trim $line] eq ""} continue

    # Parse: name out_ch in_ch kh kw kernel_size total_kernels coe_file
    set fields [split [string trim $line]]
    if {[llength $fields] < 8} continue

    set name          [lindex $fields 0]
    set out_ch        [lindex $fields 1]
    set in_ch         [lindex $fields 2]
    set kh            [lindex $fields 3]
    set kw            [lindex $fields 4]
    set kernel_size   [lindex $fields 5]
    set total_kernels [lindex $fields 6]
    set coe_file      [lindex $fields 7]

    set ip_name "wrom_${name}"
    # Clean dots for valid Verilog module name
    set ip_name [string map {"." "_"} $ip_name]

    set coe_path [file normalize "${COE_DIR}/${coe_file}"]

    puts "Creating IP: ${ip_name} (width=${kernel_size}, depth=${total_kernels}, kernel=${kh}x${kw})"

    create_ip -name blk_mem_gen \
              -vendor xilinx.com \
              -library ip \
              -module_name $ip_name

    set_property -dict [list \
        CONFIG.Memory_Type     {Single_Port_ROM} \
        CONFIG.Write_Width_A   $kernel_size \
        CONFIG.Write_Depth_A   $total_kernels \
        CONFIG.Read_Width_A    $kernel_size \
        CONFIG.Read_Depth_A    $total_kernels \
        CONFIG.Load_Init_File  {true} \
        CONFIG.Coe_File        $coe_path \
    ] [get_ips $ip_name]

    generate_target all [get_ips $ip_name]
}

puts "All weight ROM IPs generated!"

// Layer selector from your FSM
reg [4:0] layer_sel;
reg [11:0] kernel_addr;

// All ROM outputs
wire [8:0] w_l0c0, w_l0c1, w_l1c0, w_l1c1;
wire [8:0] w_l2c0, w_l2c1, w_l3c0, w_l3c1, w_l3s;
wire [8:0] w_l4c0, w_l4c1, w_l5c0, w_l5c1;
wire [8:0] w_l6c0, w_l6c1, w_l6s, w_l7c0, w_l7c1;
wire [8:0] w_l8c0, w_l8c1;


// Instantiate all ROMs
wrom_layers_0_conv0 u0 (.clka(clk), .addra(kernel_addr), .douta(w_l0c0));
wrom_layers_0_conv1 u1 (.clka(clk), .addra(kernel_addr), .douta(w_l0c1));


// MUX to select active layer's weights
reg [8:0] active_weights;
always @(*) begin
    case (layer_sel)
        5'd0:  active_weights = w_l0c0;
        5'd1:  active_weights = w_l0c1;
        5'd2:  active_weights = w_l1c0;
        // ... etc ...
        5'd19: active_weights = w_l8c1;
        default: active_weights = 9'd0;
    endcase
end

//TODO PE
dorefa_pe u_pe (
    .clk(clk),
    .rst_n(rst_n),
    .weight_bits(active_weights),
    .act_bits(act_bits),
    .valid_in(pe_valid),
    .result(pe_result),
    .valid_out(pe_valid_out)
);
// Created with Corsair vgit-latest
// Register map module v1.0

module rmap #(
    parameter ADDR_W = 8,
    parameter DATA_W = 16,
    parameter STRB_W = DATA_W / 8
)(
    // System
    input clk,
    input rst,
    // CSR: LEDCTRL
    output  csr_ledctrl_ren_out,
    output  csr_ledctrl_gen_out,
    output  csr_ledctrl_ben_out,
    // Local Bus
    input  [ADDR_W-1:0] lb_waddr,
    input  [DATA_W-1:0] lb_wdata,
    input               lb_wen,
    input  [STRB_W-1:0] lb_wstrb,
    output              lb_wready,
    input  [ADDR_W-1:0] lb_raddr,
    input               lb_ren,
    output [DATA_W-1:0] lb_rdata,
    output              lb_rvalid
);

//------------------------------------------------------------------------------
// CSR:
// [0x0] - LEDCTRL - LED control register
//------------------------------------------------------------------------------
wire [15:0] csr_ledctrl_rdata;

assign csr_ledctrl_rdata[3:1] = 3'h0;
assign csr_ledctrl_rdata[7:5] = 3'h0;
assign csr_ledctrl_rdata[15:9] = 7'h0;

wire csr_ledctrl_wen;
assign csr_ledctrl_wen = lb_wen && (lb_waddr == 8'h0);
wire csr_ledctrl_ren;
assign csr_ledctrl_ren = lb_ren && (lb_raddr == 8'h0);

//---------------------
// Bit field:
// LEDCTRL[0] - REN - Enable red led
// rw
//---------------------
reg  csr_ledctrl_ren_out_ff;
assign csr_ledctrl_rdata[0] = csr_ledctrl_ren_out_ff;
assign csr_ledctrl_ren_out = csr_ledctrl_ren_out_ff;

always @(posedge clk) begin
    if (rst) begin
        csr_ledctrl_ren_out_ff <= 1'b0;
    end else if (csr_ledctrl_wen) begin
        if (lb_wstrb[0])
            csr_ledctrl_ren_out_ff <= lb_wdata[0];
    end
end
//---------------------
// Bit field:
// LEDCTRL[4] - GEN - Enable green led
// rw
//---------------------
reg  csr_ledctrl_gen_out_ff;
assign csr_ledctrl_rdata[4] = csr_ledctrl_gen_out_ff;
assign csr_ledctrl_gen_out = csr_ledctrl_gen_out_ff;

always @(posedge clk) begin
    if (rst) begin
        csr_ledctrl_gen_out_ff <= 1'b0;
    end else if (csr_ledctrl_wen) begin
        if (lb_wstrb[0])
            csr_ledctrl_gen_out_ff <= lb_wdata[4];
    end
end
//---------------------
// Bit field:
// LEDCTRL[8] - BEN - Enable blue led
// rw
//---------------------
reg  csr_ledctrl_ben_out_ff;
assign csr_ledctrl_rdata[8] = csr_ledctrl_ben_out_ff;
assign csr_ledctrl_ben_out = csr_ledctrl_ben_out_ff;

always @(posedge clk) begin
    if (rst) begin
        csr_ledctrl_ben_out_ff <= 1'b0;
    end else if (csr_ledctrl_wen) begin
        if (lb_wstrb[1])
            csr_ledctrl_ben_out_ff <= lb_wdata[8];
    end
end

//------------------------------------------------------------------------------
// Write ready
//------------------------------------------------------------------------------
assign lb_wready = 1'b1;

//------------------------------------------------------------------------------
// Read address decoder
//------------------------------------------------------------------------------
reg [15:0] lb_rdata_ff;
always @(posedge clk) begin
    if (rst) begin
        lb_rdata_ff <= 16'hdead;
    end else if (lb_ren) begin
        case (lb_raddr)
            8'h0: lb_rdata_ff <= csr_ledctrl_rdata;
            default: lb_rdata_ff <= 16'hdead;
        endcase
    end else begin
        lb_rdata_ff <= 16'hdead;
    end
end
assign lb_rdata = lb_rdata_ff;

//------------------------------------------------------------------------------
// Read data valid
//------------------------------------------------------------------------------
reg lb_rvalid_ff;
always @(posedge clk) begin
    if (rst) begin
        lb_rvalid_ff <= 1'b0;
    end else if (lb_ren && lb_rvalid) begin
        lb_rvalid_ff <= 1'b0;
    end else if (lb_ren) begin
        lb_rvalid_ff <= 1'b1;
    end
end

assign lb_rvalid = lb_rvalid_ff;

endmodule
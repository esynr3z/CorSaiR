`timescale 1ns/1ps

module tb_ro;

// Test environment with DUT and bridge to LocalBus
`include "env.svh"

// Test body
int errors = 0;
logic [ADDR_W-1:0] addr;
logic [DATA_W-1:0] data;
logic [STRB_W-1:0] strb;

// test RO registers with no modifiers
task test_basic;
    $display("%t, Start basic tests!", $time);
    // test STATUS register
    // simple read with hardware control
    addr = 'h40;
    csr_status_dir_in = 0;
    mst.read(addr, data);
    if ((data >> 4) & 1 != 0)
        errors++;
    csr_status_dir_in = 1;
    mst.read(addr, data);
    if ((data >> 4) & 1 != 1)
        errors++;
endtask

// test RO registers with external update
task test_ext_upd;
    $display("%t, Start external update tests!", $time);
    // test STATUS register
    addr = 'h40;
    // hardware update and read (also check that write has no action)
    mst.read(addr, data);
    if (((data >> 8) & 1) != 0)
        errors++;
    @(posedge clk);
    csr_status_err_in = 1'b1;
    csr_status_err_upd = 1'b1;
    @(posedge clk);
    csr_status_err_upd = 1'b0;
    mst.read(addr, data);
    if (((data >> 8) & 1) != 1)
        errors++;
    data = 0;
    mst.write(addr, data);
    mst.read(addr, data);
    if (((data >> 8) & 1) != 1)
        errors++;
endtask

// test RO registers with read to clear
task test_read_clr;
    $display("%t, Start read to clear tests!", $time);
    // test STATUS register
    addr = 'h40;
    // hardware control and several reads to validate read to clear action (also check that write has no action)
    mst.read(addr, data);
    if (((data >> 16) & 'hFFF) != 0)
        errors++;
    @(posedge clk);
    csr_status_cap_in = 'habc;
    csr_status_cap_upd = 1'b1;
    @(posedge clk);
    csr_status_cap_upd = 1'b0;
    data = 'hffffffff;
    mst.write(addr, data);
    mst.read(addr, data);
    if (((data >> 16) & 'hFFF) != 'habc)
        errors++;
    mst.read(addr, data);
    if (((data >> 16) & 'hFFF) != 0)
        errors++;
endtask

// test RO registers with constants
task test_const;
    $display("%t, Start constatnts tests!", $time);
    // test VERSION register
    addr = 'h44;
    data = 'heeeeeeee;
    mst.write(addr, data);
    mst.read(addr, data);
    if (data != 'h00020010)
        errors++;
endtask

initial begin : main
    wait(!rst);
    repeat(5) @(posedge clk);

    test_basic();
    test_ext_upd();
    test_read_clr();
    test_const();

    repeat(5) @(posedge clk);
    if (errors)
        $display("!@# TEST FAILED - %d ERRORS #@!", errors);
    else
        $display("!@# TEST PASSED #@!");
    $finish;
end

initial begin : timeout
    #500us;
    $display("!@# TEST FAILED - TIMEOUT #@!");
    $finish;
end

endmodule

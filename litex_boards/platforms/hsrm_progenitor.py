#
#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Brendan Christy <brendan.christy@hs-rm.de>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50", 0,
        Subsignal("p", Pins("H4"), IOStandard("DIFF_SSTL15"), Misc("DIFF_TERM FALSE")),
        Subsignal("n", Pins("G4"), IOStandard("DIFF_SSTL15"), Misc("DIFF_TERM FALSE"))
    ),
#    ("clk125", 0,
#        Subsignal("p", Pins("F6"), IOStandard("DIFF_SSTL15")),
#        Subsignal("n", Pins("E6"), IOStandard("DIFF_SSTL15"))
#    ),
    #("cpu_reset", 0, Pins("T3"), IOStandard("SSTL15")),
    ("cpu_reset", 0, Pins("AA18"), IOStandard("LVCMOS33")),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins("J1 P6 N5 N3 G1 M3 N2 J5 L1 P2 L4 P5 K2 M1 M5"), IOStandard("SSTL15")),
        Subsignal("ba", Pins("P4 H5 H2"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("M6"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("M2"), IOStandard("SSTL15")),
        Subsignal("we_n", Pins("J2"), IOStandard("SSTL15")),
        Subsignal("dm", Pins("W2 Y7 V4 V5"), IOStandard("SSTL15")),
        Subsignal("dq", Pins("T1 U3 U2 U1 Y2 W1 Y1 V2 V7 W9 AB7 AA8 AB8 AB6 Y8 Y9 AB1 AB5 AB3 AA1 Y4 AA5 AB2 W4 T4 U6 T6 AA6 Y6 T5 U5 R6"), IOStandard("SSTL15")),
        Subsignal("dqs_p", Pins("R3 V9 Y3 W6"), IOStandard("DIFF_SSTL15")),
        Subsignal("dqs_n", Pins("R2 V8 AA3 W5"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_p", Pins("R1"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("P1"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke", Pins("L3"), IOStandard("SSTL15")),
        Subsignal("odt", Pins("K3"), IOStandard("SSTL15")),
        Subsignal("cs_n", Pins("K1"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("H3"), IOStandard("LVCMOS15")),
     
        Misc("SLEW=FAST"),
    ),

    # UART
    ("serial", 0,
        Subsignal("tx", Pins("B20")),
        Subsignal("rx", Pins("A20")),
        IOStandard("LVCMOS33"),
    ),

    # GMII Ethernet
    ("eth_clocks_ext", 0,
        Subsignal("tx", Pins("H18")),
        Subsignal("gtx", Pins("N20")),
        Subsignal("rx", Pins("K18")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("G20")),
        #Subsignal("int_n",   Pins("MISSING")),#TODO Ask about that pin to be added
        Subsignal("mdc",     Pins("L15")),
        Subsignal("mdio",    Pins("L14")),
        Subsignal("rx_dv",   Pins("L21")),
        Subsignal("rx_er",   Pins("K21")),
        Subsignal("rx_data", Pins("H19 J19 L20 L19 K19 J22 H22 H20")),
        Subsignal("tx_en",   Pins("M20")),
        Subsignal("tx_er",   Pins("M15")),
        Subsignal("tx_data", Pins("M13 L13 N22 M22 H17 K17 J17 M16")),
        Subsignal("col",  Pins("K22")),
        Subsignal("crs",  Pins("M21")),
        IOStandard("LVCMOS33")
    ),

    # SDCard
    ("sdcard", 0,
        Subsignal("data", Pins("AB13 AA13 Y13 AA14"), Misc("PULLUP True")),
        Subsignal("cmd",  Pins("Y14"),                Misc("PULLUP True")),
        Subsignal("clk",  Pins("Y12")),
        Subsignal("cd",   Pins("Y11")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33")
    ),
    # Buttons
    ("user_btn", 0, Pins("AB22"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("AA21"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("AA20"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("AB18"), IOStandard("LVCMOS33")),
    #("user_btn", 4, Pins("AA18"), IOStandard("LVCMOS33")),
    # Leds
    ("user_led",  0, Pins("V13"), IOStandard("LVCMOS33")),
    ("user_led",  1, Pins("R18"), IOStandard("LVCMOS33")),
    ("user_led",  2, Pins("T18"), IOStandard("LVCMOS33")),
    ("user_led",  3, Pins("V14"), IOStandard("LVCMOS33")),
    ("user_led",  4, Pins("P19"), IOStandard("LVCMOS33")),
    ("user_led",  5, Pins("T14"), IOStandard("LVCMOS33")),
    ("user_led",  6, Pins("R19"), IOStandard("LVCMOS33")),
    ("user_led",  7, Pins("T15"), IOStandard("LVCMOS33")),
    ("user_led",  8, Pins("V10"), IOStandard("LVCMOS33")),
    ("user_led",  9, Pins("T16"), IOStandard("LVCMOS33")),
    ("user_led", 10, Pins("W10"), IOStandard("LVCMOS33")),
    ("user_led", 11, Pins("U16"), IOStandard("LVCMOS33")),
    
]


_connectors = []


class Platform(XilinxPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self) -> None:
        XilinxPlatform.__init__(self, "xc7a200t-fbg484-1", _io, _connectors, toolchain="vivado")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 34]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 35]")

    def create_programmer(self):
        return OpenOCD("openocd_ax7101.cfg", "bscan_spi_xc7a200t.bit")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50",        loose=True), 1e9/50e6)        
        self.add_period_constraint(self.lookup_request("eth_clocks:gtx", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:tx", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks:rx", loose=True), 1e9/125e6)


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
    ("clk200", 0,
        Subsignal("p", Pins("R4"), IOStandard("DIFF_SSTL15")),
        Subsignal("n", Pins("T4"), IOStandard("DIFF_SSTL15"))
    ),
    ("clk125", 0,
        Subsignal("p", Pins("F6"), IOStandard("DIFF_SSTL15")),
        Subsignal("n", Pins("E6"), IOStandard("DIFF_SSTL15"))
    ),
    ("cpu_reset", 0, Pins("T6"), IOStandard("SSTL15")),

    # DDR3 SDRAM
    ("ddram", 0,
        Subsignal("a", Pins("AA4 AB2 AA5 AB5 AB1 U3 W1 T1 V2 U2 Y1 W2 Y2 U1 V3"), IOStandard("SSTL15")),
        Subsignal("ba", Pins("AA3 Y3 Y4"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("V4"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("W4"), IOStandard("SSTL15")),
        Subsignal("we_n", Pins("AA1"), IOStandard("SSTL15")),
        Subsignal("dm", Pins("D2 G2 M2 M5"), IOStandard("SSTL15")),
        Subsignal("dq", Pins("C2 G1 A1 F3 B2 F1 B1 E2 H3 G3 H2 H5 J1 J5 K1 H4 L4 M3 L3 J6 K3 K6 J4 L5 P1 N4 R1 N2 M6 N5 P6 P2"), IOStandard("SSTL15"), Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("dqs_p", Pins("E1 K2 M1 P5"), IOStandard("DIFF_SSTL15"), Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("dqs_n", Pins("D1 J2 L1 P4"), IOStandard("DIFF_SSTL15"), Misc("IN_TERM=UNTUNED_SPLIT_50")),
        Subsignal("clk_p", Pins("R3"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("R2"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke", Pins("T5"), IOStandard("SSTL15")),
        Subsignal("odt", Pins("U5"), IOStandard("SSTL15")),
        Subsignal("cs_n", Pins("AB3"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("W6"), IOStandard("LVCMOS15")),
        Misc("SLEW=FAST"),
    ),

    # UART
    ("serial", 0,
        Subsignal("tx", Pins("AB15")),
        Subsignal("rx", Pins("AA15")),
        IOStandard("LVCMOS33"),
    ),

    # GMII Ethernet
    ("eth_clocks_ext", 0,
        Subsignal("tx", Pins("K21")),
        Subsignal("gtx", Pins("G21")),
        Subsignal("rx", Pins("K18")),
        IOStandard("LVCMOS33")
    ),
    ("eth1_clocks_ext", 0,
        Subsignal("tx", Pins("T14")),
        Subsignal("gtx", Pins("M16")),
        Subsignal("rx", Pins("J20")),
        IOStandard("LVCMOS33")
    ),
    ("eth2_clocks_ext", 0,
        Subsignal("tx", Pins("V10")),
        Subsignal("gtx", Pins("AA21")),
        Subsignal("rx", Pins("V13")),
        IOStandard("LVCMOS33")
    ),
    ("eth3_clocks_ext", 0,
        Subsignal("tx", Pins("U16")),
        Subsignal("gtx", Pins("P20")),
        Subsignal("rx", Pins("Y18")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("G20")),
        Subsignal("int_n",   Pins("D14"), Misc("KEEPER = TRUE")),
        Subsignal("mdio",    Pins("L16")),
        Subsignal("mdc",     Pins("J17")),
        Subsignal("rx_dv",   Pins("M22")),
        Subsignal("rx_er",   Pins("N18")),
        Subsignal("rx_data", Pins("N22 H18 H17 M21 L21 N20 M20 N19")),
        Subsignal("tx_en",   Pins("G22")),
        Subsignal("tx_er",   Pins("K17")),
        Subsignal("tx_data", Pins("D22 H20 H22 J22 K22 L19 K19 L20")),
        Subsignal("col",  Pins("M18")),
        Subsignal("crs",  Pins("L18")), 
        IOStandard("LVCMOS33")
    ),
    ("eth", 1,
        Subsignal("rst_n",   Pins("L14")),
        Subsignal("int_n",   Pins("E14"), Misc("KEEPER = TRUE")),
        Subsignal("mdc",     Pins("AB21")),
        Subsignal("mdio",    Pins("AB22")),
        Subsignal("rx_dv",   Pins("L13")),
        Subsignal("rx_er",   Pins("G13")),
        Subsignal("rx_data", Pins("M13 K14 K13 J14 H14 H15 J15 H13")),
        Subsignal("tx_en",   Pins("M15")),
        Subsignal("tx_er",   Pins("T15")),
        Subsignal("tx_data", Pins("L15 K16 W15 W16 V17 W17 U15 V15")),
        Subsignal("col",  Pins("J21")),
        Subsignal("crs",  Pins("E22")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 2,
        Subsignal("rst_n",   Pins("T20")),
        Subsignal("int_n",   Pins("E13"), Misc("KEEPER = TRUE")),
        Subsignal("mdc",     Pins("V20")),
        Subsignal("mdio",    Pins("V19")),
        Subsignal("rx_dv",   Pins("AA20")),
        Subsignal("rx_er",   Pins("U21")),
        Subsignal("rx_data", Pins("AB20 AA19 AA18 AB18 Y17 W22 W21 T21")),
        Subsignal("tx_en",   Pins("V14")),
        Subsignal("tx_er",   Pins("AA9")),
        Subsignal("tx_data", Pins("W11 W12 Y11 Y12 W10 AA11 AA10 AB10")),
        Subsignal("col",  Pins("Y21")),
        Subsignal("crs",  Pins("Y22")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 3,
        Subsignal("rst_n",   Pins("R16")),
        Subsignal("int_n",   Pins("F13")),
        Subsignal("mdc",     Pins("V18")),
        Subsignal("mdio",    Pins("U20")),
        Subsignal("rx_dv",   Pins("W20")),
        Subsignal("rx_er",   Pins("N13")),
        Subsignal("rx_data", Pins("W19 Y19 V22 U22 T18 R18 R14 P14")),
        Subsignal("tx_en",   Pins("P16")),
        Subsignal("tx_er",   Pins("R19")),
        Subsignal("tx_data", Pins("R17 P15 N17 P17 T16 U17 U18 P19")),
        Subsignal("col",  Pins("N14")),
        Subsignal("crs",  Pins("N15")),
        IOStandard("LVCMOS33")
    ),
    ("spisdcard", 0,
            Subsignal("clk", Pins("J16")),
            Subsignal("mosi", Pins("A20"), Misc("PULLUP true")),
            Subsignal("cs_n", Pins("B22"), Misc("PULLUP true")),
            Subsignal("miso", Pins("F20"), Misc("PULLUP true")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS33"),
        ),
        ("sdcard", 0,
            Subsignal("data", Pins("F20 C22 B20 B22"), Misc("PULLUP true")),
            Subsignal("cmd", Pins("A20"), Misc("PULLUP true")),
            Subsignal("clk", Pins("J16")),
            Subsignal("cd", Pins("F19")),
            Misc("SLEW=FAST"),
            IOStandard("LVCMOS33"),
        )
    
]


_connectors = []


class Platform(XilinxPlatform):
    default_clk_name   = "clk200"
    default_clk_period = 1e9/200e6

    def __init__(self) -> None:
        XilinxPlatform.__init__(self, "xc7a100t-fgg484-2", _io, _connectors, toolchain="vivado")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 34]")
        self.add_platform_command("set_property INTERNAL_VREF 0.750 [get_iobanks 35]")


    def create_programmer(self):
        return OpenOCD("openocd_ax7101.cfg", "bscan_spi_xc7a100t.bit")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk200",        loose=True), 1e9/200e6)
        
        self.add_period_constraint(self.lookup_request("eth_clocks_ext:gtx", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks_ext:tx", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth_clocks_ext:rx", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth1_clocks_ext:gtx", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth1_clocks_ext:tx", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth1_clocks_ext:rx", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth2_clocks_ext:gtx", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth2_clocks_ext:tx", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth2_clocks_ext:rx", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth3_clocks_ext:gtx", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth3_clocks_ext:tx", loose=True), 1e9/125e6)
        self.add_period_constraint(self.lookup_request("eth3_clocks_ext:rx", loose=True), 1e9/125e6)

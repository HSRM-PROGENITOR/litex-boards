#!/usr/bin/env python3

import os
import argparse
from migen import *

from litex_boards.platforms import hsrm_progenitor

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litedram.modules import IS43TR16256B
from litedram.phy import s7ddrphy
from litex.soc.cores.led import LedChaser

from liteeth.phy import LiteEthPHYGMII

from litex.build.generic_platform import Subsignal, Pins
from litesata.phy import LiteSATAPHY

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_idelay    = ClockDomain()

        self.submodules.pll = pll = S7MMCM(speedgrade=-2)
        self.comb += pll.reset.eq(~platform.request("cpu_reset") | self.rst)
        pll.register_clkin(platform.request("clk50"), 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,  4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay, 200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)


class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), **kwargs):
        platform = hsrm_progenitor.Platform()

        # SoCCore ---------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, 
                         ident = "LiteX SoC on the",
                         ident_version = True,
                         **kwargs)

        # CRG -------------------------------------------------------------
        eth0_clock = platform.request("eth0_clocks_ext", 0)
        eth1_clock = platform.request("eth1_clocks_ext", 0)
        eth2_clock = platform.request("eth2_clocks_ext", 0)
        eth3_clock = platform.request("eth3_clocks_ext", 0)

        self.submodules.crg = _CRG(platform, sys_clk_freq) 

        # DDR3 SDRAM ------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype = "DDR3",
                nphases  = 4,
                sys_clk_freq = sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = IS43TR16256B(sys_clk_freq, "1:4"),
                l2_cache_size = kwargs.get("l2_size", 8192)
            )
        
        # Ethernet -------------------------------------------------------
        self.submodules.ethphy = LiteEthPHYGMII(
                clock_pads = eth0_clock,
                pads       = self.platform.request("eth", 0)
                )
        self.add_csr("ethphy")
        self.add_ethernet(name="ethmac", phy=self.ethphy, phy_cd="ethphy_eth")

        self.submodules.ethphy1 = LiteEthPHYGMII(
                clock_pads = eth1_clock,
                pads       = self.platform.request("eth", 1)
                )
        self.add_csr("ethphy1")
        self.add_ethernet(name="ethmac1", phy=self.ethphy1, phy_cd="ethphy1_eth")
        
        self.submodules.ethphy2 = LiteEthPHYGMII(
                clock_pads = eth2_clock,
                pads       = self.platform.request("eth", 2)
                )
        self.add_csr("ethphy2")
        self.add_ethernet(name="ethmac2", phy=self.ethphy2, phy_cd="ethphy2_eth")

        self.submodules.ethphy3 = LiteEthPHYGMII(
                clock_pads = eth3_clock,
                pads       = self.platform.request("eth", 3)
                )
        self.add_csr("ethphy3")
        self.add_ethernet(name="ethmac3", phy=self.ethphy3, phy_cd="ethphy3_eth")

        # SATA -----------------------------------------------------------
        _sata_io = [
             # PCIe 2 SATA Custom Adapter (With PCIe Riser / SATA cable mod).
            ("pcie2sata", 0,
                Subsignal("tx_p",  Pins("B6")),
                Subsignal("tx_n",  Pins("A6")),
                Subsignal("rx_p",  Pins("B10")),
                Subsignal("rx_n",  Pins("A10")),
            ),
        ]
        platform.add_extension(_sata_io)

        # RefClk, Generate 150MHz from PLL.
        self.clock_domains.cd_sata_refclk = ClockDomain()
        self.crg.pll.create_clkout(self.cd_sata_refclk, 150e6)
        sata_refclk = ClockSignal("sata_refclk")
        platform.add_platform_command("set_property SEVERITY {{Warning}} [get_drc_checks REQP-49]")

        # PHY
        self.submodules.sata_phy = LiteSATAPHY(platform.device,
            refclk     = sata_refclk,
            pads       = platform.request("pcie2sata"),
            gen        = "gen1",
            clk_freq   = sys_clk_freq,
            data_width = 16)

        # Core
        self.add_sata(phy=self.sata_phy, mode="read+write")

        # PCIE -----------------------------------------------------------
        #self.submodules.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x1"),
        #    data_width = 64,
        #    bar0_size  = 0x20000)
        #self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Leds -------------------------------------------------------------------------------------
        #self.submodules.leds = LedChaser(
        #    pads         = platform.request_all("user_led"),
        #    sys_clk_freq = sys_clk_freq)

        self.add_sdcard()
        

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on HSRM Progenitor")
    parser.add_argument("--build", action="store_true", help="Build Bitstream")
    parser.add_argument("--load", action="store_true", help="Load Bitstream")
    parser.add_argument("--sys-clk-freq", default=100e6, help="System clock frequency (default: 100MHz)")
    
    sdopts = parser.add_mutually_exclusive_group()
    sdopts.add_argument("--with-sdcard", action="store_true", help="Enable SDCard support")
    
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq=int(float(args.sys_clk_freq)),
        **soc_core_argdict(args)
    )

    if args.with_sdcard:
        soc.add_sdcard()

    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()

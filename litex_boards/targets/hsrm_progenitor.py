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
from liteeth.phy.rmii import LiteEthPHYRMII

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
    def __init__(self, sys_clk_freq=int(100e6), **kwargs):
        platform = hsrm_progenitor.Platform()

        # SoCCore ---------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, 
                         ident = "LiteX SoC on the",
                         ident_version = True,
                         **kwargs)

        # CRG -------------------------------------------------------------
        #eth0_clock = platform.request("eth_clocks", 0)
        #eth1_clock = platform.request("eth1_clocks_ext", 0)
        #eth2_clock = platform.request("eth2_clocks_ext", 0)
        #eth3_clock = platform.request("eth3_clocks_ext", 0)
        #eth4_clock = platform.request("eth4_clocks_ext", 0)

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
        # WARNING: Use LiteEthPHYRMII as Phy for the module itself (100MBit!)
        #self.submodules.ethphy = LiteEthPHYGMII(
        #        clock_pads = eth0_clock,
        #        pads       = self.platform.request("eth", 0)
        #        )
        #self.add_csr("ethphy")
        #self.add_ethernet(name="ethmac", phy=self.ethphy, phy_cd="ethphy_eth")

        from liteeth.phy import LiteEthPHYGMIIMII
        self.submodules.ethphy = LiteEthPHYGMIIMII(
            clock_pads = self.platform.request("eth_clocks", eth_phy),
            pads       = self.platform.request("eth", eth_phy),
            clk_freq   = int(self.sys_clk_freq))
        self.add_ethernet(phy=self.ethphy)
        self.ethphy.crg.cd_eth_rx.clk.attr.add("keep")
        self.ethphy.crg.cd_eth_tx.clk.attr.add("keep")
        self.platform.add_platform_command("""
        NET "{eth_clocks_rx}" CLOCK_DEDICATED_ROUTE = FALSE;
        NET "{eth_clocks_tx}" CLOCK_DEDICATED_ROUTE = FALSE;
        """,
        eth_clocks_rx=platform.lookup_request("eth_clocks").rx,
        eth_clocks_tx=platform.lookup_request("eth_clocks").tx,
        )

#        self.submodules.ethphy1 = LiteEthPHYGMII(
#                clock_pads = eth1_clock,
#                pads       = self.platform.request("eth", 1)
#                )
#        self.add_csr("ethphy1")
#        self.add_ethernet(name="ethmac1", phy=self.ethphy1, phy_cd="ethphy1_eth")
#        
#        self.submodules.ethphy2 = LiteEthPHYGMII(
#                clock_pads = eth2_clock,
#                pads       = self.platform.request("eth", 2)
#                )
#        self.add_csr("ethphy2")
#        self.add_ethernet(name="ethmac2", phy=self.ethphy2, phy_cd="ethphy2_eth")

        #self.submodules.ethphy3 = LiteEthPHYGMII(
        #        clock_pads = eth3_clock,
        #        pads       = self.platform.request("eth", 3)
        #        )
        #self.add_csr("ethphy3")
        #self.add_ethernet(name="ethmac3", phy=self.ethphy3, phy_cd="ethphy3_eth")
        #self.submodules.ethphy4 = LiteEthPHYRMII(
        #        clock_pads = eth4_clock,
        #        pads       = self.platform.request("eth", 4)
        #        )
        #self.add_csr("ethphy4")
        #self.add_ethernet(name="ethmac4", phy=self.ethphy4, phy_cd="ethphy4_eth")


        # Leds -------------------------------------------------------------------------------------
        #self.submodules.leds = LedChaser(
        #    pads         = platform.request_all("user_led"),
        #    sys_clk_freq = sys_clk_freq)
            

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

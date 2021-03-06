#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Created with Corsair vgit-latest

Control/status register map.
"""

__VERSION__ = '1.0'


class _RegLedctrl:
    def __init__(self, rmap):
        self._rmap = rmap

    @property
    def ren(self):
        """Enable red led"""
        rdata = self._rmap._if.read(self._rmap.LEDCTRL_ADDR)
        return (rdata >> self._rmap.LEDCTRL_REN_POS) & self._rmap.LEDCTRL_REN_MSK

    @ren.setter
    def ren(self, val):
        rdata = self._rmap._if.read(self._rmap.LEDCTRL_ADDR)
        rdata = rdata & (~(self._rmap.LEDCTRL_REN_MSK << self._rmap.LEDCTRL_REN_POS))
        rdata = rdata | (val << self._rmap.LEDCTRL_REN_POS)
        self._rmap._if.write(self._rmap.LEDCTRL_ADDR, rdata)

    @property
    def gen(self):
        """Enable green led"""
        rdata = self._rmap._if.read(self._rmap.LEDCTRL_ADDR)
        return (rdata >> self._rmap.LEDCTRL_GEN_POS) & self._rmap.LEDCTRL_GEN_MSK

    @gen.setter
    def gen(self, val):
        rdata = self._rmap._if.read(self._rmap.LEDCTRL_ADDR)
        rdata = rdata & (~(self._rmap.LEDCTRL_GEN_MSK << self._rmap.LEDCTRL_GEN_POS))
        rdata = rdata | (val << self._rmap.LEDCTRL_GEN_POS)
        self._rmap._if.write(self._rmap.LEDCTRL_ADDR, rdata)

    @property
    def ben(self):
        """Enable blue led"""
        rdata = self._rmap._if.read(self._rmap.LEDCTRL_ADDR)
        return (rdata >> self._rmap.LEDCTRL_BEN_POS) & self._rmap.LEDCTRL_BEN_MSK

    @ben.setter
    def ben(self, val):
        rdata = self._rmap._if.read(self._rmap.LEDCTRL_ADDR)
        rdata = rdata & (~(self._rmap.LEDCTRL_BEN_MSK << self._rmap.LEDCTRL_BEN_POS))
        rdata = rdata | (val << self._rmap.LEDCTRL_BEN_POS)
        self._rmap._if.write(self._rmap.LEDCTRL_ADDR, rdata)


class RegMap:
    """Control/Status register map"""

    # LEDCTRL - LED control register
    LEDCTRL_ADDR = 0x00
    LEDCTRL_REN_POS = 0
    LEDCTRL_REN_MSK = 0x1
    LEDCTRL_GEN_POS = 4
    LEDCTRL_GEN_MSK = 0x1
    LEDCTRL_BEN_POS = 8
    LEDCTRL_BEN_MSK = 0x1

    def __init__(self, interface):
        self._if = interface

    @property
    def ledctrl(self):
        """LED control register"""
        return self._if.read(self.LEDCTRL_ADDR)

    @ledctrl.setter
    def ledctrl(self, val):
        self._if.write(self.LEDCTRL_ADDR, val)

    @property
    def ledctrl_bf(self):
        return _RegLedctrl(self)

#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

Implements
==========

xpl-stat { hop=1 source=bnz-rfxcomrx.vesta target=* } hbeat.app { interval=5 port=44250 remote-ip=192.168.0.39 }


@author: domos  (domos p vesta at gmail p com)
@copyright: (C) 2007-2015 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

from domogik.xpl.common.xplmessage import XplMessage
from domogik.xpl.common.xplconnector import Listener
from domogik.xpl.common.plugin import XplPlugin
import time
import threading


class RfxBnzManager(XplPlugin):
    """
    """

    def __init__(self):
        """ Init plugin
        """
        XplPlugin.__init__(self, name='rfxbnz')

        # check if the plugin is configured. If not, this will stop the plugin and log an error
        if not self.check_configured():
            return

        # Configuration
        host = self.get_config("host")                         # host where rfxcomrx run
        if host is None:
            self.log.error('### Host is not configured, exiting')
            self.force_leave()
            return

        self.lastTimestampHbeat = time.time()

        # Create listeners
        self.log.info("==>  Creating listener for rfxbnz")
        Listener(self.rfxbnz_stat_cb, self.myxpl, {'xplsource': 'bnz-rfxcomrx.' + host, 'xpltype': 'xpl-stat', 'schema': 'hbeat.app'})

        self.log.info("==> Launch thread to rfxbnz_chk_hbeat")
        threads = {}
        thr_name = "rfxbnz_chk"
        threads[thr_name] = threading.Thread(None,
                                            self.rfxbnz_chk_hbeat,
                                            thr_name,
                                            (self.log,
                                                self.get_stop()),
                                            {})
        threads[thr_name].start()
        self.register_thread(threads[thr_name])

        self.ready()


    def rfxbnz_stat_cb(self, message):
        """
        Callback heartbeat rfxcomrx messages
        """
        self.log.debug("==> Call rfxbnz_stat_cb")
        self.lastTimestampHbeat = time.time()                      # time.time() -> 1324305354.0857329


    def rfxbnz_chk_hbeat(self, log, stop):
        """
        Check if heartbeat to old
        """
        self.log.debug("==> Call rfxbnz_chk_hbeat thread")
        while not self._stop.isSet():
            self.log.debug("==> Check if hbeat.app of 'rfxcomrx' process is too old ...")
            if time.time() - self.lastTimestampHbeat > 630:
                self.log.error('### rfxcomrx.pl not alive, exiting')
                self.force_leave()
            time.sleep(120)


if __name__ == "__main__":
    RfxBnzManager()

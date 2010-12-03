#!/usr/bin/env python
# -*- coding: utf-8

# Copyright (C) 2010 Stefan Hacker <dd0t@users.sourceforge.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Neither the name of the Mumble Developers nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# `AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest
import Queue
from mumo_manager import MumoManager, MumoManagerRemote
from mumo_module import MumoModule
import logging
from threading import Event


class MumoManagerTest(unittest.TestCase):
    def setUp(self):
        class MyModule(MumoModule):
            def __init__(self, name, manager, configuration = None):
                MumoModule.__init__(self, name, manager, configuration)
                
                self.estarted = Event()
                self.estopped = Event()
                self.econnected = Event()
                self.edisconnected = Event()
            
            def onStart(self):
                self.estarted.set()
            
            def onStop(self):
                self.estopped.set()
            
            def connected(self):
                self.econnected.set()
            
            def disconnected(self):
                self.edisconnected.set()
        
        self.mymod = MyModule

        class conf(object):
            pass # Dummy class
        
        self.cfg = conf()
        self.cfg.test = 10

    #
    #--- Helpers for independent test env creation
    #
    def up(self):
        man = MumoManager()
        man.start()

        mod = man.loadModuleCls("MyModule", self.mymod, self.cfg)
        man.startModules()
        
        return (man, mod)
    
    def down(self, man, mod):
        man.stopModules()
        man.stop()
        man.join(timeout=1)
    
    #
    #--- Tests
    #
    def testModuleStarted(self):
        man, mod = self.up()
        
        mod.estarted.wait(timeout=1)
        assert(mod.estarted.is_set())
        
        self.down(man, mod)
    
    def testModuleStopStart(self):
        man ,mod = self.up()
        
        tos = ["MyModule"]
        self.assertEquals(list(man.stopModules(tos).iterkeys()), tos)
        mod.estopped.wait(timeout=1)
        assert(mod.estopped.is_set())
        
        self.down(man, mod)

    def tearDown(self):
        pass
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
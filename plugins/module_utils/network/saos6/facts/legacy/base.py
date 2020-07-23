# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The SAOS 6 Legacy fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type
import platform
import re
from ansible_collections.ciena.saos6.plugins.module_utils.network.saos6.saos6 import (
    run_commands,
    get_capabilities,
)
from ansible_collections.ciena.saos6.plugins.module_utils.network.saos6.utils.utils import (
    parse_cli_textfsm,
)


class FactsBase(object):

    COMMANDS = frozenset()

    def __init__(self, module):
        self.module = module
        self.facts = dict()
        self.warnings = list()
        self.responses = None

    def populate(self):
        self.responses = run_commands(
            self.module, commands=self.COMMANDS, check_rc=False
        )

    def run(self, cmd):
        return run_commands(self.module, commands=cmd, check_rc=False)


class Default(FactsBase):

    COMMANDS = ["chassis show device-id"]

    def populate(self):
        super(Default, self).populate()
        data = self.responses[0]
        self.facts["serialnum"] = self.parse_serialnum(data)
        self.facts.update(self.platform_facts())

    def parse_serialnum(self, data):
        match = re.search(r"\| Serial Number +\| +(\S+)", data)
        if match:
            return match.group(1)

    def platform_facts(self):
        platform_facts = {}

        resp = get_capabilities(self.module)
        device_info = resp["device_info"]

        platform_facts["system"] = device_info["network_os"]

        for item in ("model", "image", "version", "platform", "hostname"):
            val = device_info.get("network_os_%s" % item)
            if val:
                platform_facts[item] = val

        platform_facts["api"] = resp["network_api"]
        platform_facts["python_version"] = platform.python_version()

        return platform_facts


class Config(FactsBase):

    COMMANDS = ["conf show brief"]

    def populate(self):
        super(Config, self).populate()
        self.facts["config"] = self.responses[0]


class Interfaces(FactsBase):

    COMMANDS = ["port show"]

    def populate(self):
        super(Interfaces, self).populate()


class Neighbors(FactsBase):

    COMMANDS = ["lldp show configuration", "lldp show neighbors"]

    def populate(self):
        super(Neighbors, self).populate()

        fsm = """#
Value localPort (\S+)
Value remotePort (\S+)
Value chassisId (\S+)
Value mgmtAddr (\S+)
Value systemName (\S+)
Value systemDesc (.+)

Start
  ^\|Port +\|Port -> PortTable

PortTable
  ^\+[-]+ -> Entrypoint

Entrypoint
  ^\|${localPort} +\|${remotePort}.*Chassis Id\: ${chassisId}
  ^\| +\| +\| +Mgmt Addr\: ${mgmtAddr}
  ^\| +\| +\| +System Name\: ${systemName}
  ^\| +\| +\| +System Desc\: ${systemDesc}  +\|
  ^\+[-]+ -> Record
"""

        lldp_config = self.responses[0]
        if "Enable" in lldp_config:
            neighbors = parse_cli_textfsm(self.responses[1], fsm)
            self.facts["neighbors"] = neighbors

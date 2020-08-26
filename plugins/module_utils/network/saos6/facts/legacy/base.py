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

    COMMANDS = ["port show status"]

    def populate(self):
        super(Interfaces, self).populate()

        fsm = r"""#
Value port (\S+)
Value macAddress (\S+)
Value LinkStateAdmin (\S+)
Value LinkStateOper (\S+)
Value pvid (\S+)
Value mode (\S+)
Value speed (\S+)
Value duplex (\S+)
Value flow_ctrl (\S+)
Value auto_neg (\S+)
Value untagged_data_vid (\S+)
Value fixed_rcos (\S+)
Value fixed_rcolor (\S+)
Value acceptable_frame_type (\S+)
Value egress_untag_vlan (\S+)
Value max_frame_size (\S+)
Value untagged_data_vs (\S+)
Value untagged_ctrl_vs (\S+)
Value resolved_cos_policy (\S+)
Value ingress_to_egress_qmap (\S+)
Value resolved_cos_map (\S+)
Value frame_cos_map (\S+)

Start
  ^.*PORT ${port} INFO.*
  ^\| *MAC Address *\| ${macAddress}
  ^\| *Link State *\| *${LinkStateAdmin} *\| ${LinkStateOper} *\|
  ^\| *Mode   *\| ${mode}
  ^\| *Speed   *\| ${speed}
  ^\| *Duplex   *\| ${duplex}
  ^\| *Flow Control   *\| ${flow_ctrl}
  ^\| *Auto Negotiation   *\| ${auto_neg}
  ^\| *PVID *\| ${pvid}
  ^\| *Untag Ingress Data Vid *\| ${untagged_data_vid}
  ^\| *Fixed Resolved CoS *\| ${fixed_rcos}
  ^\| *Fixed Resolved Color *\| ${fixed_rcolor}
  ^\| *Acceptable Frame Type *\| ${acceptable_frame_type}
  ^\| *Egress Untag VLAN *\| ${egress_untag_vlan}
  ^\| *Max Frame Size *\| ${max_frame_size}
  ^\| *Untagged Data VS *\| ${untagged_data_vs}
  ^\| *Untagged Ctrl VS *\| ${untagged_ctrl_vs}
  ^\| *Resolved CoS Policy *\| ${resolved_cos_policy}
  ^\| *Ingress to Egress QMap *\| ${ingress_to_egress_qmap}
  ^\| *Ingress FCOS->RCOS Map *\| ${resolved_cos_map}
  ^\| *Egress RCOS->FCOS Map *\| ${frame_cos_map} -> Record

EOF
"""
        interfaces = []
        ports = re.findall(r"^\|(\S+)", self.responses[0], re.M)
        for port in ports:
            command = "port show port %s" % port
            port_response = self.run([command])
            interface = parse_cli_textfsm(port_response[0], fsm.encode('utf-8'))
            interfaces.append(interface[0])
        self.facts["interfaces"] = interfaces


class Neighbors(FactsBase):

    COMMANDS = ["lldp show configuration", "lldp show neighbors"]

    def populate(self):
        super(Neighbors, self).populate()

        fsm = r"""#
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
            neighbors = parse_cli_textfsm(self.responses[1], fsm.encode('utf-8'))
            self.facts["neighbors"] = neighbors

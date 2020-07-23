# (c) 2020 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
---
cliconf: saos6
short_description: Use saos6 cliconf to run command on Ciena saos6 platform
description:
  - This saos6 plugin provides low level abstraction apis for
    sending and receiving CLI commands from Ciena saos6 network devices.
"""

import re
import json

from itertools import chain

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils.common._collections_compat import Mapping
from ansible.module_utils._text import to_text
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list
from ansible.plugins.cliconf import CliconfBase


class Cliconf(CliconfBase):

    def get_device_info(self):
        device_info = {}
        device_info['network_os'] = 'ciena.saos6.saos6'
        reply = self.get('software show')
        data = to_text(reply, errors='surrogate_or_strict').strip()

        match = re.search(r'Running Package +\: (\S+)', data)
        if match:
            device_info['network_os_version'] = match.group(1).strip(',')

        reply = self.get('chassis show capabilities')
        data = to_text(reply, errors='surrogate_or_strict').strip()

        model_search = re.search(r'Platform Name + \| (\S+)', data)
        if model_search:
            device_info['network_os_model'] = model_search.group(1)

        return device_info

    def get_config(self, source='running', format='text', flags=None):
        cmd = 'conf sh brief'
        out = self.send_command(cmd)
        return out

    def edit_config(self, command):
        for cmd in chain(to_list(command)):
            self.send_command(cmd)

    def get_capabilities(self):
        result = super(Cliconf, self).get_capabilities()
        return json.dumps(result)

    def get(
        self,
        command=None,
        prompt=None,
        answer=None,
        sendonly=False,
        output=None,
        newline=True,
        check_all=False,
    ):
        if not command:
            raise ValueError("must provide value of command to execute")
        if output:
            raise ValueError(
                "'output' value %s is not supported for get" % output
            )

        return self.send_command(
            command=command,
            prompt=prompt,
            answer=answer,
            sendonly=sendonly,
            newline=newline,
            check_all=check_all,
        )

    def run_commands(self, commands=None, check_rc=True):
        if commands is None:
            raise ValueError("'commands' value is required")

        responses = list()
        for cmd in to_list(commands):
            if not isinstance(cmd, Mapping):
                cmd = {"command": cmd}

            output = cmd.pop("output", None)
            if output:
                raise ValueError(
                    "'output' value %s is not supported for run_commands"
                    % output
                )

            try:
                out = self.send_command(**cmd)
            except AnsibleConnectionFailure as e:
                if check_rc:
                    raise
                out = getattr(e, "err", e)

            responses.append(out)

        return responses

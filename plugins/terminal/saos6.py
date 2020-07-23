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

import re

from ansible.plugins.terminal import TerminalBase
from ansible.errors import AnsibleConnectionFailure
from ansible.utils.display import Display

display = Display()


class TerminalModule(TerminalBase):
    terminal_stdout_re = [
        re.compile(br"[\w\+\-\.:\/\[\]]+(?:\([^\)]+\)){0,3}[*]?> ")
    ]

    terminal_stderr_re = [
        re.compile(br"SHELL PARSER FAILURE"),
    ]

    terminal_inital_prompt_newline = False

    def on_open_shell(self):
        try:
            self._exec_cli_command(b"system shell session set more off")
        except AnsibleConnectionFailure:
            raise AnsibleConnectionFailure("unable to set terminal parameters")

        try:
            self._exec_cli_command(b"system shell session set window-width 512")
        except AnsibleConnectionFailure:
            display.display(
                "WARNING: Unable to set terminal width, command responses may be truncated"
            )

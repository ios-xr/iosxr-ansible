#!/usr/bin/python
#------------------------------------------------------------------------------
#
#    Copyright (C) 2016 Cisco Systems, Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#------------------------------------------------------------------------------

from ansible.module_utils.basic import *
from ansible.module_utils.shell import *
from ansible.module_utils.netcfg import *
from iosxr_common import *
from iosxr import *

DOCUMENTATION = """
---
module: iosxr_cli
author: Adisorn Ermongkonchai
short_description: Run a command on IOS-XR devices.
description:
  - Run an IOS-XR CLI command
options:
  host:
    description:
      - IP address or hostname (resolvable by Ansible control host) of
        the target IOS-XR node.
    required: true
  username:
    description:
      - username used to login to IOS-XR
    required: false
    default: none
  password:
    description:
      - password used to login to IOS-XR
    required: false
    default: none
  command:
    description:
      - IOS-XR CLI command string
    required: true
"""

EXAMPLES = """
- iosxr_cli:
    host: '{{ ansible_ssh_host }}'
    username: cisco
    password: cisco
    command: 'show version'
"""

RETURN = """
stdout:
  description: raw response
  returned: always
stdout_lines:
  description: list of response lines
  returned: always
"""

def main():
    module = get_module(
        argument_spec = dict(
            username = dict(required=False, default=None),
            password = dict(required=False, default=None),
            command = dict(required=True)
        ),
        supports_check_mode = False
    )
    args = module.params
    command = args['command']

    result = dict(changed=False)
    result['stdout'] = execute_command(module, command)
    result['stdout_lines'] = str(result['stdout']).split(r'\n')
    return module.exit_json(**result)

if __name__ == "__main__":
    main()

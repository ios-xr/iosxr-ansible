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
module: iosxr_install_key
author: Adisorn Ermongkonchai
short_description: Install BASE64 crypto key on IOS-XR device
description:
  - Install BASE64 crypto key on IOS-XR device
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
  keyfile:
    description:
      - fully qualified base64 key file, e.g. tftp://192.168.1.1/id_rsa_pub.b64
    note:
      - following commands show how to convert Linux rsa key file to base64 file
        $cut -d" " -f2 ~/.ssh/id_rsa.pub | base64 -d > ~/.ssh/id_rsa_pub.b64
    required: true
"""

EXAMPLES = """
- iosxr_install_config:
    host: '{{ ansible_ssh_host }}'
    username: cisco
    password: cisco
    keyfile: 'tftp://192.168.1.1/id_rsa_pub.b64'

"""

RETURN = """
stdout:
  description: raw response
  returned: always
stdout_lines:
  description: list of response lines
  returned: always
"""

CLI_PROMPTS_RE.append(re.compile(r'[\r\n]?[>|#|%|:](?:\s*)$'))

def main():
    module = get_module(
        argument_spec = dict(
            username = dict(required=False, default=None),
            password = dict(required=False, default=None),
            keyfile  = dict(required=True),
        ),
        supports_check_mode = False
    )
    args = module.params
    keyfile = args['keyfile']
  
    show_command = 'show crypto key authentication rsa'
    response = execute_command(module, show_command)

    commands = ['crypto key import authentication rsa ' + keyfile]
    if 'authentication' in response[0]:
        commands.append('yes')
    response = execute_command(module, commands)

    show_command = 'show crypto key authentication rsa'
    response = execute_command(module, show_command)

    result = dict(changed=True)
    result['stdout'] = response
    result['stdout_lines'] = str(result['stdout']).split(r'\n')

    module.exit_json(**result)

if __name__ == "__main__":
  main()

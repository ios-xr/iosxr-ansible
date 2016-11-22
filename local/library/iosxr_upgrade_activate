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
module: iosxr_upgrade_activate
author: Adisorn Ermongkonchai
short_description: Activate packages in IOS-XR repository.
description:
  - Activate IOS-XR packages in IOS-XR repository.
options:
  host:
    description:
      - IP address or hostname (resolvable by Ansible control host) of
        the target IOS-XR node.
    required: true
  username:
    description:
      - username used to login to IOS-XR
    required: true
    default: none
  password:
    description:
      - password used to login to IOS-XR
    required: true
    default: none
  pkgname:
    description:
      - IOS-XR software packages in the repository
        NOTE: use 'show install inactive' to see packages in repository
    required: true
"""

EXAMPLES = """
- iosxr_upgrade_activate:
    host: '{{ ansible_ssh_host }}'
    username: cisco
    pkgname: 'xrv9k-mgbl-3.0.0.0-r60204I xrv9k-k9sec-2.0.0.0-r60204I'
"""

RETURN = """
stdout:
  description: raw response
  returned: always
stdout_lines:
  description: list of response lines
  returned: always
"""

# check if another install command in progress
def is_legacy_iosxr(module):
    command = "show version"
    response = execute_command(module, command)
    return "Build Information:" not in response[0]

# check if another install command in progress
def is_install_in_progress(module):
    command = "show install request"
    response = execute_command(module, command)
    return "No install operation in progress" not in response[0]

CLI_PROMPTS_RE.append(re.compile(r'[\r\n]?\[yes\/no]:\[\w+]\s'))

def main():
    module = get_module(
        argument_spec = dict(
            username = dict(required=False, default=None),
            password = dict(required=False, default=None),
            pkgname = dict(required=True, default=None),
        ),
        supports_check_mode = False
    )
    args = module.params
    pkg_name = args['pkgname']

    # cannot run on classic XR
    if is_legacy_iosxr(module):
        module.fail_json(msg='this upgrade module cannot run on 32-bit IOS-XR')

    # make sure no other install in progress
    if is_install_in_progress(module):
        module.fail_json(msg='other install operation in progress')

    # ignore timeout
    module.connection.shell.shell.settimeout(None)

    # run install activate command
    commands = [ 'install activate ' + pkg_name ]
    commands.append('yes\n')

    response = execute_command(module, commands)
    while True:
        try:
            if not is_install_in_progress(module):
                break
        except:
            break

    result = dict(changed=True)
    result['stdout'] = response
    result['stdout_lines'] = str(result['stdout']).split(r'\n')

    module.exit_json(**result)

if __name__ == "__main__":
    main()

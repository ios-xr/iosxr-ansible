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
module: iosxr_reload
author: Adisorn Ermongkonchai
short_description: Reload IOS-XR device
description:
  - Restart specified IOS-XR device
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
  confirm:
    description:
      - make sure user really want to reload
    required: true
    value: "yes" or other string
  location:
    description:
      - location of the node that needs to be reboot
        e.g. 0/RP0/CPU0
    required: false
    default: None
  force:
    description:
      - force reaload without doing any cleanup
    required: false
    default: false

"""

EXAMPLES = """
- iosxr_reload:
    host: '{{ ansible_ssh_host }}'
    username: cisco
    password: cisco
    confirm: yes
"""

RETURN = """
stdout:
  description: raw response
  returned: always
stdout_lines:
  description: list of response lines
  returned: always
"""

CLI_PROMPTS_RE.append(re.compile(r'[\r\n]?[a-zA-Z]{1}[a-zA-Z0-9-]*[confirm]]'))

def main():
    module = get_module(
        argument_spec = dict(
            username = dict(required=False, default=None),
            password = dict(required=False, default=None),
            confirm  = dict(required=True),
            location = dict(required=False, default=None),
            force    = dict(required=False, type='bool', default=False)
        ),
        supports_check_mode = False
    )
    args = module.params
    force = args['force']
    location = args['location']

    result = dict(changed=False)
    if args['confirm'] != 'yes':
        result['stdout'] = "reload aborted"
        module.exit_json(**result)
  
    reload_command = 'reload '
    if location != None:
        reload_command = reload_command + 'location %s ' % location
    if force is True:
        reload_command = reload_command + 'force '
    commands = [reload_command]
    commands.append('\r')
    commands.append('\r')
    response = execute_command(module, commands)
  
    result['stdout'] = response
    result['stdout_lines'] = str(result['stdout']).split(r'\n')
    module.exit_json(**result)

if __name__ == "__main__":
  main()

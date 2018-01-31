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
module: iosxr_clear_config
author: Adisorn Ermongkonchai
short_description: Clear all configurations on IOS-XR device
description:
  - Clear all configurations on IOS-XR device
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
  confirm:
    description:
      - make sure user really want to reload
    required: true
    value: "yes" or other string
"""

EXAMPLES = """
- iosxr_clear_config:
    host: '{{ ansible_ssh_host }}'
    username: {{ ansible_ssh_user }}
    password: {{ ansible_ssh_pass }}
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

CLI_PROMPTS_RE.append(re.compile(r'[\r\n]?[>|#|%|:](?:\s*)$'))

def main():
    module = get_module(
        argument_spec = dict(
            username = dict(required=False, default=None),
            password = dict(required=False, default=None),
            confirm  = dict(required=True),
        ),
        supports_check_mode = False
    )
    result = dict(changed=False)
    if module.params['confirm'] != 'yes':
        result['stdout'] = "clear configs aborted"
        module.exit_json(**result)

    commands = ['commit replace']
    commands.insert(0, 'configure terminal')
    commands.append('yes')
    try:
        module.execute(commands)
    except:
        pass
  
    result = dict(changed=False)
    result['stdout'] = 'all configs cleared'
    result['stdout_lines'] = str(result['stdout']).split(r'\n')
    return module.exit_json(**result)

if __name__ == "__main__":
    main()

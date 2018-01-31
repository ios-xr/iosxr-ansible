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
module: iosxr_rollback
author: Adisorn Ermongkonchai
short_description: Rollback configuration on IOS-XR device
description:
  - Rollback IOS-XR configuration
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
  password:
    description:
      - password used to login to IOS-XR
    required: true
  rollback_id:
    description:
      - rollback configuration committted to particular id
        e.g. 1000000012
    required: false
    default: None
  to_rollback_id:
    description:
      - rollback up to (and including) a specific commit
        e.g. 1000000012
    required: false
    default: None
  to_exclude_rollback_id:
    description:
      - rollback up to (and excluding) a specific commit
        e.g. 1000000012
    required: false
    default: None
  last_n_committed:
    description:
      - rollback configuration last N committted made
        e.g. 5
    required: false
    default: None
  label:
    description:
      - assign a label to this commit
    required: false
  force:
    description:
      - override commit blocks
    required: false
    default: false
"""

EXAMPLES = """
- iosxr_rollback:
    host: '{{ ansible_ssh_host }}'
    username: cisco
    password: cisco
    last_n_committed: 2
    label: bgp_rollback
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
            to_rollback_id = dict(required=False, default=None),
            to_exclude_rollback_id = dict(required=False, default=None),
            rollback_id = dict(required=False, default=None),
            last_n_committed = dict(required=False, default=None),
            label = dict(required=False, default=None),
            force = dict(required=False, type='bool', default=False),
        ),
        mutually_exclusive = (
            [ 'rollback_id', 
              'to_rollback_id', 
              'to_exclude_rollback_id',
              'last_n_committed' ],
        ),
        supports_check_mode = False
    )
    args = module.params
    force = args['force']
    rollback_id = args['rollback_id']
    to_id = args['to_rollback_id']
    to_excl_id = args['to_exclude_rollback_id']
    last_n = args['last_n_committed']
    label = args['label']
    force = args['force']
  
    reload_command = 'rollback configuration '
    if rollback_id is not None:
        reload_command += rollback_id
    if to_id is not None:
        reload_command += 'to %s ' % to_id
    if to_excl_id is not None:
        reload_command += 'to-exclude %s ' % to_excl_id
    if last_n is not None:
        reload_command += 'last %s ' % last_n
    if force is True:
        reload_command += 'force '
    if label is not None:
        reload_command += 'label %s ' % label
    response = execute_command(module, reload_command)
  
    result = dict(changed=True)
    result['stdout'] = response
    result['stdout_lines'] = str(result['stdout']).split(r'\n')

    module.exit_json(**result)

if __name__ == "__main__":
  main()

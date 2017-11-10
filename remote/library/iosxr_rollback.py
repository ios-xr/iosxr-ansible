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
from ansible.module_utils.iosxr import iosxr_argument_spec

DOCUMENTATION = """
---
module: iosxr_rollback
author: Adisorn Ermongkonchai
short_description: Rollback configuration on IOS-XR device
description:
  - Rollback IOS-XR configuration

provider options:
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

module options:
  rollback_id:
    description:
      - rollback configuration committed to particular id
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
      - rollback configuration last N committed made
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
    provider:
      host: "{{ ansible_host }}"
      username: "{{ ansible_user }}"
      password: "{{ ansible_ssh_pass }}"
    last_n_committed: 1
    label: bgp_rollback
    force: True
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
    spec = dict (provider = dict (required = True),
                 rollback_id = dict (required = False, default = None),
                 to_rollback_id = dict (required = False, default = None),
                 to_exclude_rollback_id = dict (required = False,
                                                default = None),
                 last_n_committed = dict (required = False, type = 'int',
                                          default = None),
                 label = dict (required = False, default = None),
                 force = dict (required = False, type = 'bool',
                               default = False))
    spec.update (iosxr_argument_spec)
    module = AnsibleModule (argument_spec = spec,
                            mutually_exclusive = (['rollback_id',
                                                   'to_rollback_id',
                                                   'to_exclude_rollback_id',
                                                   'last_n_committed']))
    args = module.params
    force = args['force']
    rollback_id = args['rollback_id']
    to_id = args['to_rollback_id']
    to_excl_id = args['to_exclude_rollback_id']
    last_n = args['last_n_committed']
    label = args['label']
    force = args['force']

    reload_command = 'source /etc/profile ; PATH=/pkg/sbin:/pkg/bin:${PATH} nsenter -t 1 -n -- config_rollback '
    if rollback_id is not None:
        reload_command += '-j %s ' % rollback_id
    if to_id is not None:
        reload_command += '-i %s ' % to_id
    if to_excl_id is not None:
        reload_command += '-u %s ' % to_excl_id
    if last_n is not None:
        reload_command += '-n %s ' % hex(last_n)
    if force is True:
        reload_command += '-f '
    if label is not None:
        reload_command += '-l %s ' % label
    (rc, out, err) = module.run_command (reload_command,
                                         use_unsafe_shell = True)
  
    result = dict(changed = False)
    result['stdout'] = err
    if 'successfully' in result['stdout']:
        result['changed'] = True
        result['stdout_lines'] = str(result['stdout']).split(r'\n')
        return module.exit_json(**result)
    else:
        return module.fail_json(msg = result['stdout'])

if __name__ == "__main__":
    main()

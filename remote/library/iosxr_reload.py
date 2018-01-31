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

DOCUMENTATION = """
---
module: iosxr_reload
author: Adisorn Ermongkonchai
short_description: Reload IOS-XR device
description:
  - Restart specified IOS-XR device
options:
  confirm:
    description:
      - make sure user really want to reload
    required: true
    value: "yes" or other string
  force:
    description:
      - force reload without doing any cleanup
    required: false
    default: false
"""

EXAMPLES = """
- iosxr_reload:
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
    module = AnsibleModule(
        argument_spec = dict(
            username = dict(required=False, default=None),
            password = dict(required=False, default=None),
            confirm = dict(required=True),
            force   = dict(required=False, type='bool', default=False)
        ),
        supports_check_mode = False
    )
    args = module.params
    if args['confirm'] != 'yes':
        result['stdout'] = "reload aborted"
        module.exit_json(**result)
 
    command = '/bin/echo y > yes'
    (rc, out, err) = module.run_command(command, use_unsafe_shell=True)
    reload_command = 'source /etc/profile ; PATH=/pkg/sbin:/pkg/bin:${PATH} nsenter -t 1 -n -- reload -t 0x0 '
    reload_options = '-a' if args['force'] is True else '-d'
    command = reload_command + reload_options + ' < yes'
    (rc, out, err) = module.run_command(command, use_unsafe_shell=True)
  
    result = dict(changed=False)
    result['stdout'] = out
    result['stdout_lines'] = err if err != "" else out
    return module.exit_json(**result)

if __name__ == "__main__":
    main()

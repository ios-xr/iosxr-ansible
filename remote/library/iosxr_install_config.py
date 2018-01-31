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
module: iosxr_install_config
author: Adisorn Ermongkonchai
short_description: Commit configuration file on IOS-XR device
description:
  - Commit configuration file on IOS-XR device
options:
  cfgname:
    description:
      - fully qualified config filename, e.g. tftp://192.168.1.1/user_add.cfg
    required: true
  label:
    description:
      - assign a label to this commit
    required: false
    default: none
"""

EXAMPLES = """
- iosxr_install_config:
    cfgname: "/tftp://192.168.1.1/user_add.cfg"
    label: "bgp_config_commit"

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
            cfgname  = dict(required=True),
            label    = dict(required=False, default=None),
        ),
        supports_check_mode = False
    )
    args = module.params
    cfg_name = args['cfgname']
    label = args['label']
  
    load_command = 'config -f %s ' % cfg_name
    if label is not None:
        load_command = load_command + '-l "%s"' % label
    command = "source /etc/profile ; PATH=/pkg/sbin:/pkg/bin:${PATH} nsenter -t 1 -n -- %s" % load_command
    (rc, out, err) = module.run_command(command, use_unsafe_shell=True)

    # check for error
    if err != "":
        module.fail_json(msg=err)
  
    change_command = 'show config commit changes last 1'
    command = 'source /etc/profile ; PATH=/pkg/sbin:/pkg/bin:${PATH} nsenter -t 1 -n -- xr_cli "%s"' % \
              change_command
    (rc, out, err) = module.run_command(command, use_unsafe_shell=True)

    result = dict(changed=False)
    result['stdout'] = out
    result['stdout_lines'] = str(result['stdout']).splitlines()

    module.exit_json(**result)

if __name__ == "__main__":
    main()

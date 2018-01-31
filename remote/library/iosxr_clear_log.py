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
module: iosxr_clear_log
author: Adisorn Ermongkonchai
short_description: Clear log
description:
  - Clear system log

EXAMPLES = """
- iosxr_clear_log:
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
        ),
        supports_check_mode = False
    )
  
    command = '/bin/echo yes > yes'
    (rc, out, err) = module.run_command(command, use_unsafe_shell=True)
    command = 'source /etc/profile ; PATH=/pkg/sbin:/pkg/bin:${PATH} nsenter -t 1 -n -- clr_logging < yes'
    (rc, out, err) = module.run_command(command, use_unsafe_shell=True)
  
    result = dict(changed=True)
    result['stdout'] = out if out != "" else err
    return module.exit_json(**result)

if __name__ == "__main__":
    main()

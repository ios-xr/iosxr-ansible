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

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.iosxr import iosxr_argument_spec, run_commands
from ansible.module_utils.connection import exec_command

DOCUMENTATION = """
---
module: iosxr_clear_config
author: Adisorn Ermongkonchai
short_description: Clear all configurations on IOS-XR device
description:
  - Clear all configurations on IOS-XR device

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
  confirm:
    description:
      - make sure user really want to reload
    required: true
    value: "yes" or other string
"""

EXAMPLES = """
- iosxr_clear_config:
    provider:
      host: "{{ ansible_host }}"
      username: "{{ ansible_user }}"
      password: "{{ ansible_ssh_pass }}"
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

CLI_PROMPT_RE = [ r"[\r\n]?proceed\? \[no\]: $" ]

def main ():
    spec = dict (provider = dict (required = True),
                 confirm = dict (required = True))
    spec.update (iosxr_argument_spec)
    module = AnsibleModule (argument_spec = spec)

    result = dict (changed = False)
    if module.params["confirm"] != "yes":
        result["stdout"] = "clear configs aborted"
        module.exit_json (**result)

    command = "configure terminal"
    rc, out, err = exec_command (module, command)
    if rc != 0:
        module.fail_json (msg = "unable to enter configuration mode",
                          err = to_text (err, errors = "surrogate_or_strict"))

    command = {"command": "commit replace",
               "prompt": CLI_PROMPT_RE,
               "answer": "yes"}
    run_commands (module, command, check_rc = False)
  
    result = dict (changed = False)
    result["stdout"] = "all configs cleared"
    result["stdout_lines"] = str (result["stdout"]).split (r"\n")
    return module.exit_json (**result)

if __name__ == "__main__":
    main ()

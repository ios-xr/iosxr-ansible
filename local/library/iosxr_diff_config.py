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
module: iosxr_diff_config
author: Adisorn Ermongkonchai
short_description: Compare a given config file with the running config
description:
  - Compare config file provided with the running configuration
    on the IOS-XR node.

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
  cfgname:
    description:
      - fully qualified config filename, e.g. tftp://192.168.1.1/user_add.cfg
    required: true
"""

EXAMPLES = """
- iosxr_diff_config:
    provider:
      host: "{{ ansible_host }}"
      username: "{{ ansible_user }}"
      password: "{{ ansible_ssh_pass }}"
    cfgname: "tftp://192.168.1.1/add_replace.cfg"
"""

RETURN = """
stdout:
  description: raw response
  returned: always
stdout_lines:
  description: list of response lines
  returned: always
"""

def main ():
    spec = dict (provider = dict (required = True),
                 cfgname = dict (required = True))
    spec.update (iosxr_argument_spec)
    module = AnsibleModule (argument_spec = spec)

    args = module.params
    cfg_name = args["cfgname"]
  
    command = "configure terminal"
    rc, out, err = exec_command (module, command)
    if rc != 0:
        module.fail_json (msg="unable to enter configuration mode",
                          err = to_text (err, errors="surrogate_or_strict"))

    commands = ["load " + cfg_name]
    commands.append ("show commit changes diff")
    response = run_commands  (module, commands)
  
    result = dict (changed = False)
    result["stdout"] = response
    result["stdout_lines"] = str (result["stdout"]).split (r"\n")

    module.exit_json (**result)

if __name__ == "__main__":
  main ()

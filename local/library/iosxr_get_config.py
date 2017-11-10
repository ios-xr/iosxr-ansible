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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.iosxr import iosxr_argument_spec, run_commands

DOCUMENTATION = """
---
module: iosxr_get_config
author: Adisorn Ermongkonchai
short_description: Show running configuration on IOS-XR device
description:
  - Get running configuration from IOS-XR device

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
  component:
    description:
      - component to query
    required: false
    default: all
"""

EXAMPLES = """
- iosxr_get_config:
    provider:
      host: "{{ ansible_host }}"
      username: "{{ ansible_user }}"
      password: "{{ ansible_ssh_pass }}"
    component: "all"

- iosxr_get_config:
    provider:
      host: "{{ ansible_host }}"
      username: "{{ ansible_user }}"
      password: "{{ ansible_ssh_pass }}"
    component: "router static"
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
                 component = dict (required = False, default = "all"))
    spec.update (iosxr_argument_spec)
    module = AnsibleModule (argument_spec = spec)

    args = module.params
    comp = args["component"]
    command = "show running-config " + comp
    response = run_commands (module, command)

    result = dict (changed = False)
    result["stdout"] = response
    result["stdout_lines"] = str (result["stdout"]).split (r"\n")
    return module.exit_json (**result)

if __name__ == "__main__":
    main ()

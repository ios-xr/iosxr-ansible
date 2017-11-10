#!/usr/bin/python
# ------------------------------------------------------------------------------
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
# ------------------------------------------------------------------------------

from ansible.module_utils.basic import *
from ansible.module_utils.iosxr import iosxr_argument_spec
import sys
sys.path.append("/pkg/bin/")
from ztp_helper import ZtpHelpers

DOCUMENTATION = """
---
module: iosxr_install_config
author: Adisorn Ermongkonchai
short_description: Commit configuration file on IOS-XR device
description:
  - Commit configuration file on IOS-XR device

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
  label:
    description:
      - assign a label to this commit
    required: false
    default: none
"""

EXAMPLES = """
- iosxr_install_config:
    provider:
      host: "{{ ansible_host }}"
      username: "{{ ansible_user }}"
      password: "{{ ansible_ssh_pass }}"
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
    spec = dict (provider = dict (required = True),
                 cfgname = dict (required = True),
                 label = dict (required = False, default = None))
    spec.update (iosxr_argument_spec)
    module = AnsibleModule (argument_spec = spec)

    script = ZtpHelpers()

    args = module.params
    cfg_name = args["cfgname"]
    label = args["label"]
    command = cfg_name
    if label:
        command += label
    script.xrapply (command)

    change_command = "show config commit changes last 1"
    out = script.xrcmd ({"exec_cmd": change_command})

    result = dict (changed = False)
    result["stdout"] = out
    result["stdout_lines"] = str(out["output"]).splitlines()

    module.exit_json (**result)


if __name__ == "__main__":
    main()

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
module: iosxr_install_config
author: Adisorn Ermongkonchai
short_description: Commit configuration file on IOS-XR device
description:
  - load and commit configuration file on IOS-XR device

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
  replace:
    description:
      - remove all current running-config and apply new config
    required: false
    default: false
  force:
    description:
      - override commit blocks
    required: false
    default: false
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
    cfgname: "tftp://192.168.1.1/add_user.cfg"
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

CLI_PROMPT_RE = [ r"[\r\n]?proceed\? \[no\]: $" ]

def main ():
    spec = dict (provider = dict (required = True),
                 cfgname= dict (required = True),
                 label= dict (required = False, default = None),
                 replace= dict (required = False, type="bool", default = False),
                 force= dict (required = False, type="bool", default = False))
    spec.update (iosxr_argument_spec)
    module = AnsibleModule (argument_spec = spec)

    args = module.params
    cfg_name = args["cfgname"]
    label = args["label"]
    force = args["force"]
    replace = args["replace"]
  
    # enter config mode
    command = "configure terminal"
    rc, out, err = exec_command (module, command)
    if rc != 0:
        module.fail_json (msg="unable to enter configuration mode",
                          err = to_text (err, errors="surrogate_or_strict"))

    # load config command
    command = "load " + cfg_name
    rc, out, err = exec_command (module, command)
    if rc != 0:
        module.fail_json (msg="configuration loader failed",
                          err = to_text (err, errors="surrogate_or_strict"))
  
    # commit configuration
    commit_command = "commit "
    if replace is True:
        commit_command = commit_command + "replace "
    if force is True:
        commit_command = commit_command + "force "
    if label != None:
        commit_command = commit_command + "label " + label
    command = {"command": commit_command,
               "prompt": CLI_PROMPT_RE,
               "answer": "yes"}

    response = run_commands (module, command)
  
    result = dict (changed = True)
    result["stdout"] = response
    result["stdout_lines"] = str (result["stdout"]).split (r"\n")

    # show and log changes to file
    response = run_commands (module, "show config commit changes last 1")
    result["stdout"] = response
    result["stdout_lines"] = str (result["stdout"]).split (r"\n")

    module.exit_json (**result)

if __name__ == "__main__":
  main ()

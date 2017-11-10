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
module: iosxr_reload
author: Adisorn Ermongkonchai
short_description: Reload IOS-XR device
description:
  - Restart specified IOS-XR device

provider options:
  host:
    description:
      - IP address or hostname (resolvable by Ansible control host) of
        the target IOS-XR node.
    required: true
  username:
    description:
      - username used to login to IOS-XR
    required: true
    default: none
  password:
    description:
      - password used to login to IOS-XR
    required: true
    default: none

module options:
  confirm:
    description:
      - make sure user really want to reload
    required: true
    value: "yes" or other string
  location:
    description:
      - location of the node that needs to be reboot
        e.g. 0/RP0/CPU0
    required: false
    default: None
  force:
    description:
      - force reaload without doing any cleanup
    required: false
    default: false

"""

EXAMPLES = """
- iosxr_reload:
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

CLI_PROMPT_RE = [ r"[\r\n]?[confirm]" ]

def main ():
    spec = dict (provider = dict (required = True),
                 confirm= dict (required = True),
                 location= dict (required = False, default = None),
                 force= dict (required = False, type="bool", default = False))
    spec.update (iosxr_argument_spec)
    module = AnsibleModule (argument_spec = spec)
    
    args = module.params
    force = args["force"]
    location = args["location"]

    result = dict (changed = False)
    if args["confirm"] != "yes":
        result["stdout"] = "reload aborted"
        module.exit_json (**result)
 
    # setup reload command expecting specific prompt to return
    reload_command = "reload "
    if location != None:
        reload_command = reload_command + "location %s " % location
    if force is True:
        reload_command = reload_command + "force "
    command = {"command": reload_command,
               "prompt": CLI_PROMPT_RE,
               "answer": "y"}
    response = run_commands (module, command)

    result["stdout"] = response
    result["stdout_lines"] = str (result["stdout"]).split (r"\n")
    module.exit_json (**result)

if __name__ == "__main__":
  main ()

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
module: iosxr_install_key
author: Adisorn Ermongkonchai
short_description: Install BASE64 crypto key on IOS-XR device
description:
  - Install BASE64 crypto key on IOS-XR device

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
  keyfile:
    description:
      - fully qualified base64 key file, e.g. tftp://192.168.1.28/id_rsa_pub.b64
    note:
      - following commands show how to convert Linux rsa key file to base64 file
        $cut -d" " -f2 ~/.ssh/id_rsa.pub | base64 -d > ~/.ssh/id_rsa_pub.b64
    required: true
"""

EXAMPLES = """
- iosxr_install_config:
    provider:
      host: "{{ ansible_host }}"
      username: "{{ ansible_user }}"
      password: "{{ ansible_ssh_pass }}"
    keyfile: "tftp://192.168.1.28/id_rsa_pub.b64"

"""

RETURN = """
stdout:
  description: raw response
  returned: always
stdout_lines:
  description: list of response lines
  returned: always
"""

CLI_PROMPT_RE = [ r"[\r\n]?\[yes\/no\]: $" ]

def main ():
    spec = dict (provider = dict (required = True),
                 keyfile = dict (required = True))
    spec.update (iosxr_argument_spec)
    module = AnsibleModule (argument_spec = spec)

    args = module.params
    keyfile = args["keyfile"]
  
    show_command = "show crypto key authentication rsa"
    response = run_commands (module, show_command)

    cmd = "crypto key import authentication rsa " + keyfile
    if "authentication" in response[0]:
        crypto_command = {"command": cmd,
                          "prompt": CLI_PROMPT_RE,
                          "answer": "yes"}
    else:
        crypto_command = cmd
    response = run_commands (module, crypto_command)

    # now show the new key
    response = run_commands (module, show_command)

    result = dict (changed = True)
    result["stdout"] = response
    result["stdout_lines"] = str (result["stdout"]).split (r"\n")

    module.exit_json (**result)

if __name__ == "__main__":
  main ()

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

import re
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.iosxr import iosxr_argument_spec, run_commands

DOCUMENTATION = """
---
module: iosxr_upgrade_package
author: Adisorn Ermongkonchai
short_description: Upgrade packages on IOS-XR device.
description:
  - Upgrade IOS-XR packages on the IOS-XR device.

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
  timeout:
    description:
      - default timeout value might be too short for IOS-XR install 
        due to several different factors so put timeout value that
        work for you, e.g. 30 seconds
    required: true
    value: integer in seconds
  confirm:
    description:
      - make sure user really want to reload
    required: true
    value: "yes" or other string
  version:
    description:
      - new software version
    required: true
  pkgpath:
    description:
      - souce directory for the package(s)
        Example:
          sftp://user@server/directory/
          ftp://user@server/directory/
          scp://user@server/directory/
          tftp://server/directory/
          http://server/directory/
          https://server/directory/
    required: true
  rpmname:
    description:
      - IOS-XR software packages
        e.g. xrv9k-ospf-1.0.0.0-r61102I.x86_64.rpm
    required: false
    default: none
"""

EXAMPLES = """
- iosxr_upgrade_package:
    provider:
      host: "{{ ansible_host }}"
      username: "{{ ansible_user }}"
      password: "{{ ansible_ssh_pass }}"
    version: 6.1.1
    confirm: yes
    pkgpath: "https://secure_server_name"
    rpmname: "xrv9k-ospf-2.0.0.0-r64121I.x86_64.rpm"
"""

RETURN = """
stdout:
  description: raw response
  returned: always
stdout_lines:
  description: list of response lines
  returned: always
"""

# check if another install command in progress
def is_legacy_iosxr (module):
    command = "show version"
    response = run_commands (module, command)
    return "Build Information:" not in response[0]

# check if another install command in progress
def is_install_in_progress (module):
    command = "show install request"
    response = run_commands (module, command)
    return "No install operation in progress" not in response[0]

CLI_PROMPT_RE = [ r"[\r\n]?\[yes\/no]:\[\w+]\s" ]

def main ():
    spec = dict (provider = dict (required = True),
                 confirm = dict (required = True),
                 version = dict (required = True, default = None),
                 pkgpath = dict (required = True, default = None),
                 rpmname = dict (required = False, default = ""))
    spec.update (iosxr_argument_spec)
    module = AnsibleModule (argument_spec = spec)

    args = module.params
    version = args["version"]
    pkg_path = args["pkgpath"]
    rpm_name = args["rpmname"]

    # confirm upgrade
    result = dict (changed = False)
    if args["confirm"] != "yes":
        result["stdout"] = "upgrade aborted"
        module.exit_json (**result)

    # cannot run on classic XR
    if is_legacy_iosxr (module):
        module.fail_json (msg="this upgrade module cannot run on 32-bit IOS-XR")

    # make sure no other install in progress
    if is_install_in_progress (module):
        module.fail_json (msg="other install operation in progress")

    # run install upgrade command
    install_command = ('install upgrade source ' + pkg_path +
                       ' version ' + version + ' ' + rpm_name + '\n')
    command = {"command": install_command,
               "prompt": CLI_PROMPT_RE,
               "answer": "yes"}
    response = run_commands (module, command)

    # check if operation successful
    if re.search ("(?i)aborted", response[0]) or \
       re.search ("(?i)error", response[0]):
        pattern = re.compile (r"operation (\d+) started")
        oper_id = pattern.findall (response[0])
        command = "show install log " + oper_id[0]
        log_msg = run_commands (module, command)
        for line in str (log_msg).split (r"\n"):
            if "ERROR" in line or "Error" in line:
                response = line
        result = dict (changed = False, failed = True)
    else:
        # now wait till reload
        while True:
            try:
                #  install operation done
                if not is_install_in_progress(module):
                    break
                sleep(5)
            # or socket exception when reload
            except:
                break

    # show result
    result["stdout"] = response
    result["stdout_lines"] = str (result["stdout"]).splitlines ()

    module.exit_json (**result)

if __name__ == "__main__":
    main ()

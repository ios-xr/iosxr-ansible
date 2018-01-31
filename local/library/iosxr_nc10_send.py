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
from ansible.module_utils.shell import *
from ansible.module_utils.netcfg import *
from iosxr_common import *
from iosxr import *

DOCUMENTATION = """
---
module: iosxr_nc10_send
author: Adisorn Ermongkonchai
short_description: Send NETCONF 1.0 XML file to IOS-XR device
description:
  - Send NETCONF 1.0 XML file to IOS-XR device
options:
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
  xmlfile:
    description:
      - XML file
    required: true
    example: nc_show_install_active.xml
      <?xml version="1.0" encoding="UTF-8"?>
      <rpc message-id="101" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
        <get>
          <filter>
            <Operational>
              <SoftwareInstall>
                <Active/>
              </SoftwareInstall>
            </Operational>
          </filter>
        </get>
      </rpc>
"""

EXAMPLES = """
- iosxr_nc10_send:
    host: '{{ ansible_ssh_host }}'
    username: cisco
    password: cisco
    xmlfile: xml/nc_show_install_active.xml
"""

RETURN = """
stdout:
  description: raw response
  returned: always
stdout_lines:
  description: list of response lines
  returned: always
"""

CLI_PROMPTS_RE.append(re.compile(r']]>]]>[\r\n]?'))

def main():
    module = get_module(
        argument_spec = dict(
            xmlfile = dict(required=True)
        ),
        supports_check_mode = False
    )
    args = module.params
    xml_file = module.params['xmlfile']

    result = dict(changed=False)
    xml_text = open(xml_file).read()
    if 'edit-config' in xml_text or 'delete-config' in xml_text:
        result['changed'] = True

    module.execute('netconf format')
    module.connection.shell.shell.send(xml_text)
    module.connection.shell.shell.send(']]>]]>\n')

    # collect all responses 1024 bytes at a time
    response = module.connection.shell.shell.recv(1024)
    while ']]>]]>' not in response:
        response += module.connection.shell.shell.recv(1024)

    result['stdout'] = response
    if 'rpc-error' in response:
        return module.fail_json(msg=response)
    else:
        return module.exit_json(**result)

if __name__ == "__main__":
    main()

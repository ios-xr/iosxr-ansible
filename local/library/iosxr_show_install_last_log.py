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
from ydk.providers import NetconfServiceProvider
from ydk.services import CRUDService
from ydk.models.cisco_ios_xr.Cisco_IOS_XR_spirit_install_instmgr_oper import SoftwareInstall

def main():
    module = AnsibleModule(
        argument_spec = dict(
            host = dict(required=True),
            username = dict(required=False, default=None),
            password = dict(required=False, default=None),
        ),
        supports_check_mode = False
    )

    args = module.params

    # establish ssh connection
    provider = NetconfServiceProvider(address=args['host'],
                                      port=830,
                                      username=args['username'],
                                      password=args['password'],
                                      protocol='ssh')
    # establish CRUD service
    crud = CRUDService()

    # retrieve software install version
    install = SoftwareInstall()
    info = crud.read(provider, install)

    result = dict(changed=False)
    result['stdout'] = "no log available"
    for logger in info.last_n_operation_logs.last_n_operation_log:
      result['stdout'] = logger.summary.log
    return module.exit_json(**result)

if __name__ == "__main__":
    main()

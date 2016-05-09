#
# Copyright 2016 Cisco Systems
# Author: Adisorn Ermognkonchai
#

import time

def execute_command(module, command):
    retries = 5
    while retries > 0:
        try:
            response = module.execute(command)
            return response
        except:
            pass
        retries -= 1
        time.sleep(2)
    else:
        module.fail_json(msg="too many timeouts trying to send command")


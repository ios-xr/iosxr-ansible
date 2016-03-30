Ansible Test Setup
==================

- Create 2 XRV9K (Sunstone) VMs and 1 Linux server on MB Cloud following
  the instruction in the link below
  * http://tc-midnight.cisco.com:8080/wiki/MB%20Cloud%20XR

  NOTE:
    The nightly build images provided on the MB Cloud is based on xr-dev.
    Unfortunately, the missing Python libraries were committed to r60y
    (CSCux90222).  These missing libraries are required for Ansible to run
    in "remote" mode.  The tests that were exercising here run on "local" mode

- You will also need k9sec security package to be installed in your XRV9K VMs.
  Using the following example command to install the k9sec pacakge.
  * install update source tftp://192.168.1.1 xrv9k-iosxr-security-1.0.0.0-r60125I
  * show install active

- Pull YDK from the gitlab.cisco.com into the Linux server created
  * git clone git@gitlab.cisco.com:ydk-dev/ydk-py.git

- Pull Ansible Core modules
  * git clone git://github.com/ansible/ansible.git --recursive

  Addition read on Ansible installation is here
  * http://docs.ansible.com/ansible/intro_installation.html#getting-ansible

Running Ansible
===============

- Edit and source Ansible, YDK, and Python environment to point to your
  installed applications
  * cd iosxr/local
  * vi ansible_env
  * source ansible_env

- Edit "ansible_hosts" file to change "ss-xr" host IP to your 2 XRV9K VMs

- Create default crypto key in your XRV9K VMs (select default 1024 bits)
  * crypto key generate rsa 
  * show crypto key mypubkey rsa

- Configure IOS-XR as shown in ss1.cfg and ss2.cfg for both XRV9K VMs.
  Make any necessary changes, such as, management IP address and hostname
  Here are required configuration
  * ssh server v2
  * ssh server netconf vrf default
  * ssh server logging
  * xml agent ssl
  * netconf agent tty
  * netconf-yang agent ssh

- Make sure you can connect to both XRV9K VMs management port
  * ssh root@x.x.x.x
  * ssh root@x.x.x.x "show run"

  NOTE:
    Currently, crypto key import is not working (CSCuy80921) so when
    using Ansible playbook, password is required.

Additional Notes
================

- How to GitLab?
  * https://cisco.jiveon.com/docs/DOC-42998


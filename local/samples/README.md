This directory and its subdirectories contains sample playbooks, convenient scripts, and sample XML files to interact with the IOS-XR using Ansible in local mode.  As mentioned in the main README page, there are 6 methods of accessing IOS-XR in local mode.

1. Console CLI
2. TPNNS CLI
3. Raw XML
4. Raw NETCONF 1.0
5. Raw NETCONF 1.1
6. YDK NETCONF API

The playbooks that are in the base directory are those that provide the commonly used functionalities in network software configuration and maintenance on the IOS-XR.  Along with these playbooks are convenient scripts used to invoke Ansible using these playbooks.  The samples in the subdirectories are intended to show different methods of accessing IOS-XR.

Noted that there are 2 sample playbooks with xr32 on their filename, they are intended for legacy QNX-based IOS-XR SMU installation playbook.  All playbooks with iosxr prefix can be used with Linux-based IOS-XR and some can be used with QNX-based.

There are 4 subdirectories,

1. cli   - contains playbooks showing how to use Ansible network module, iosxr_command, to communicate with IOS-XR CLI shell in exec mode.
2. tpnns - contains playbooks showing how to use Ansible to access IOS-XR thirdparty namespace (TPNNS) Linux shell through SSH port 57722 and interact with IOS-XR.
3. xml   - contains 3 different types of Cisco and NETCONF XML files showing how IOS-XR data can be configured or queried.  There are many scripts in the base directory that make use of these XML files
4. ydk   - contains playbooks that uses Ansible modules with YDK service.


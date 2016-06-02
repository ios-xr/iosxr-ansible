This directory and its subdirectories contains sample playbooks and convenient scripts interact with the IOS-XR using Ansible in remote mode.  There is only one method of accessing IOS-XR in remote mode which is through IOS-XR thirdparty namespace (TPNNS)

The playbooks that are in the base directory are those that provide the commonly used functionalities in network software configuration and maintenance on the IOS-XR.  Along with these playbooks are convenient scripts used to invoke Ansible using these playbooks.  The samples in the subdirectories are intended to show different methods of accessing IOS-XR.

Each CLI command has an IOS-XR application associated with it.  The subdirectory, install, shows how to directly access IOS-XR install application through Ansible and Cisco TPNNS.

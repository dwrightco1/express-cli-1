##
## Ansible Inventory
##
[all]
[all:vars]

[hypervisors]

################################################################################################
## Kubernetes Groups
################################################################################################
[pmk:children]
k8s_worker

[k8s_worker]
$node_details


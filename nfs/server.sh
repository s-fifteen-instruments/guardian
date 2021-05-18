#!/bin/sh



dnf install -y nfs-utils
systemctl enable rpcbind nfs-server
systemctl start rpcbind nfs-server
firewall-cmd --add-service=nfs --permanent
firewall-cmd --add-service={nfs,mountd,rpc-bind} --permanent
firewall-cmd --reload


# Assuming you have no other exported dirs
export GUARDIAN_MOUNT=/home/cproctor/code/current/s15/guardian/volumes
echo "${GUARDIAN_MOUNT} 192.168.1.0/24(rw,no_root_squash)" > /etc/exports
exportfs -rv

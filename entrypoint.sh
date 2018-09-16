#!/bin/bash

export BGP_LOCAL=$(ip -4 addr show `route -n | grep '^0.0.0.0' | awk '{print $NF}'` | grep -Eo 'inet [^/]+' |awk '{print $2}' | head -1)
export BGP_PEER=$(route -n | grep '^0.0.0.0' | awk '{print $2}')

sed -i "s/host_gw/$BGP_PEER/" /etc/exabgp/exabgp.conf
sed -i "s/host_if/$BGP_LOCAL/" /etc/exabgp/exabgp.conf
sed -i "s/container_if/$BGP_LOCAL/" /etc/exabgp/exabgp.conf

exabgp /etc/exabgp/exabgp.conf

#!/bin/sh


for IP in `cat block_*.txt`; do
    echo  iptables -I INPUT -p tcp -s $IP -j DROP
    echo  iptables -I INPUT -p udp -s $IP -j DROP
done

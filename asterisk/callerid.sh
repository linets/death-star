#!/bin/bash

## This script will put the callerid as the peer number if the peer doesn't
## have a caller id assigned 

for anexo in `asterisk -rx "sip show peers"  | awk -F/ '{print $1}' | grep -v Name | grep -v peers`; do

    RES=`asterisk -rx "sip show peer $anexo" | grep Callerid`;
    PAS=`echo $RES | grep '"" <>'`;

    if [ $? -eq 0 ]; then
        sed -i -e "s/username\=$anexo/username\=$anexo\ncallerid\=$anexo/g" sip.conf;
    fi;
done

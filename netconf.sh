#!/usr/bin/bash

netconf-console --edit-config /home/dwdd/confd-basic/confd-basic-8.0.2.linux.x86_64/northbound-perf/data.xml
netconf-console --get-config
netconf-console --edit-config /home/dwdd/confd-basic/confd-basic-8.0.2.linux.x86_64/northbound-perf/del.xml
# /home/dwdd/thesis/thesis_app
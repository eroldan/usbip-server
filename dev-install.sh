#!/bin/bash

ansible-playbook --inventory usbgw.lan, --become playbook.yaml $@

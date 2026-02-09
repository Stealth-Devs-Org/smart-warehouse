#!/bin/bash

sudo /home/vipula/srsRAN_Project/scripts/srsran_performance

# sudo systemctl stop power-profiles-daemon.service
# sudo systemctl disable power-profiles-daemon.service

# sudo tuned-adm profile srs
# tuned-adm active

# sudo systemctl enable tuned.service

docker rm -v $(docker ps --filter status=exited -q)
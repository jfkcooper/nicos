#!/bin/sh
session="nicos"

tmux start-server
tmux new-session -d -s $session

tmux new-window -t $session:1 -n cache
tmux send-keys "conda activate nicos_env" C-m
tmux send-keys "export EPICS_CA_AUTO_ADDR_LIST=NO" C-m
tmux send-keys "export EPICS_CA_ADDR_LIST='172.30.238.79'" C-m
tmux send-keys "export EPICS_PVA_AUTO_ADDR_LIST=NO" C-m
tmux send-keys "export EPICS_PVA_ADDR_LIST='172.30.238.79'" C-m
tmux send-keys "bin/nicos-cache" C-m
sleep 5

tmux new-window -t $session:2 -n poller
tmux send-keys "conda activate nicos_env" C-m
tmux send-keys "export EPICS_CA_AUTO_ADDR_LIST=NO" C-m
tmux send-keys "export EPICS_CA_ADDR_LIST='172.30.238.79'" C-m
tmux send-keys "export EPICS_PVA_AUTO_ADDR_LIST=NO" C-m
tmux send-keys "export EPICS_PVA_ADDR_LIST='172.30.238.79'" C-m
tmux send-keys "bin/nicos-poller" C-m

tmux new-window -t $session:3 -n daemon
tmux send-keys "conda activate nicos_env" C-m
tmux send-keys "export EPICS_CA_AUTO_ADDR_LIST=NO" C-m
tmux send-keys "export EPICS_CA_ADDR_LIST='172.30.238.79'" C-m
tmux send-keys "export EPICS_PVA_AUTO_ADDR_LIST=NO" C-m
tmux send-keys "export EPICS_PVA_ADDR_LIST='172.30.238.79'" C-m
tmux send-keys "bin/nicos-daemon" C-m

tmux new-window -t $session:4 -n collector
tmux send-keys "conda activate nicos_env" C-m
tmux send-keys "bin/nicos-collector" C-m

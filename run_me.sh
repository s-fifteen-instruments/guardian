#!/bin/sh


reset
ssh alice@kme1 "cd ~/code/guardian && hostname &&  make clean && make init"
ssh bob@kme2   "cd ~/code/guardian && hostname &&  make clean && make init"
ssh alice@kme1 "cd ~/code/guardian && hostname &&  make rest"
ssh bob@kme2   "cd ~/code/guardian && hostname &&  make rest"

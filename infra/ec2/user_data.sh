#!/bin/bash
sudo apt update
sudo snap install aws-cli --classic
sudo snap install amazon-ssm-agent --classic
sudo apt install -y wget unzip tmux 
sudo systemctl enable snap.amazon-ssm-agent.amazon-ssm-agent.service
sudo systemctl start snap.amazon-ssm-agent.amazon-ssm-agent.service
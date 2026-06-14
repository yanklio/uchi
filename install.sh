#!/bin/bash

# Install Ansible and dependencies
pip install ansible
pip install ansible-lint

# Add Arg Completion
pip install argcomplete
activate-global-python-argcomplete --user

# Add minimal software
curl -fsSL https://tailscale.com/install.sh | sh  # Install Tailscale
curl -fsSL https://proton.me/download/pass-cli/install.sh | bash  # Install Proton Pass CLI

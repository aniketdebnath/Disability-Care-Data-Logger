#!/bin/bash

# Update package lists
sudo apt update

# Install Node.js
sudo apt install -y nodejs npm

# Install Python and FastAPI dependencies
sudo apt install -y python3-pip python3-venv

# Install Nginx
sudo apt install -y nginx

# Enable UFW firewall and allow SSH, HTTP, HTTPS
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Start Nginx service
sudo systemctl start nginx
sudo systemctl enable nginx

echo "Setup complete! Node.js, FastAPI, and Nginx installed."

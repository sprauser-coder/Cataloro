#!/bin/bash

# Server Setup Script for Cataloro Marketplace
# This script sets up a fresh Ubuntu server with all dependencies

set -e

echo "🖥️  Cataloro Marketplace Server Setup"
echo "====================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Update system
update_system() {
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y curl wget git unzip
}

# Install Docker
install_docker() {
    print_status "Installing Docker..."
    
    # Remove old versions
    sudo apt remove -y docker docker-engine docker.io containerd runc || true
    
    # Install dependencies
    sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Add Docker GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    print_status "Docker installed successfully!"
}

# Install Docker Compose
install_docker_compose() {
    print_status "Installing Docker Compose..."
    
    # Get latest version
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)
    
    # Download and install
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_status "Docker Compose installed successfully!"
}

# Setup firewall
setup_firewall() {
    print_status "Setting up firewall..."
    
    sudo ufw --force reset
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    
    # Allow SSH
    sudo ufw allow ssh
    
    # Allow HTTP and HTTPS
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    
    # Allow application ports (for development)
    sudo ufw allow 3000/tcp
    sudo ufw allow 8001/tcp
    
    sudo ufw --force enable
    
    print_status "Firewall configured!"
}

# Setup SSL with Let's Encrypt (optional)
setup_ssl() {
    read -p "Do you want to set up SSL with Let's Encrypt? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installing Certbot for SSL..."
        
        sudo apt install -y certbot
        
        read -p "Enter your domain name: " domain
        read -p "Enter your email: " email
        
        print_warning "Make sure your domain points to this server before proceeding!"
        read -p "Press Enter to continue..."
        
        # Get SSL certificate
        sudo certbot certonly --standalone -d $domain --email $email --agree-tos --non-interactive
        
        # Create SSL directory for Docker
        sudo mkdir -p ./ssl
        sudo cp /etc/letsencrypt/live/$domain/fullchain.pem ./ssl/cert.pem
        sudo cp /etc/letsencrypt/live/$domain/privkey.pem ./ssl/key.pem
        sudo chown -R $USER:$USER ./ssl
        
        print_status "SSL certificate installed!"
        print_warning "Remember to update nginx.conf to enable HTTPS!"
    fi
}

# Create application directory
setup_app_directory() {
    print_status "Setting up application directory..."
    
    mkdir -p ~/cataloro-marketplace
    cd ~/cataloro-marketplace
    
    print_status "Application directory created at ~/cataloro-marketplace"
}

# Main setup process
main() {
    print_status "Starting server setup..."
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
        exit 1
    fi
    
    update_system
    install_docker
    install_docker_compose
    setup_firewall
    setup_app_directory
    setup_ssl
    
    print_status "Server setup completed!"
    echo ""
    echo "Next steps:"
    echo "1. Log out and log back in (or run 'newgrp docker')"
    echo "2. Upload your application files to ~/cataloro-marketplace"
    echo "3. Configure your .env file"
    echo "4. Run ./deploy.sh to start the application"
    echo ""
    print_warning "Please reboot or log out and back in for Docker group changes to take effect!"
}

main
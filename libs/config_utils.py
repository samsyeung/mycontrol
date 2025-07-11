#!/usr/bin/env python3

import json
import logging
import socket
from pathlib import Path

logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / 'config.json'
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in config file: {config_path}")
        return {}

def find_host_by_hostname(hosts, hostname):
    """Find a host configuration by hostname (IPMI or SSH)"""
    for host in hosts:
        if host.get('ipmi_host') == hostname or host.get('ssh_host') == hostname:
            return host
    return None

def get_local_hostname(config):
    """Get the local hostname for terminal URLs, with fallback to FQDN then hostname"""
    local_hostname = config.get('local_hostname')
    if local_hostname:
        return local_hostname
    
    try:
        # Try to get FQDN first (more useful for remote access)
        fqdn = socket.getfqdn()
        hostname = socket.gethostname()
        
        # Prefer FQDN if it's a proper domain name (not reverse DNS or localhost)
        if (fqdn and fqdn != 'localhost' and '.' in fqdn and 
            not fqdn.endswith('.arpa') and not fqdn.startswith('127.')):
            return fqdn
        
        # Fallback to regular hostname
        if hostname and hostname != 'localhost':
            return hostname
            
        # Last resort
        return 'localhost'
    except Exception as e:
        logger.warning(f"Failed to get system hostname: {e}")
        return 'localhost'
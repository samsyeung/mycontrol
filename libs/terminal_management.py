#!/usr/bin/env python3

import subprocess
import os
import signal
import time
import tempfile
import stat
import logging

# Get the app logger to ensure proper logging configuration
logger = logging.getLogger('app')

class TerminalManager:
    """Manages ttyd terminal processes"""
    
    def __init__(self, ttyd_base_port=7681, local_hostname='localhost'):
        self.ttyd_base_port = ttyd_base_port
        self.local_hostname = local_hostname
        self.ssh_processes = {}
        self.nvtop_processes = {}
    
    def _check_ttyd_available(self):
        """Check if ttyd is available"""
        try:
            subprocess.run(['ttyd', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_sshpass_available(self):
        """Check if sshpass is available"""
        try:
            subprocess.run(['sshpass', '-V'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _kill_existing_process(self, hostname, process_dict):
        """Kill any existing process for a hostname"""
        if hostname in process_dict:
            try:
                os.kill(process_dict[hostname]['pid'], signal.SIGTERM)
                time.sleep(0.5)  # Give it time to shutdown
            except ProcessLookupError:
                pass  # Process already dead
    
    def start_ssh_terminal(self, hostname, ssh_host, ssh_username=None):
        """Start a ttyd SSH terminal"""
        if not self._check_ttyd_available():
            return {'success': False, 'message': 'ttyd not installed. Please install ttyd to use SSH terminals.'}
        
        # Generate a unique port for this terminal session
        terminal_port = self.ttyd_base_port + hash(hostname) % 1000
        
        # Kill any existing SSH process for this host
        self._kill_existing_process(hostname, self.ssh_processes)
        
        try:
            if ssh_username:
                # Use configured username, but still prompt for password
                cmd = [
                    'ttyd',
                    '--port', str(terminal_port),
                    '--interface', '0.0.0.0',  # Bind to all interfaces for remote access
                    '--once',  # Close after one client disconnects
                    '--writable',  # Allow keyboard input
                    'ssh', 
                    '-o', 'StrictHostKeyChecking=no',
                    '-o', 'UserKnownHostsFile=/dev/null',
                    '-o', 'LogLevel=ERROR',
                    f'{ssh_username}@{ssh_host}'
                ]
            else:
                # Fallback to manual authentication (original behavior)
                cmd = [
                    'ttyd',
                    '--port', str(terminal_port),
                    '--interface', '0.0.0.0',  # Bind to all interfaces for remote access
                    '--once',  # Close after one client disconnects
                    '--writable',  # Allow keyboard input
                    'ssh', 
                    '-o', 'StrictHostKeyChecking=no',
                    '-o', 'UserKnownHostsFile=/dev/null',
                    '-o', 'LogLevel=ERROR',
                    ssh_host
                ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Store process info
            self.ssh_processes[hostname] = {
                'pid': process.pid,
                'port': terminal_port,
                'host': ssh_host,
                'started': time.time()
            }
            
            # Give ttyd a moment to start up
            time.sleep(1)
            
            # Check if process is still running
            if process.poll() is not None:
                # Process died, get error output
                _, stderr = process.communicate()
                return {
                    'success': False, 
                    'message': f'Failed to start terminal: {stderr.decode()}'
                }
            
            logger.info(f"Started SSH terminal for {hostname} on port {terminal_port} with username: {ssh_username or 'manual'}")
            
            return {
                'success': True,
                'terminal_url': f'http://{self.local_hostname}:{terminal_port}',
                'message': 'SSH terminal started successfully'
            }
            
        except Exception as e:
            logger.error(f"Error starting SSH terminal for {hostname}: {e}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def start_nvtop_terminal(self, hostname, ssh_host, ssh_username, ssh_password=None, nvtop_path="nvtop", sshpass_path="sshpass"):
        """Start a ttyd nvtop terminal"""
        if not self._check_ttyd_available():
            return {'success': False, 'message': 'ttyd not installed. Please install ttyd to use nvtop terminal.'}
        
        # Generate a unique port for this nvtop session
        nvtop_port = self.ttyd_base_port + hash(f"{hostname}_nvtop") % 1000
        
        # Kill any existing nvtop process for this host
        self._kill_existing_process(hostname, self.nvtop_processes)
        
        try:
            if ssh_password:
                # Check if sshpass is available for password authentication
                if not self._check_sshpass_available():
                    return {'success': False, 'message': 'sshpass not installed. Please install sshpass to use password-based SSH terminals.'}
                
                # Create a temporary script for password-based SSH similar to working SSH terminal
                with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                    f.write(f'''#!/bin/bash
export SSHPASS='{ssh_password}'
{sshpass_path} -e ssh -t -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR {ssh_username}@{ssh_host} "export TERM=xterm-256color; {nvtop_path}"
''')
                    script_path = f.name
                
                # Make script executable
                os.chmod(script_path, stat.S_IRWXU)
                
                # Start ttyd with the script
                cmd = [
                    'ttyd',
                    '--port', str(nvtop_port),
                    '--interface', '0.0.0.0',  # Bind to all interfaces for remote access
                    '--once',  # Close after one client disconnects
                    '/bin/bash', script_path
                ]
            else:
                # Use key-based authentication, similar to working SSH terminal
                cmd = [
                    'ttyd',
                    '--port', str(nvtop_port),
                    '--interface', '0.0.0.0',  # Bind to all interfaces for remote access
                    '--once',  # Close after one client disconnects
                    'ssh',
                    '-t',
                    '-o', 'StrictHostKeyChecking=no',
                    '-o', 'UserKnownHostsFile=/dev/null',
                    '-o', 'LogLevel=ERROR',
                    f'{ssh_username}@{ssh_host}',
                    f'export TERM=xterm-256color; {nvtop_path}'
                ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Store process info
            self.nvtop_processes[hostname] = {
                'pid': process.pid,
                'port': nvtop_port,
                'host': ssh_host,
                'started': time.time()
            }
            
            # Give ttyd a moment to start up
            time.sleep(1)
            
            # Check if process is still running
            if process.poll() is not None:
                # Process died, get error output
                stdout, stderr = process.communicate()
                logger.error(f"nvtop terminal process died immediately. stdout: {stdout.decode()}, stderr: {stderr.decode()}")
                return {
                    'success': False, 
                    'message': f'Failed to start nvtop terminal: {stderr.decode()}'
                }
            
            logger.info(f"Started nvtop terminal for {hostname} on port {nvtop_port}")
            
            return {
                'success': True,
                'terminal_url': f'http://{self.local_hostname}:{nvtop_port}',
                'message': 'nvtop terminal started successfully'
            }
            
        except Exception as e:
            logger.error(f"Error starting nvtop terminal for {hostname}: {e}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def list_ssh_terminals(self):
        """List active SSH terminals"""
        return self._list_terminals(self.ssh_processes)
    
    def list_nvtop_terminals(self):
        """List active nvtop terminals"""
        return self._list_terminals(self.nvtop_processes)
    
    def _list_terminals(self, process_dict):
        """List active terminals for a given process dictionary"""
        active_terminals = []
        current_time = time.time()
        
        # Clean up dead processes
        for hostname in list(process_dict.keys()):
            try:
                # Check if process is still alive
                os.kill(process_dict[hostname]['pid'], 0)
                # Add to active list if it's been running for less than 1 hour
                if current_time - process_dict[hostname]['started'] < 3600:
                    active_terminals.append({
                        'hostname': hostname,
                        'port': process_dict[hostname]['port'],
                        'host': process_dict[hostname]['host'],
                        'url': f"http://{self.local_hostname}:{process_dict[hostname]['port']}"
                    })
            except ProcessLookupError:
                # Process is dead, remove it
                del process_dict[hostname]
        
        return active_terminals
    
    def stop_ssh_terminal(self, hostname):
        """Stop SSH terminal for a specific host"""
        return self._stop_terminal(hostname, self.ssh_processes, 'SSH terminal')
    
    def stop_nvtop_terminal(self, hostname):
        """Stop nvtop terminal for a specific host"""
        return self._stop_terminal(hostname, self.nvtop_processes, 'nvtop terminal')
    
    def _stop_terminal(self, hostname, process_dict, terminal_type):
        """Stop a terminal for a specific host"""
        if hostname in process_dict:
            try:
                os.kill(process_dict[hostname]['pid'], signal.SIGTERM)
                del process_dict[hostname]
                return {'success': True, 'message': f'{terminal_type} stopped'}
            except ProcessLookupError:
                del process_dict[hostname]
                return {'success': True, 'message': f'{terminal_type} was already stopped'}
        else:
            return {'success': False, 'message': f'No active {terminal_type} found'}
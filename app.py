#!/usr/bin/env python3

from flask import Flask, render_template, jsonify, request
import subprocess
import json
import logging
import os
import signal
import time
from pathlib import Path
from logging.handlers import RotatingFileHandler
from libs.ssh_utils import get_host_uptimes
from libs.grafana_utils import process_dashboards
from libs.power_management import get_power_status, power_on_host
from libs.network_utils import check_host_ping
from libs.gpu_management import get_gpu_info_sync, get_gpu_topo_info_sync, get_docker_info_sync, parse_docker_output_to_html, docker_action_sync
from libs.terminal_management import TerminalManager
from libs.config_utils import load_config, find_host_by_hostname, get_local_hostname
from libs.version import get_version, get_version_info, get_build_info

class DeduplicatingHandler(logging.Handler):
    """A logging handler that prevents duplicate log messages"""
    
    def __init__(self, target_handler):
        super().__init__()
        self.target_handler = target_handler
        self.recent_messages = {}
        self.max_age = 1.0  # Consider messages within 1 second as duplicates
        
    def emit(self, record):
        import time
        current_time = time.time()
        message_key = (record.levelno, record.getMessage())
        
        # Clean old messages
        self.recent_messages = {
            k: v for k, v in self.recent_messages.items() 
            if current_time - v < self.max_age
        }
        
        # Check if this is a duplicate
        if message_key not in self.recent_messages:
            self.recent_messages[message_key] = current_time
            self.target_handler.emit(record)
    
    def setFormatter(self, formatter):
        self.target_handler.setFormatter(formatter)
        
    def setLevel(self, level):
        super().setLevel(level)
        self.target_handler.setLevel(level)

app = Flask(__name__)

def setup_logging():
    logs_dir = Path(__file__).parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    log_file = logs_dir / 'mycontrol.log'
    
    # Disable all existing logging completely
    logging.disable(logging.NOTSET)  # Re-enable logging
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Clear all loggers
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.disabled = True
    
    # Create file handler
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    
    # Configure Flask app logger
    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    
    # Add console handler only if running interactively (not via control script)
    if os.getenv('MYCONTROL_INTERACTIVE', '').lower() == 'true':
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        app.logger.addHandler(console_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False  # Critical: don't propagate
    app.logger.disabled = False
    
    # Disable werkzeug logging completely
    logging.getLogger('werkzeug').disabled = True

logger = setup_logging()


# Initialize terminal manager (will be updated with config values)
terminal_manager = None

def get_terminal_manager():
    """Get terminal manager instance with current config"""
    global terminal_manager
    if terminal_manager is None:
        config = load_config()
        ttyd_base_port = config.get('ttyd_base_port', 7681)
        local_hostname = get_local_hostname(config)
        terminal_manager = TerminalManager(ttyd_base_port, local_hostname)
    return terminal_manager


@app.route('/')
def index():
    config = load_config()
    hosts = config.get('hosts', [])
    ipmitool_path = config.get('ipmitool_path', 'ipmitool')
    ssh_timeout = config.get('ssh_timeout', 10)
    grafana_dashboards = config.get('grafana_dashboard_urls', [])
    
    # Process Grafana dashboards
    updated_dashboards = process_dashboards(grafana_dashboards)
    
    # Build host status list (without SSH uptime initially for faster page load)
    host_status = []
    for host in hosts:
        ipmi_host = host.get('ipmi_host')
        ipmi_username = host.get('ipmi_username')
        ipmi_password = host.get('ipmi_password')
        ssh_host = host.get('ssh_host')
        name = host.get('name', ipmi_host or ssh_host)
        
        # Get power status only (fast IPMI check)
        if ipmi_host and ipmi_username and ipmi_password:
            power_status = get_power_status(ipmi_host, ipmi_username, ipmi_password, ipmitool_path)
        else:
            power_status = 'config_error'
        
        host_status.append({
            'name': name,
            'hostname': ipmi_host or ssh_host,  # Keep for backwards compatibility
            'ipmi_host': ipmi_host,
            'ssh_host': ssh_host,
            'status': power_status,
            'uptime': 'Loading...',  # Will be updated via AJAX
        })
    
    refresh_interval = config.get('refresh_interval', 0)
    
    return render_template('index.html', 
                          hosts=host_status, 
                          grafana_dashboards=updated_dashboards, 
                          refresh_interval=refresh_interval,
                          version=get_version(),
                          build_info=get_build_info())

@app.route('/api/status')
def api_status():
    config = load_config()
    hosts = config.get('hosts', [])
    ipmitool_path = config.get('ipmitool_path', 'ipmitool')
    ssh_timeout = config.get('ssh_timeout', 10)
    
    # Get SSH uptimes in parallel
    ssh_results = get_host_uptimes(hosts, ssh_timeout)
    
    # Build host status list
    host_status = []
    for (host, uptime) in ssh_results:
        ipmi_host = host.get('ipmi_host')
        ipmi_username = host.get('ipmi_username')
        ipmi_password = host.get('ipmi_password')
        ssh_host = host.get('ssh_host')
        name = host.get('name', ipmi_host or ssh_host)
        
        # Get power status
        if ipmi_host and ipmi_username and ipmi_password:
            power_status = get_power_status(ipmi_host, ipmi_username, ipmi_password, ipmitool_path)
        else:
            power_status = 'config_error'
        
        host_status.append({
            'name': name,
            'hostname': ipmi_host or ssh_host,
            'status': power_status,
            'uptime': uptime
        })
    
    return jsonify({'hosts': host_status})

@app.route('/api/uptime/<hostname>')
def get_uptime(hostname):
    """Get uptime for a specific host via SSH"""
    config = load_config()
    hosts = config.get('hosts', [])
    ssh_timeout = config.get('ssh_timeout', 10)
    
    # Find the host in config
    target_host = find_host_by_hostname(hosts, hostname)
    
    if not target_host:
        return jsonify({'success': False, 'uptime': 'Host not found'})
    
    ssh_host = target_host.get('ssh_host')
    ssh_username = target_host.get('ssh_username')
    ssh_password = target_host.get('ssh_password')
    
    if not ssh_host or not ssh_username:
        return jsonify({'success': False, 'uptime': 'No SSH config'})
    
    # Check if host is pingable first
    ping_result = check_host_ping(ssh_host)
    if not ping_result.get('success') or ping_result.get('status') != 'online':
        return jsonify({'success': False, 'uptime': 'Host unreachable'})
    
    # Get uptime using the existing SSH utility
    from libs.ssh_utils import get_uptime_sync
    uptime = get_uptime_sync(ssh_host, ssh_username, ssh_password, ssh_timeout)
    
    return jsonify({'success': True, 'uptime': uptime})

@app.route('/api/ping/<hostname>')
def check_ping(hostname):
    """Check if a host is reachable via ping"""
    config = load_config()
    hosts = config.get('hosts', [])
    
    # Find the host in config
    target_host = find_host_by_hostname(hosts, hostname)
    
    if not target_host:
        return jsonify({'success': False, 'status': 'error', 'message': 'Host not found'})
    
    # Use SSH host if available, otherwise use IPMI host
    ping_target = target_host.get('ssh_host') or target_host.get('ipmi_host')
    
    if not ping_target:
        return jsonify({'success': False, 'status': 'error', 'message': 'No host address configured'})
    
    result = check_host_ping(ping_target)
    return jsonify(result)

@app.route('/api/power-on/<hostname>', methods=['POST'])
def api_power_on(hostname):
    config = load_config()
    hosts = config.get('hosts', [])
    ipmitool_path = config.get('ipmitool_path', 'ipmitool')
    
    # Find the host in config
    target_host = find_host_by_hostname(hosts, hostname)
    
    if not target_host:
        return jsonify({'success': False, 'message': 'Host not found in configuration'}), 404
    
    # Extract credentials
    ipmi_username = target_host.get('ipmi_username')
    ipmi_password = target_host.get('ipmi_password')
    
    if not ipmi_username or not ipmi_password:
        return jsonify({'success': False, 'message': 'Missing credentials in configuration'}), 400
    
    # Attempt to power on
    result = power_on_host(hostname, ipmi_username, ipmi_password, ipmitool_path)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route('/api/ssh-terminal/<hostname>', methods=['POST'])
def start_ssh_terminal(hostname):
    """Start a ttyd SSH terminal for the specified host"""
    config = load_config()
    hosts = config.get('hosts', [])
    
    # Find the host in config
    target_host = find_host_by_hostname(hosts, hostname)
    
    if not target_host:
        return jsonify({'success': False, 'message': 'Host not found in configuration'}), 404
    
    ssh_host = target_host.get('ssh_host')
    if not ssh_host:
        return jsonify({'success': False, 'message': 'No SSH host configured for this server'}), 400
    
    result = get_terminal_manager().start_ssh_terminal(hostname, ssh_host)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route('/api/ssh-terminals')
def list_ssh_terminals():
    """List active SSH terminals"""
    terminals = get_terminal_manager().list_ssh_terminals()
    return jsonify({'terminals': terminals})

@app.route('/api/gpu-info/<hostname>')
def get_gpu_info(hostname):
    """Get GPU information via SSH by running nvidia-smi"""
    config = load_config()
    hosts = config.get('hosts', [])
    ssh_timeout = config.get('ssh_timeout', 10)
    
    # Find the host in config
    target_host = find_host_by_hostname(hosts, hostname)
    
    if not target_host:
        return jsonify({'success': False, 'message': 'Host not found in configuration'}), 404
    
    ssh_host = target_host.get('ssh_host')
    ssh_username = target_host.get('ssh_username')
    ssh_password = target_host.get('ssh_password')
    
    if not ssh_host:
        return jsonify({'success': False, 'message': 'No SSH host configured for this server'}), 400
    
    if not ssh_username:
        return jsonify({'success': False, 'message': 'No SSH username configured for this server'}), 400
    
    result = get_gpu_info_sync(ssh_host, ssh_username, ssh_password, ssh_timeout)
    return jsonify(result)

@app.route('/api/gpu-topo-info/<hostname>')
def get_gpu_topo_info(hostname):
    """Get GPU topology information via SSH by running nvidia-smi topo -m"""
    config = load_config()
    hosts = config.get('hosts', [])
    ssh_timeout = config.get('ssh_timeout', 10)
    
    # Find the host in config
    target_host = find_host_by_hostname(hosts, hostname)
    
    if not target_host:
        return jsonify({'success': False, 'message': 'Host not found in configuration'}), 404
    
    ssh_host = target_host.get('ssh_host')
    ssh_username = target_host.get('ssh_username')
    ssh_password = target_host.get('ssh_password')
    
    if not ssh_host:
        return jsonify({'success': False, 'message': 'No SSH host configured for this server'}), 400
    
    if not ssh_username:
        return jsonify({'success': False, 'message': 'No SSH username configured for this server'}), 400
    
    result = get_gpu_topo_info_sync(ssh_host, ssh_username, ssh_password, ssh_timeout)
    return jsonify(result)

@app.route('/api/docker-info/<hostname>')
def get_docker_info(hostname):
    """Get Docker containers information via SSH by running docker ps -a"""
    config = load_config()
    hosts = config.get('hosts', [])
    ssh_timeout = config.get('ssh_timeout', 10)
    
    # Find the host in config
    target_host = find_host_by_hostname(hosts, hostname)
    
    if not target_host:
        return jsonify({'success': False, 'message': 'Host not found in configuration'}), 404
    
    ssh_host = target_host.get('ssh_host')
    ssh_username = target_host.get('ssh_username')
    ssh_password = target_host.get('ssh_password')
    
    if not ssh_host:
        return jsonify({'success': False, 'message': 'No SSH host configured for this server'}), 400
    
    if not ssh_username:
        return jsonify({'success': False, 'message': 'No SSH username configured for this server'}), 400
    
    result = get_docker_info_sync(ssh_host, ssh_username, ssh_password, ssh_timeout)
    
    if result['success']:
        # Parse the docker output into HTML table
        html_table = parse_docker_output_to_html(result['output'], hostname)
        return jsonify({'success': True, 'html': html_table})
    else:
        return jsonify(result)

@app.route('/api/docker-action/<hostname>', methods=['POST'])
def docker_action(hostname):
    """Perform Docker action (start/stop) on a container"""
    try:
        data = request.get_json()
        container_id = data.get('container_id')
        action = data.get('action')
        
        if not container_id or not action:
            return jsonify({'success': False, 'message': 'Missing container_id or action'}), 400
        
        if action not in ['start', 'stop']:
            return jsonify({'success': False, 'message': 'Invalid action. Must be start or stop'}), 400
        
        config = load_config()
        hosts = config.get('hosts', [])
        ssh_timeout = config.get('ssh_timeout', 10)
        
        # Find the host in config
        target_host = find_host_by_hostname(hosts, hostname)
        
        if not target_host:
            return jsonify({'success': False, 'message': 'Host not found in configuration'}), 404
        
        ssh_host = target_host.get('ssh_host')
        ssh_username = target_host.get('ssh_username')
        ssh_password = target_host.get('ssh_password')
        
        if not ssh_host:
            return jsonify({'success': False, 'message': 'No SSH host configured for this server'}), 400
        
        if not ssh_username:
            return jsonify({'success': False, 'message': 'No SSH username configured for this server'}), 400
        
        result = docker_action_sync(ssh_host, ssh_username, ssh_password, container_id, action, ssh_timeout)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/api/nvtop-terminal/<hostname>', methods=['POST'])
def start_nvtop_terminal(hostname):
    """Start a ttyd nvtop terminal for the specified host"""
    config = load_config()
    hosts = config.get('hosts', [])
    
    # Find the host in config
    target_host = find_host_by_hostname(hosts, hostname)
    
    if not target_host:
        return jsonify({'success': False, 'message': 'Host not found in configuration'}), 404
    
    ssh_host = target_host.get('ssh_host')
    ssh_username = target_host.get('ssh_username')
    ssh_password = target_host.get('ssh_password')
    
    if not ssh_host or not ssh_username:
        return jsonify({'success': False, 'message': 'SSH configuration missing for this server'}), 400
    
    # Get nvtop and sshpass paths from config
    nvtop_path = config.get('nvtop_path', 'nvtop')
    sshpass_path = config.get('sshpass_path', 'sshpass')
    
    result = get_terminal_manager().start_nvtop_terminal(hostname, ssh_host, ssh_username, ssh_password, nvtop_path, sshpass_path)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route('/api/nvtop-terminals')
def list_nvtop_terminals():
    """List active nvtop terminals"""
    terminals = get_terminal_manager().list_nvtop_terminals()
    return jsonify({'terminals': terminals})

@app.route('/api/nvtop-stop/<hostname>', methods=['POST'])
def stop_nvtop_terminal(hostname):
    """Stop nvtop terminal for a specific host"""
    result = get_terminal_manager().stop_nvtop_terminal(hostname)
    return jsonify(result)

@app.route('/api/update', methods=['POST'])
def update_application():
    """Trigger application update via git pull and restart"""
    try:
        import subprocess
        import os
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        update_script = os.path.join(script_dir, 'update.sh')
        
        if not os.path.exists(update_script):
            return jsonify({'success': False, 'message': 'Update script not found'}), 500
        
        if not os.access(update_script, os.X_OK):
            return jsonify({'success': False, 'message': 'Update script is not executable'}), 500
        
        # Run update script in background, detached from parent process
        # Use a new process group to avoid signal propagation when parent dies
        try:
            process = subprocess.Popen([update_script], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     cwd=script_dir,
                                     start_new_session=True)  # Create new session (detach from terminal)
        except Exception as e:
            app.logger.error(f"Failed to start update process: {e}")
            return jsonify({'success': False, 'message': f'Failed to start update process: {str(e)}'}), 500
        
        app.logger.info("Update process started")
        return jsonify({'success': True, 'message': 'Update process initiated. Application will restart if updates are available.'}), 200
        
    except Exception as e:
        app.logger.error(f"Failed to start update process: {e}")
        return jsonify({'success': False, 'message': f'Failed to start update: {str(e)}'}), 500

@app.route('/api/version')
def api_version():
    """Get application version information"""
    try:
        version_info = get_version_info()
        return jsonify({
            'success': True,
            'version': version_info['version'],
            'tag': version_info['tag'],
            'revision': version_info['revision'],
            'branch': version_info['branch'],
            'commit_count': version_info['commit_count'],
            'commit_date': version_info['commit_date'],
            'is_dirty': version_info['is_dirty'],
            'build_info': version_info['build_info']
        }), 200
    except Exception as e:
        app.logger.error(f"Failed to get version info: {e}")
        return jsonify({'success': False, 'message': f'Failed to get version: {str(e)}'}), 500

if __name__ == '__main__':
    config = load_config()
    port = config.get('port', 5010)
    
    app.logger.info(f"Starting MyControl application on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
# My Lab Control Systemd Service

This directory contains systemd service files and installation scripts for running My Lab Control as a system service.

## Files

- `mylabcontrol.service` - Systemd service unit file
- `install-service.sh` - Installation script for setting up the service
- `uninstall-service.sh` - Uninstallation script for removing the service

## Quick Installation

1. **Install the service:**
   ```bash
   sudo ./install-service.sh
   ```

2. **Configure the application:**
   ```bash
   sudo nano /opt/mylabcontrol/config.json
   ```

3. **Start the service:**
   ```bash
   sudo systemctl start mylabcontrol
   sudo systemctl enable mylabcontrol  # Auto-start on boot
   ```

## Service Details

- **Service Name:** `mylabcontrol`
- **Installation Path:** `/opt/mylabcontrol`
- **User/Group:** `mylabcontrol:mylabcontrol`
- **Service Type:** Forking (uses control.sh script)
- **Auto-restart:** Enabled with 10-second delay
- **Logs:** Available via `journalctl -u mylabcontrol`

## Security Features

The service includes several security hardening measures:

- Dedicated non-privileged user account
- No new privileges allowed
- Protected system directories
- Private temporary directory
- Kernel protection enabled
- Read-write access only to application directory

## Management Commands

```bash
# Service control
sudo systemctl start mylabcontrol      # Start
sudo systemctl stop mylabcontrol       # Stop
sudo systemctl restart mylabcontrol    # Restart
sudo systemctl reload mylabcontrol     # Reload (restart)
sudo systemctl status mylabcontrol     # Status

# Boot management
sudo systemctl enable mylabcontrol     # Auto-start on boot
sudo systemctl disable mylabcontrol    # Disable auto-start

# Logs
sudo journalctl -u mylabcontrol        # View logs
sudo journalctl -u mylabcontrol -f     # Follow logs
sudo journalctl -u mylabcontrol --since "1 hour ago"  # Recent logs
```

## Troubleshooting

### Service won't start
1. Check the configuration file exists and is valid:
   ```bash
   sudo test -f /opt/mylabcontrol/config.json && echo "Config exists"
   sudo python3 -m json.tool /opt/mylabcontrol/config.json > /dev/null && echo "Config is valid JSON"
   ```

2. Check file permissions:
   ```bash
   sudo ls -la /opt/mylabcontrol/
   ```

3. Check service logs:
   ```bash
   sudo journalctl -u mylabcontrol --no-pager
   ```

### Permission errors
The service runs as the `mylabcontrol` user. Ensure all files are owned correctly:
```bash
sudo chown -R mylabcontrol:mylabcontrol /opt/mylabcontrol
```

### Port conflicts
Check if the configured port is already in use:
```bash
sudo netstat -tlnp | grep :5010
```

### Dependencies missing
The service will automatically install Python dependencies on startup, but system dependencies must be installed manually:
```bash
# Ubuntu/Debian
sudo apt-get install ipmitool ttyd sshpass

# CentOS/RHEL/Fedora
sudo dnf install ipmitool ttyd sshpass
```

## Updating the Application

The service supports the built-in update functionality:

1. **Via web interface:** Use the Update button in the web UI
2. **Via command line:**
   ```bash
   sudo -u mylabcontrol /opt/mylabcontrol/update.sh
   ```

The service will automatically restart after updates if changes are detected.

## Uninstallation

To completely remove the service:

```bash
sudo ./uninstall-service.sh
```

This will:
- Stop and disable the service
- Remove the systemd service file
- Optionally remove application files and user account

## Custom Configuration

The service unit file can be customized by editing `/etc/systemd/system/mylabcontrol.service` after installation:

```bash
sudo systemctl edit mylabcontrol  # Create override file
# OR
sudo nano /etc/systemd/system/mylabcontrol.service  # Edit directly
sudo systemctl daemon-reload  # Reload after changes
```

Common customizations:
- Change user/group
- Modify restart behavior
- Add environment variables
- Adjust security settings
# Changelog

All notable changes to the MyControl project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.0] - 2025-01-08

### Added
- **Systemd service support** - Production-ready service deployment capabilities
  - `mylabcontrol.service` systemd unit file with security hardening
  - `install-service.sh` automated installation script for system service setup
  - `uninstall-service.sh` clean removal script for complete service uninstallation
  - Dedicated `mylabcontrol` user and group for secure service operation
  - Service runs from `/opt/mylabcontrol` with proper file permissions and ownership
  - Automatic restart on failure with 10-second delay for reliability
  - Integration with systemd journal for centralized logging
  - Security features: NoNewPrivileges, ProtectSystem, PrivateTmp, kernel protection
  - Auto-start capability on system boot when enabled
  - Support for standard systemctl management commands
- **Enhanced documentation** - Comprehensive service deployment guidance
  - Updated README.md with systemd service installation instructions
  - `SERVICE.md` detailed service management and troubleshooting guide
  - Complete service management command reference
  - Troubleshooting section for common deployment issues

### Enhanced
- **Production deployment** - Professional system service capabilities
  - Dedicated user isolation for improved security posture
  - Automatic dependency installation and virtual environment management
  - Systemd integration for proper process lifecycle management
  - Update functionality preserved in service context with proper permissions
  - Configuration management with secure file permissions

## [1.4.1] - 2025-01-08

### Fixed
- **Web update compatibility** - Resolved subprocess creation error on web interface
  - Removed problematic `preexec_fn` parameter causing "Exception occurred in preexec_fn" errors
  - Improved cross-platform compatibility for web-triggered updates
  - Enhanced error handling for subprocess creation with better error reporting
  - Maintained process isolation using `start_new_session=True` for reliable updates

## [1.4.0] - 2025-01-08

### Fixed
- **Critical web update reliability** - Resolved process management issues with web-triggered updates
  - Fixed update script termination when triggered from web interface
  - Process isolation using new session and process group to prevent signal propagation
  - Added timing delay to ensure web response completion before application restart
  - Eliminated race conditions between Flask app termination and update script execution
- **Enhanced hostname resolution** - Improved FQDN fallback logic
  - Better fallback chain: config → valid FQDN → hostname → localhost
  - Filter out reverse DNS results and invalid domain names
  - More reliable terminal URL generation for remote access

### Enhanced
- **Intelligent update tracking** - Improved user experience during updates
  - Smart restart detection using version API endpoint instead of fixed timeout
  - Progressive feedback showing update progress and restart status
  - Automatic page refresh once application restart is confirmed
  - Better error handling and timeout management for update process

## [1.3.1] - 2025-01-06

### Changed
- **Improved default settings** - Better out-of-box user experience
  - Auto-refresh now defaults to "Off" instead of 30 seconds for better user control
  - Updated configuration template to reflect new defaults
- **Enhanced interface layout** - Improved button positioning and visual hierarchy
  - Moved Update button to the left of Refresh button for better prominence
  - Adjusted button spacing and margins for cleaner appearance
- **Updated documentation** - Refreshed visual assets
  - Updated main dashboard screenshot with latest interface improvements
  - Screenshots now reflect current "My Lab Control" branding and features

## [1.3.0] - 2025-01-06

### Enhanced
- **Intelligent update system** - Major improvements to application update handling
  - Application state preservation: Only restarts app if it was running before update
  - Smart restart logic: Leaves stopped applications stopped with clear instructions
  - Enhanced logging and user feedback about update process and state changes
  - No-update scenarios properly handled with version file refresh
- **Clean version tracking** - Resolved version display issues
  - Excluded VERSION file from git tracking to prevent false dirty states
  - Force refresh of version cache after git operations for accurate display
  - Eliminated persistent "-dirty" suffixes when no actual changes exist
  - VERSION file now shows accurate, clean version information

### Fixed
- Update script no longer unnecessarily restarts stopped applications
- Version file displays clean state instead of permanent "-dirty" suffix
- Application state detection and preservation during updates
- Version cache refresh to show current git state accurately

## [1.2.2] - 2025-01-06

### Changed
- **Application rebranding** - Updated title and branding throughout interface
  - Changed application title from "MyControl - Host Power Status Monitor" to "My Lab Control"
  - Added 🖥️ computer/server emoji icon as favicon and in header
  - Updated version display to reflect new application name
- **Enhanced host information display** - Improved visibility of connection details
  - Show both IPMI and SSH host addresses in host cards
  - Color-coded host types: IPMI (orange) and SSH (green) for easy identification
  - Maintained backward compatibility with existing JavaScript functionality
- **Streamlined interface** - Cleaner and more professional layout
  - Removed redundant "Host Status" heading for cleaner appearance
  - Enhanced visual hierarchy with improved spacing and typography
  - Monospace font for technical host details

## [1.2.1] - 2025-01-06

### Added
- **Version system** - Comprehensive git-based version tracking and display
  - `libs/version.py` module for extracting version from git tags and commits
  - Smart versioning with tag-based releases and development builds
  - Dirty state detection for uncommitted changes
  - Web interface version display at bottom of page with build info tooltip
  - `/api/version` endpoint for programmatic version access
  - Automatic VERSION file generation on startup and updates
  - Integration with control.sh and update.sh scripts

### Enhanced
- **Version Display** - Professional version information throughout application
  - Git tag-based versioning (e.g., v1.2.1)
  - Development version tracking (e.g., v1.2.0+3.abc1234-dirty)
  - Branch, commit count, and date information
  - Build traceability for deployment management

## [1.2.0] - 2025-01-06

### Added
- **Auto-update functionality** - One-click git pull and application restart
  - `update.sh` script for automated git updates and dependency management
  - Update button in web interface next to refresh button
  - `/api/update` endpoint for triggering updates via web interface
  - Comprehensive update logging to `logs/update.log`
  - Smart update detection - only restarts if changes are available
  - Automatic dependency updates when `requirements.txt` changes
  - Git stash handling for uncommitted local changes

### Enhanced
- **Web Interface** - Improved header controls and user experience
  - Green "Update" button with visual feedback states
  - Progress indicators during update process
  - User-friendly status messages and error handling
  - Auto-refresh after successful updates

### Documentation
- Added update management section to README
- Updated API documentation with new update endpoint
- Enhanced feature list with auto-update capability

## [1.1.0] - 2025-01-06

### Added
- `local_hostname` configuration option for terminal URLs with automatic hostname detection
- Support for remote browser access to SSH and nvtop terminals

### Changed
- Terminal services now bind to all interfaces (0.0.0.0) instead of localhost-only
- Terminal URLs use configured hostname instead of hardcoded localhost
- Improved remote access capability for web-based terminals

### Fixed
- Remote browsers can now properly connect to ttyd terminals
- Terminal URLs correctly resolve to the server hostname for remote clients

## [0.7.1] - 2025-01-07

### Added
- **Enhanced documentation** - Comprehensive visual showcase of application features
  - Added 6 new screenshots demonstrating all major functionality
  - Main dashboard overview showing host status and monitoring tools
  - GPU Summary monitoring with nvidia-smi output display
  - GPU Topology analysis for multi-GPU system interconnects
  - Docker container management interface with start/stop controls
  - Web-based SSH terminal access demonstration
  - Real-time nvtop monitoring interface showcase
- **Improved README structure** - Better organization and visual presentation
  - Detailed feature descriptions with accompanying screenshots
  - Step-by-step visual guide through application capabilities
  - Enhanced user onboarding experience with clear feature explanations

### Enhanced
- **Documentation quality** - More comprehensive and user-friendly documentation
  - Visual documentation of all monitoring and management features
  - Clear explanations of GPU monitoring, Docker management, and terminal access
  - Better presentation of multi-host management capabilities

## [0.7.0] - 2025-01-07

### Added
- **Docker container management** - Complete Docker monitoring and control capabilities
  - Docker containers table showing all containers with formatted information
  - Start/Stop buttons for individual container management
  - Real-time container status with color-coded indicators (running=green, exited=red, etc.)
  - Container details including ID, name, image, status, ports, and creation date
  - JSON-based parsing for reliable data extraction from `docker ps -a --format json`
- **Enhanced GPU monitoring interface** - Improved button layout and organization
  - GPU Summary button (renamed from nvidia-smi for clarity)
  - GPU Topology button showing `nvidia-smi topo -m` output for multi-GPU systems
  - Docker button integrated with GPU monitoring section
  - Consistent button styling across all monitoring tools
- **Terminal interface improvements** - Better organization of SSH and monitoring tools
  - nvtop button moved to header next to SSH button for logical grouping
  - Terminal buttons container with proper spacing and alignment
  - Improved visual hierarchy for host management actions

### Enhanced
- **User interface refinements** - Better visual organization and usability
  - Reorganized button layout for improved workflow
  - Enhanced table styling with hover effects and alternating row colors
  - Responsive action buttons with loading states and visual feedback
  - Consistent color scheme across different monitoring sections
- **API endpoints expansion** - Extended functionality for container management
  - `/api/docker-info/<hostname>` - Retrieve Docker container information
  - `/api/docker-action/<hostname>` - Start/stop Docker containers remotely
  - JSON response format for structured data handling
  - Comprehensive error handling and validation

### Technical Improvements
- Enhanced SSH command execution for Docker operations with proper timeout handling
- Improved HTML table generation with structured data parsing
- Better error messaging and user feedback for all Docker operations
- Optimized refresh mechanism for real-time status updates

## [0.6.0] - 2025-01-07

### Added
- **Configurable tool paths** - Support for custom binary paths in configuration
  - `sshpass_path` configuration option for custom sshpass binary location
  - Enhanced flexibility for different system configurations and installations
- **Improved ping-based connectivity checks** - Smarter uptime monitoring
  - Uptime requests now check host connectivity via ping before attempting SSH
  - Prevents unnecessary SSH connection timeouts to unreachable hosts
  - Faster response times and better user experience

### Fixed
- **nvtop terminal functionality** - Resolved critical terminal execution issues
  - Fixed "execvp failed" errors in nvtop popup terminals
  - Added pseudo-terminal allocation (`-t` flag) for proper nvtop execution
  - Set proper terminal environment (`TERM=xterm-256color`) for display compatibility
  - Removed unsupported ttyd options (`--title-format`, `--readonly`) causing failures
  - nvtop terminals now work reliably across different system configurations
- **Git repository cleanup** - Removed unnecessary tracked files
  - Removed log files and PID files from version control
  - Improved .gitignore patterns for cleaner repository management

### Technical Improvements
- Enhanced error handling and debugging capabilities for terminal management
- Improved SSH connection reliability with proper terminal allocation
- Better integration between configuration system and library modules
- Streamlined terminal command construction and execution

## [0.5.0-alpha] - 2025-01-07

### Added
- **Network connectivity monitoring** - Real-time ping status indicators
  - Ping status indicator next to power status showing online/offline/error states
  - Non-blocking ping checks after page load for better performance
  - Visual indicators with colored badges (green=online, red=offline, yellow=error)
- **Compact UI improvements** - Streamlined interface design
  - Smaller power status badges and buttons for cleaner layout
  - Reduced padding and font sizes for better space utilization
  - More compact status indicators while maintaining readability

### Changed
- **nvtop implementation** - Switched to popup terminal approach
  - nvtop now opens in popup window using SSH terminal (like SSH feature)
  - Changed from page-embedded streaming to dedicated terminal window
  - Button renamed from "GPU Stream" to "nvtop" for clarity
  - Read-only SSH terminal session specifically for nvtop monitoring
  - Uses configured SSH credentials instead of requiring sshpass
- **Major code refactoring** - Improved maintainability and organization
  - Renamed `utils/` directory to `libs/` for better naming convention
  - Split large `app.py` into focused library modules:
    - `libs/power_management.py` - IPMI power control functions
    - `libs/network_utils.py` - Ping and network connectivity
    - `libs/gpu_management.py` - GPU information retrieval
    - `libs/terminal_management.py` - SSH and nvtop terminal management
    - `libs/config_utils.py` - Configuration loading and utilities
  - Reduced main application file by ~300 lines
  - Better separation of concerns and reusable components

### Fixed
- nvtop streaming connection errors with proper SSH credential handling
- DOM element selection issues with hostnames containing special characters
- Terminal management now properly uses configured SSH credentials

### Technical Improvements
- Class-based terminal management for better process lifecycle control
- Centralized configuration loading and host lookup utilities
- Improved error handling and resource cleanup
- More maintainable codebase with clear module boundaries

## [0.3.0] - 2025-01-07

### Added
- **Real-time nvtop streaming** - Live GPU monitoring with expandable sections
  - nvtop button positioned next to nvidia-smi for easy access
  - Server-Sent Events (SSE) for real-time streaming output
  - Black terminal-style interface with auto-scrolling
  - Manual stop controls and automatic cleanup
  - Proper SSH process management and error handling
- **Enhanced SSH terminal interface** - Improved user experience
  - Custom wrapper with close button in terminal header
  - Professional dark header design with hostname display
  - Always-visible close button for easy session termination
  - Safari popup blocker compatibility maintained
- **Improved GPU monitoring layout** - Better button organization
  - Side-by-side placement of nvidia-smi and nvtop buttons
  - Consistent styling and responsive design
  - Enhanced error handling and user feedback

### Fixed
- SSH terminal connection issues with host key algorithms
- Popup blocking in Safari browser for SSH terminals
- Improved SSH connection reliability with proper options

### Technical Improvements
- Server-Sent Events implementation for real-time data streaming
- Process lifecycle management for nvtop SSH sessions
- Enhanced error handling and connection management
- Better resource cleanup and memory management

## [0.2.0] - 2025-01-07

### Added
- **Web-based SSH terminals** - Direct SSH access to servers through the browser
  - Browser-based SSH terminal sessions using ttyd
  - SSH Terminal button on each host card
  - Secure localhost-only terminal binding
  - Automatic terminal cleanup after client disconnect
  - Unique port allocation per host to prevent conflicts
  - Manual SSH authentication required (no auto-login)
- New API endpoints for SSH terminal management:
  - `POST /api/ssh-terminal/<hostname>` - Start SSH terminal for a host
  - `GET /api/ssh-terminals` - List active SSH terminals
- `ttyd_base_port` configuration option for SSH terminal port management
- **GPU Status Monitoring** - Expandable sections showing nvidia-smi output
  - GPU Status button appears on powered-on hosts
  - Fetches real-time GPU information via SSH
  - Expandable/collapsible interface with loading states
  - Formatted output in monospace font for readability
  - Error handling for hosts without nvidia-smi
- New API endpoint: `GET /api/gpu-info/<hostname>` - Get GPU information via nvidia-smi

## [0.1.0] - 2025-06-06

### Added
- Application screenshot in README showing interface and features
- Documentation images directory structure
- `config.json.example` template with sample configuration
- `.gitignore` file to protect sensitive configuration
- Enhanced security documentation

### Changed
- Improved project structure by moving utility modules to `utils/` subdirectory
- Cleaner root directory with better organization
- Enhanced README with visual application preview
- Setup process now uses example configuration file for security
- Removed actual configuration file from version control

### Security
- **BREAKING**: `config.json` is no longer tracked in git for security
- Users must create `config.json` from the provided example template
- Added comprehensive security notes and best practices

### Added
- SSH uptime monitoring functionality
- Asynchronous SSH connections for fast uptime retrieval
- Configurable dashboard iframe heights per dashboard
- Configurable auto-refresh interval (default 30 seconds)
- Configurable SSH timeout (default 10 seconds)
- Optional dashboard headers (omit name to hide header)
- Power-on functionality for hosts via IPMI when powered off
- Comprehensive configuration validation
- Modular code structure with separate utility modules

### Changed
- **BREAKING**: Configuration structure updated with prefixed keys:
  - `hostname` → `ipmi_host`
  - `username` → `ipmi_username` 
  - `password` → `ipmi_password`
- Reorganized Grafana dashboards to display below host status in 2-column grid
- Improved configuration format for better organization
- Enhanced README with detailed configuration options
- Refactored codebase into separate modules for better maintainability

### Fixed
- **Major**: Eliminated duplicate log entries that were appearing twice in log files
- Improved logging configuration to prevent handler conflicts
- Fixed dashboard header display when no name is configured

### Technical Improvements
- Split SSH functionality into `ssh_utils.py` module
- Split Grafana functionality into `grafana_utils.py` module
- Simplified main `app.py` by using utility modules
- Added deduplication logic to prevent duplicate logging
- Implemented environment variable option for console logging during development
- Disabled propagation to root logger to prevent conflicts
- Added ThreadPoolExecutor for parallel SSH connections
- Enhanced error handling and timeout management

### Dependencies
- Added `asyncssh` for SSH connectivity

## Configuration Migration Guide

If upgrading from a previous version, update your `config.json`:

```json
{
  "hosts": [
    {
      "name": "Server Name",
      "ipmi_host": "192.168.1.100",      // was: "hostname"
      "ipmi_username": "ipmi_user",      // was: "username" 
      "ipmi_password": "ipmi_password",  // was: "password"
      "ssh_host": "192.168.1.100",      // new: for uptime monitoring
      "ssh_username": "user",           // new: for SSH access
      "ssh_password": "password"        // new: for SSH access
    }
  ],
  "grafana_dashboard_urls": [           // enhanced structure
    {
      "name": "Dashboard Name",         // optional: omit to hide header
      "url": "https://grafana.example.com/...",
      "height": 400                     // new: configurable height
    }
  ],
  "refresh_interval": 30,               // new: configurable refresh
  "ssh_timeout": 10                     // new: SSH timeout setting
}
```
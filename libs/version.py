#!/usr/bin/env python3

import subprocess
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class VersionInfo:
    """Handles version information extraction from git"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.parent
        self._version_cache = None
        
    def _run_git_command(self, cmd):
        """Run a git command and return the output"""
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.script_dir,
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def _get_git_tag(self):
        """Get the latest git tag"""
        return self._run_git_command(['git', 'describe', '--tags', '--abbrev=0'])
    
    def _get_git_revision(self):
        """Get the current git revision (short hash)"""
        return self._run_git_command(['git', 'rev-parse', '--short', 'HEAD'])
    
    def _get_git_revision_long(self):
        """Get the current git revision (full hash)"""
        return self._run_git_command(['git', 'rev-parse', 'HEAD'])
    
    def _get_git_branch(self):
        """Get the current git branch"""
        return self._run_git_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    
    def _get_git_commit_count(self):
        """Get the total number of commits"""
        result = self._run_git_command(['git', 'rev-list', '--count', 'HEAD'])
        return int(result) if result else None
    
    def _get_git_commit_date(self):
        """Get the date of the latest commit"""
        return self._run_git_command(['git', 'log', '-1', '--format=%ci'])
    
    def _is_git_dirty(self):
        """Check if there are uncommitted changes"""
        result = self._run_git_command(['git', 'status', '--porcelain'])
        return bool(result)
    
    def _get_tag_distance(self):
        """Get distance from latest tag"""
        result = self._run_git_command(['git', 'describe', '--tags'])
        if result and '-' in result:
            parts = result.split('-')
            if len(parts) >= 2:
                try:
                    return int(parts[1])
                except ValueError:
                    pass
        return 0
    
    def get_version_info(self, force_refresh=False):
        """Get comprehensive version information"""
        if self._version_cache and not force_refresh:
            return self._version_cache
        
        # Check if we're in a git repository
        if not (self.script_dir / '.git').exists():
            self._version_cache = {
                'version': 'unknown',
                'tag': None,
                'revision': None,
                'revision_long': None,
                'branch': None,
                'commit_count': None,
                'commit_date': None,
                'is_dirty': False,
                'tag_distance': 0,
                'version_string': 'unknown',
                'build_info': 'Not a git repository'
            }
            return self._version_cache
        
        # Gather git information
        tag = self._get_git_tag()
        revision = self._get_git_revision()
        revision_long = self._get_git_revision_long()
        branch = self._get_git_branch()
        commit_count = self._get_git_commit_count()
        commit_date = self._get_git_commit_date()
        is_dirty = self._is_git_dirty()
        tag_distance = self._get_tag_distance()
        
        # Determine version string
        if tag and tag_distance == 0:
            # We're exactly on a tag
            version = tag
            if is_dirty:
                version += '-dirty'
        elif tag and tag_distance > 0:
            # We're ahead of the latest tag
            version = f"{tag}+{tag_distance}.{revision}"
            if is_dirty:
                version += '-dirty'
        elif revision:
            # No tags, use revision
            version = f"dev-{revision}"
            if is_dirty:
                version += '-dirty'
        else:
            version = 'unknown'
        
        # Create build info string
        build_parts = []
        if branch and branch != 'HEAD':
            build_parts.append(f"branch:{branch}")
        if commit_count:
            build_parts.append(f"commits:{commit_count}")
        if commit_date:
            build_parts.append(f"date:{commit_date[:10]}")  # Just the date part
        
        build_info = ', '.join(build_parts) if build_parts else 'No build info available'
        
        self._version_cache = {
            'version': version,
            'tag': tag,
            'revision': revision,
            'revision_long': revision_long,
            'branch': branch,
            'commit_count': commit_count,
            'commit_date': commit_date,
            'is_dirty': is_dirty,
            'tag_distance': tag_distance,
            'version_string': version,
            'build_info': build_info
        }
        
        return self._version_cache
    
    def get_version_string(self):
        """Get a simple version string"""
        info = self.get_version_info()
        return info['version_string']
    
    def get_build_info(self):
        """Get build information string"""
        info = self.get_version_info()
        return info['build_info']
    
    def write_version_file(self, filepath=None):
        """Write version information to a file"""
        if filepath is None:
            filepath = self.script_dir / 'VERSION'
        
        info = self.get_version_info()
        
        with open(filepath, 'w') as f:
            f.write(f"Version: {info['version']}\n")
            f.write(f"Tag: {info['tag'] or 'None'}\n")
            f.write(f"Revision: {info['revision'] or 'None'}\n")
            f.write(f"Branch: {info['branch'] or 'None'}\n")
            f.write(f"Commit Count: {info['commit_count'] or 'None'}\n")
            f.write(f"Commit Date: {info['commit_date'] or 'None'}\n")
            f.write(f"Dirty: {info['is_dirty']}\n")
            f.write(f"Tag Distance: {info['tag_distance']}\n")
            f.write(f"Build Info: {info['build_info']}\n")
        
        logger.info(f"Version file written to {filepath}")
        return filepath

# Global instance
_version_info = VersionInfo()

def get_version():
    """Get the current version string"""
    return _version_info.get_version_string()

def get_version_info():
    """Get detailed version information"""
    return _version_info.get_version_info()

def get_build_info():
    """Get build information"""
    return _version_info.get_build_info()

def write_version_file(filepath=None):
    """Write version file"""
    return _version_info.write_version_file(filepath)

def refresh_version():
    """Force refresh of version information"""
    return _version_info.get_version_info(force_refresh=True)

if __name__ == '__main__':
    # CLI usage
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--write':
            filepath = sys.argv[2] if len(sys.argv) > 2 else None
            write_version_file(filepath)
            print(f"Version file written")
        elif sys.argv[1] == '--info':
            info = get_version_info()
            for key, value in info.items():
                print(f"{key}: {value}")
        else:
            print("Usage: python version.py [--write [filepath]] [--info]")
    else:
        print(f"MyControl version: {get_version()}")
        print(f"Build info: {get_build_info()}")
import platform
import logging
import os
import sys
import multiprocessing
import importlib.metadata  # Modern alternative to pkg_resources

class HealthCheckService:
    def __init__(self):
        """
        Initialize HealthCheckService with logging
        """
        self.logger = logging.getLogger(__name__)

    def perform_checks(self):
        """
        Perform comprehensive system health checks
        
        Returns:
        Dict with health status details
        """
        try:
            health_status = {
                "system": {
                    "os": platform.system(),
                    "release": platform.release(),
                    "python_version": platform.python_version(),
                    "python_implementation": platform.python_implementation()
                },
                "resources": self._get_resource_usage(),
                "dependencies": self._check_dependencies(),
                "status": "operational"
            }
            return health_status
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
            return {
                "status": "degraded",
                "error": str(e)
            }

    def _get_resource_usage(self):
        """
        Retrieve system resource usage with fallback mechanisms
        
        Returns:
        Dict with resource usage information
        """
        resources = {
            "cpu_cores": multiprocessing.cpu_count(),
            "memory": {
                "total": self._get_total_memory(),
                "available": self._get_available_memory()
            }
        }
        
        # Try to get psutil data if available
        try:
            import psutil
            resources.update({
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            })
        except ImportError:
            self.logger.warning("psutil not available. Using limited resource checking.")
        
        return resources

    def _get_total_memory(self):
        """
        Get total system memory
        
        Returns:
        Total memory in bytes
        """
        try:
            import psutil
            return psutil.virtual_memory().total
        except ImportError:
            # Fallback for systems without psutil
            try:
                return os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
            except (AttributeError, ValueError):
                return None

    def _get_available_memory(self):
        """
        Get available system memory
        
        Returns:
        Available memory in bytes
        """
        try:
            import psutil
            return psutil.virtual_memory().available
        except ImportError:
            # Limited fallback
            return None

    def _check_dependencies(self):
        """
        Check critical dependencies
        
        Returns:
        Dict with dependency status
        """
        dependencies = {
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation()
            },
            "installed_packages": self._get_installed_packages()
        }
        
        # Check specific package availability
        packages_to_check = [
            "flask", 
            "openai", 
            "psutil"
        ]
        
        for package in packages_to_check:
            try:
                importlib.metadata.version(package)
                dependencies[package] = {
                    "installed": True,
                    "version": self._get_package_version(package)
                }
            except importlib.metadata.PackageNotFoundError:
                dependencies[package] = {
                    "installed": False,
                    "version": None
                }
        
        return dependencies

    def _get_installed_packages(self):
        """
        Get list of installed packages
        
        Returns:
        List of installed package names
        """
        try:
            return [dist.metadata['Name'] for dist in importlib.metadata.distributions()]
        except Exception as e:
            self.logger.warning(f"Could not retrieve installed packages: {e}")
            return []

    def _get_package_version(self, package_name):
        """
        Get version of a specific package
        
        Args:
            package_name (str): Name of the package
        
        Returns:
        Package version or None
        """
        try:
            return importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            return None

def health_check():
    """
    Utility function to perform a health check
    
    Returns:
    Dict with comprehensive health status
    """
    health_service = HealthCheckService()
    return health_service.perform_checks()
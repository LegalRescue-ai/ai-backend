import platform
import logging
import os
import sys
import time
import threading
import multiprocessing
import importlib.metadata
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import json

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

class ComponentStatus(Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"

@dataclass
class HealthMetric:
    name: str
    value: float
    unit: str
    status: ComponentStatus
    threshold_warning: float
    threshold_critical: float
    message: str = ""

@dataclass
class ComponentHealth:
    name: str
    status: ComponentStatus
    metrics: List[HealthMetric]
    last_check: datetime
    error_message: Optional[str] = None

@dataclass
class SystemHealth:
    overall_status: HealthStatus
    timestamp: datetime
    components: Dict[str, ComponentHealth]
    system_info: Dict[str, Any]
    uptime_seconds: float
    total_checks: int
    failed_checks: int

class HealthCheckService:
    def __init__(self, check_interval: int = 60):
        self.logger = logging.getLogger(__name__)
        self.check_interval = check_interval
        self.start_time = time.time()
        self.total_checks = 0
        self.failed_checks = 0
        self.last_health_check = None
        self.health_history = []
        self.max_history_size = 1000
        self.alert_thresholds = {
            'cpu_usage': {'warning': 80.0, 'critical': 95.0},
            'memory_usage': {'warning': 85.0, 'critical': 95.0},
            'disk_usage': {'warning': 80.0, 'critical': 90.0},
            'error_rate': {'warning': 5.0, 'critical': 10.0},
            'response_time': {'warning': 5.0, 'critical': 10.0}
        }
        self._lock = threading.Lock()
        self.application_metrics = {}
        
    def perform_comprehensive_check(self) -> SystemHealth:
        """
        Perform comprehensive system health check
        
        Returns:
            SystemHealth object with detailed status
        """
        try:
            check_start = time.time()
            self.total_checks += 1
            
            components = {}
            
            # Check system resources
            components['system_resources'] = self._check_system_resources()
            
            # Check dependencies
            components['dependencies'] = self._check_dependencies()
            
            # Check disk space
            components['disk_space'] = self._check_disk_space()
            
            # Check memory usage
            components['memory'] = self._check_memory()
            
            # Check CPU usage
            components['cpu'] = self._check_cpu()
            
            # Check application metrics if available
            if self.application_metrics:
                components['application'] = self._check_application_metrics()
            
            # Check Python environment
            components['python_environment'] = self._check_python_environment()
            
            # Determine overall status
            overall_status = self._determine_overall_status(components)
            
            # Create system health object
            system_health = SystemHealth(
                overall_status=overall_status,
                timestamp=datetime.utcnow(),
                components=components,
                system_info=self._get_system_info(),
                uptime_seconds=time.time() - self.start_time,
                total_checks=self.total_checks,
                failed_checks=self.failed_checks
            )
            
            # Update history
            self._update_health_history(system_health)
            
            # Update last check
            self.last_health_check = system_health
            
            self.logger.info(f"Health check completed in {time.time() - check_start:.2f}s - Status: {overall_status.value}")
            
            return system_health
            
        except Exception as e:
            self.failed_checks += 1
            self.logger.error(f"Health check failed: {e}")
            
            return SystemHealth(
                overall_status=HealthStatus.CRITICAL,
                timestamp=datetime.utcnow(),
                components={},
                system_info=self._get_system_info(),
                uptime_seconds=time.time() - self.start_time,
                total_checks=self.total_checks,
                failed_checks=self.failed_checks
            )
    
    def _check_system_resources(self) -> ComponentHealth:
        """Check system resource availability"""
        try:
            metrics = []
            
            # CPU cores
            cpu_cores = multiprocessing.cpu_count()
            metrics.append(HealthMetric(
                name="cpu_cores",
                value=cpu_cores,
                unit="cores",
                status=ComponentStatus.OPERATIONAL,
                threshold_warning=1,
                threshold_critical=1,
                message=f"{cpu_cores} CPU cores available"
            ))
            
            # Load average (Unix-like systems)
            if hasattr(os, 'getloadavg'):
                try:
                    load_avg = os.getloadavg()[0]
                    load_status = ComponentStatus.OPERATIONAL
                    if load_avg > cpu_cores * 0.8:
                        load_status = ComponentStatus.DEGRADED
                    if load_avg > cpu_cores * 1.2:
                        load_status = ComponentStatus.FAILED
                    
                    metrics.append(HealthMetric(
                        name="load_average",
                        value=load_avg,
                        unit="load",
                        status=load_status,
                        threshold_warning=cpu_cores * 0.8,
                        threshold_critical=cpu_cores * 1.2,
                        message=f"Load average: {load_avg:.2f}"
                    ))
                except OSError:
                    pass
            
            return ComponentHealth(
                name="system_resources",
                status=ComponentStatus.OPERATIONAL,
                metrics=metrics,
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                name="system_resources",
                status=ComponentStatus.FAILED,
                metrics=[],
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    def _check_dependencies(self) -> ComponentHealth:
        """Check critical dependencies"""
        try:
            metrics = []
            critical_packages = [
                'openai',
                'flask',
                'psutil'
            ]
            
            optional_packages = [
                'numpy',
                'pandas',
                'requests'
            ]
            
            failed_critical = 0
            failed_optional = 0
            
            # Check critical packages
            for package in critical_packages:
                try:
                    version = importlib.metadata.version(package)
                    metrics.append(HealthMetric(
                        name=f"package_{package}",
                        value=1.0,
                        unit="status",
                        status=ComponentStatus.OPERATIONAL,
                        threshold_warning=1.0,
                        threshold_critical=1.0,
                        message=f"{package} v{version} available"
                    ))
                except importlib.metadata.PackageNotFoundError:
                    failed_critical += 1
                    metrics.append(HealthMetric(
                        name=f"package_{package}",
                        value=0.0,
                        unit="status",
                        status=ComponentStatus.FAILED,
                        threshold_warning=1.0,
                        threshold_critical=1.0,
                        message=f"{package} not found"
                    ))
            
            # Check optional packages
            for package in optional_packages:
                try:
                    version = importlib.metadata.version(package)
                    metrics.append(HealthMetric(
                        name=f"package_{package}",
                        value=1.0,
                        unit="status",
                        status=ComponentStatus.OPERATIONAL,
                        threshold_warning=1.0,
                        threshold_critical=1.0,
                        message=f"{package} v{version} available"
                    ))
                except importlib.metadata.PackageNotFoundError:
                    failed_optional += 1
                    metrics.append(HealthMetric(
                        name=f"package_{package}",
                        value=0.0,
                        unit="status",
                        status=ComponentStatus.DEGRADED,
                        threshold_warning=1.0,
                        threshold_critical=1.0,
                        message=f"{package} not found (optional)"
                    ))
            
            # Determine overall dependency status
            if failed_critical > 0:
                status = ComponentStatus.FAILED
            elif failed_optional > 0:
                status = ComponentStatus.DEGRADED
            else:
                status = ComponentStatus.OPERATIONAL
            
            return ComponentHealth(
                name="dependencies",
                status=status,
                metrics=metrics,
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                name="dependencies",
                status=ComponentStatus.FAILED,
                metrics=[],
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    def _check_disk_space(self) -> ComponentHealth:
        """Check disk space usage"""
        try:
            metrics = []
            
            # Check root directory
            paths_to_check = ['/']
            if platform.system() == 'Windows':
                paths_to_check = ['C:\\']
            
            for path in paths_to_check:
                try:
                    if hasattr(os, 'statvfs'):
                        # Unix-like systems
                        statvfs = os.statvfs(path)
                        total = statvfs.f_frsize * statvfs.f_blocks
                        available = statvfs.f_frsize * statvfs.f_available
                        used = total - available
                        usage_percent = (used / total) * 100 if total > 0 else 0
                    else:
                        # Windows fallback
                        import shutil
                        total, used, free = shutil.disk_usage(path)
                        usage_percent = (used / total) * 100 if total > 0 else 0
                    
                    status = ComponentStatus.OPERATIONAL
                    if usage_percent > self.alert_thresholds['disk_usage']['warning']:
                        status = ComponentStatus.DEGRADED
                    if usage_percent > self.alert_thresholds['disk_usage']['critical']:
                        status = ComponentStatus.FAILED
                    
                    metrics.append(HealthMetric(
                        name=f"disk_usage_{path.replace('/', '_').replace('\\', '_')}",
                        value=usage_percent,
                        unit="percent",
                        status=status,
                        threshold_warning=self.alert_thresholds['disk_usage']['warning'],
                        threshold_critical=self.alert_thresholds['disk_usage']['critical'],
                        message=f"Disk usage: {usage_percent:.1f}%"
                    ))
                    
                except (OSError, ImportError):
                    continue
            
            overall_status = ComponentStatus.OPERATIONAL
            for metric in metrics:
                if metric.status == ComponentStatus.FAILED:
                    overall_status = ComponentStatus.FAILED
                    break
                elif metric.status == ComponentStatus.DEGRADED:
                    overall_status = ComponentStatus.DEGRADED
            
            return ComponentHealth(
                name="disk_space",
                status=overall_status,
                metrics=metrics,
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                name="disk_space",
                status=ComponentStatus.FAILED,
                metrics=[],
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    def _check_memory(self) -> ComponentHealth:
        """Check memory usage"""
        try:
            metrics = []
            
            try:
                import psutil
                memory = psutil.virtual_memory()
                usage_percent = memory.percent
                
                status = ComponentStatus.OPERATIONAL
                if usage_percent > self.alert_thresholds['memory_usage']['warning']:
                    status = ComponentStatus.DEGRADED
                if usage_percent > self.alert_thresholds['memory_usage']['critical']:
                    status = ComponentStatus.FAILED
                
                metrics.append(HealthMetric(
                    name="memory_usage",
                    value=usage_percent,
                    unit="percent",
                    status=status,
                    threshold_warning=self.alert_thresholds['memory_usage']['warning'],
                    threshold_critical=self.alert_thresholds['memory_usage']['critical'],
                    message=f"Memory usage: {usage_percent:.1f}%"
                ))
                
                # Available memory
                available_gb = memory.available / (1024**3)
                metrics.append(HealthMetric(
                    name="memory_available",
                    value=available_gb,
                    unit="GB",
                    status=ComponentStatus.OPERATIONAL,
                    threshold_warning=1.0,
                    threshold_critical=0.5,
                    message=f"Available memory: {available_gb:.1f} GB"
                ))
                
            except ImportError:
                # Fallback without psutil
                try:
                    total_memory = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
                    available_memory = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_AVPHYS_PAGES')
                    usage_percent = ((total_memory - available_memory) / total_memory) * 100
                    
                    status = ComponentStatus.OPERATIONAL
                    if usage_percent > self.alert_thresholds['memory_usage']['warning']:
                        status = ComponentStatus.DEGRADED
                    if usage_percent > self.alert_thresholds['memory_usage']['critical']:
                        status = ComponentStatus.FAILED
                    
                    metrics.append(HealthMetric(
                        name="memory_usage",
                        value=usage_percent,
                        unit="percent",
                        status=status,
                        threshold_warning=self.alert_thresholds['memory_usage']['warning'],
                        threshold_critical=self.alert_thresholds['memory_usage']['critical'],
                        message=f"Memory usage: {usage_percent:.1f}% (estimated)"
                    ))
                    
                except (AttributeError, ValueError):
                    metrics.append(HealthMetric(
                        name="memory_usage",
                        value=0.0,
                        unit="percent",
                        status=ComponentStatus.UNKNOWN,
                        threshold_warning=85.0,
                        threshold_critical=95.0,
                        message="Memory usage unavailable"
                    ))
            
            overall_status = ComponentStatus.OPERATIONAL
            for metric in metrics:
                if metric.status == ComponentStatus.FAILED:
                    overall_status = ComponentStatus.FAILED
                    break
                elif metric.status == ComponentStatus.DEGRADED:
                    overall_status = ComponentStatus.DEGRADED
            
            return ComponentHealth(
                name="memory",
                status=overall_status,
                metrics=metrics,
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                name="memory",
                status=ComponentStatus.FAILED,
                metrics=[],
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    def _check_cpu(self) -> ComponentHealth:
        """Check CPU usage"""
        try:
            metrics = []
            
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                
                status = ComponentStatus.OPERATIONAL
                if cpu_percent > self.alert_thresholds['cpu_usage']['warning']:
                    status = ComponentStatus.DEGRADED
                if cpu_percent > self.alert_thresholds['cpu_usage']['critical']:
                    status = ComponentStatus.FAILED
                
                metrics.append(HealthMetric(
                    name="cpu_usage",
                    value=cpu_percent,
                    unit="percent",
                    status=status,
                    threshold_warning=self.alert_thresholds['cpu_usage']['warning'],
                    threshold_critical=self.alert_thresholds['cpu_usage']['critical'],
                    message=f"CPU usage: {cpu_percent:.1f}%"
                ))
                
                # CPU count
                cpu_count = psutil.cpu_count()
                metrics.append(HealthMetric(
                    name="cpu_count",
                    value=cpu_count,
                    unit="cores",
                    status=ComponentStatus.OPERATIONAL,
                    threshold_warning=1,
                    threshold_critical=1,
                    message=f"CPU cores: {cpu_count}"
                ))
                
            except ImportError:
                # Fallback without psutil
                cpu_count = multiprocessing.cpu_count()
                metrics.append(HealthMetric(
                    name="cpu_count",
                    value=cpu_count,
                    unit="cores",
                    status=ComponentStatus.OPERATIONAL,
                    threshold_warning=1,
                    threshold_critical=1,
                    message=f"CPU cores: {cpu_count}"
                ))
                
                metrics.append(HealthMetric(
                    name="cpu_usage",
                    value=0.0,
                    unit="percent",
                    status=ComponentStatus.UNKNOWN,
                    threshold_warning=80.0,
                    threshold_critical=95.0,
                    message="CPU usage unavailable"
                ))
            
            overall_status = ComponentStatus.OPERATIONAL
            for metric in metrics:
                if metric.status == ComponentStatus.FAILED:
                    overall_status = ComponentStatus.FAILED
                    break
                elif metric.status == ComponentStatus.DEGRADED:
                    overall_status = ComponentStatus.DEGRADED
            
            return ComponentHealth(
                name="cpu",
                status=overall_status,
                metrics=metrics,
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                name="cpu",
                status=ComponentStatus.FAILED,
                metrics=[],
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    def _check_application_metrics(self) -> ComponentHealth:
        """Check application-specific metrics"""
        try:
            metrics = []
            
            # Error rate
            error_rate = self.application_metrics.get('error_rate', 0.0)
            error_status = ComponentStatus.OPERATIONAL
            if error_rate > self.alert_thresholds['error_rate']['warning']:
                error_status = ComponentStatus.DEGRADED
            if error_rate > self.alert_thresholds['error_rate']['critical']:
                error_status = ComponentStatus.FAILED
            
            metrics.append(HealthMetric(
                name="error_rate",
                value=error_rate,
                unit="percent",
                status=error_status,
                threshold_warning=self.alert_thresholds['error_rate']['warning'],
                threshold_critical=self.alert_thresholds['error_rate']['critical'],
                message=f"Error rate: {error_rate:.1f}%"
            ))
            
            # Response time
            response_time = self.application_metrics.get('avg_response_time', 0.0)
            response_status = ComponentStatus.OPERATIONAL
            if response_time > self.alert_thresholds['response_time']['warning']:
                response_status = ComponentStatus.DEGRADED
            if response_time > self.alert_thresholds['response_time']['critical']:
                response_status = ComponentStatus.FAILED
            
            metrics.append(HealthMetric(
                name="avg_response_time",
                value=response_time,
                unit="seconds",
                status=response_status,
                threshold_warning=self.alert_thresholds['response_time']['warning'],
                threshold_critical=self.alert_thresholds['response_time']['critical'],
                message=f"Average response time: {response_time:.2f}s"
            ))
            
            # Request count
            request_count = self.application_metrics.get('total_requests', 0)
            metrics.append(HealthMetric(
                name="total_requests",
                value=request_count,
                unit="requests",
                status=ComponentStatus.OPERATIONAL,
                threshold_warning=float('inf'),
                threshold_critical=float('inf'),
                message=f"Total requests: {request_count}"
            ))
            
            # Fallback usage
            fallback_rate = self.application_metrics.get('fallback_rate', 0.0)
            fallback_status = ComponentStatus.OPERATIONAL
            if fallback_rate > 30.0:
                fallback_status = ComponentStatus.DEGRADED
            if fallback_rate > 50.0:
                fallback_status = ComponentStatus.FAILED
            
            metrics.append(HealthMetric(
                name="fallback_rate",
                value=fallback_rate,
                unit="percent",
                status=fallback_status,
                threshold_warning=30.0,
                threshold_critical=50.0,
                message=f"Fallback rate: {fallback_rate:.1f}%"
            ))
            
            overall_status = ComponentStatus.OPERATIONAL
            for metric in metrics:
                if metric.status == ComponentStatus.FAILED:
                    overall_status = ComponentStatus.FAILED
                    break
                elif metric.status == ComponentStatus.DEGRADED:
                    overall_status = ComponentStatus.DEGRADED
            
            return ComponentHealth(
                name="application",
                status=overall_status,
                metrics=metrics,
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                name="application",
                status=ComponentStatus.FAILED,
                metrics=[],
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    def _check_python_environment(self) -> ComponentHealth:
        """Check Python environment"""
        try:
            metrics = []
            
            # Python version
            python_version = platform.python_version()
            python_major, python_minor = map(int, python_version.split('.')[:2])
            
            python_status = ComponentStatus.OPERATIONAL
            if python_major < 3 or (python_major == 3 and python_minor < 8):
                python_status = ComponentStatus.DEGRADED
            if python_major < 3 or (python_major == 3 and python_minor < 7):
                python_status = ComponentStatus.FAILED
            
            metrics.append(HealthMetric(
                name="python_version",
                value=float(f"{python_major}.{python_minor}"),
                unit="version",
                status=python_status,
                threshold_warning=3.8,
                threshold_critical=3.7,
                message=f"Python {python_version}"
            ))
            
            # Python implementation
            implementation = platform.python_implementation()
            impl_status = ComponentStatus.OPERATIONAL
            if implementation != 'CPython':
                impl_status = ComponentStatus.DEGRADED
            
            metrics.append(HealthMetric(
                name="python_implementation",
                value=1.0 if implementation == 'CPython' else 0.5,
                unit="status",
                status=impl_status,
                threshold_warning=1.0,
                threshold_critical=0.5,
                message=f"Python implementation: {implementation}"
            ))
            
            overall_status = ComponentStatus.OPERATIONAL
            for metric in metrics:
                if metric.status == ComponentStatus.FAILED:
                    overall_status = ComponentStatus.FAILED
                    break
                elif metric.status == ComponentStatus.DEGRADED:
                    overall_status = ComponentStatus.DEGRADED
            
            return ComponentHealth(
                name="python_environment",
                status=overall_status,
                metrics=metrics,
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                name="python_environment",
                status=ComponentStatus.FAILED,
                metrics=[],
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        return {
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "architecture": platform.architecture()[0],
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "hostname": platform.node()
        }
    
    def _determine_overall_status(self, components: Dict[str, ComponentHealth]) -> HealthStatus:
        """Determine overall system health status"""
        failed_components = []
        degraded_components = []
        
        for name, component in components.items():
            if component.status == ComponentStatus.FAILED:
                failed_components.append(name)
            elif component.status == ComponentStatus.DEGRADED:
                degraded_components.append(name)
        
        if failed_components:
            # Critical components that cause system failure
            critical_components = ['dependencies', 'python_environment']
            if any(comp in failed_components for comp in critical_components):
                return HealthStatus.CRITICAL
            else:
                return HealthStatus.UNHEALTHY
        elif degraded_components:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def _update_health_history(self, health: SystemHealth):
        """Update health check history"""
        with self._lock:
            self.health_history.append(health)
            if len(self.health_history) > self.max_history_size:
                self.health_history.pop(0)
    
    def update_application_metrics(self, metrics: Dict[str, float]):
        """Update application-specific metrics"""
        with self._lock:
            self.application_metrics.update(metrics)
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of current health status"""
        if not self.last_health_check:
            return {
                "status": "unknown",
                "message": "No health check performed yet"
            }
        
        return {
            "status": self.last_health_check.overall_status.value,
            "timestamp": self.last_health_check.timestamp.isoformat(),
            "uptime_seconds": self.last_health_check.uptime_seconds,
            "total_checks": self.total_checks,
            "failed_checks": self.failed_checks,
            "success_rate": ((self.total_checks - self.failed_checks) / self.total_checks * 100) if self.total_checks > 0 else 0,
            "component_count": len(self.last_health_check.components),
            "healthy_components": sum(1 for c in self.last_health_check.components.values() if c.status == ComponentStatus.OPERATIONAL),
            "degraded_components": sum(1 for c in self.last_health_check.components.values() if c.status == ComponentStatus.DEGRADED),
            "failed_components": sum(1 for c in self.last_health_check.components.values() if c.status == ComponentStatus.FAILED)
        }
    
    def get_detailed_report(self) -> Dict[str, Any]:
        """Get detailed health report"""
        if not self.last_health_check:
            return {"error": "No health check performed yet"}
        
        # Convert to dict for JSON serialization
        report = {
            "overall_status": self.last_health_check.overall_status.value,
            "timestamp": self.last_health_check.timestamp.isoformat(),
            "system_info": self.last_health_check.system_info,
            "uptime_seconds": self.last_health_check.uptime_seconds,
            "total_checks": self.total_checks,
            "failed_checks": self.failed_checks,
            "components": {}
        }
        
        for name, component in self.last_health_check.components.items():
            report["components"][name] = {
                "status": component.status.value,
                "last_check": component.last_check.isoformat(),
                "error_message": component.error_message,
                "metrics": [
                    {
                        "name": metric.name,
                        "value": metric.value,
                        "unit": metric.unit,
                        "status": metric.status.value,
                        "threshold_warning": metric.threshold_warning,
                        "threshold_critical": metric.threshold_critical,
                        "message": metric.message
                    }
                    for metric in component.metrics
                ]
            }
        
        return report
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current health alerts"""
        alerts = []
        
        if not self.last_health_check:
            return alerts
        
        for name, component in self.last_health_check.components.items():
            if component.status in [ComponentStatus.FAILED, ComponentStatus.DEGRADED]:
                severity = "critical" if component.status == ComponentStatus.FAILED else "warning"
                
                alerts.append({
                    "component": name,
                    "severity": severity,
                    "message": component.error_message or f"Component {name} is {component.status.value}",
                    "timestamp": component.last_check.isoformat()
                })
                
                # Add metric-specific alerts
                for metric in component.metrics:
                    if metric.status in [ComponentStatus.FAILED, ComponentStatus.DEGRADED]:
                        metric_severity = "critical" if metric.status == ComponentStatus.FAILED else "warning"
                        alerts.append({
                            "component": name,
                            "metric": metric.name,
                            "severity": metric_severity,
                            "message": metric.message,
                            "value": metric.value,
                            "threshold": metric.threshold_critical if metric.status == ComponentStatus.FAILED else metric.threshold_warning,
                            "timestamp": component.last_check.isoformat()
                        })
        
        return alerts
    
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        if not self.last_health_check:
            return False
        return self.last_health_check.overall_status == HealthStatus.HEALTHY
    
    def should_accept_requests(self) -> bool:
        """Determine if system should accept new requests"""
        if not self.last_health_check:
            return True  # Default to accepting requests
        
        # Don't accept requests if system is critical
        if self.last_health_check.overall_status == HealthStatus.CRITICAL:
            return False
        
        # Accept requests for healthy, degraded, or unhealthy states
        return True

def health_check() -> Dict[str, Any]:
    """
    Utility function to perform a quick health check
    
    Returns:
        Dict with health status
    """
    health_service = HealthCheckService()
    system_health = health_service.perform_comprehensive_check()
    return health_service.get_health_summary()

def detailed_health_check() -> Dict[str, Any]:
    """
    Utility function to perform a detailed health check
    
    Returns:
        Dict with detailed health information
    """
    health_service = HealthCheckService()
    system_health = health_service.perform_comprehensive_check()
    return health_service.get_detailed_report()

if __name__ == "__main__":
    # Example usage
    health_service = HealthCheckService()
    
    # Perform health check
    health = health_service.perform_comprehensive_check()
    
    # Print summary
    print("Health Check Summary:")
    print("-" * 50)
    summary = health_service.get_health_summary()
    print(f"Status: {summary['status']}")
    print(f"Uptime: {summary['uptime_seconds']:.0f} seconds")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Components: {summary['healthy_components']}/{summary['component_count']} healthy")
    
    # Print alerts
    alerts = health_service.get_alerts()
    if alerts:
        print(f"\nAlerts ({len(alerts)}):")
        for alert in alerts:
            print(f"  - {alert['severity'].upper()}: {alert['message']}")
    else:
        print("\nNo alerts")
    
    # Print detailed report
    print("\nDetailed Report:")
    print("-" * 50)
    detailed_report = health_service.get_detailed_report()
    print(json.dumps(detailed_report, indent=2, default=str))
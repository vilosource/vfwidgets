#!/usr/bin/env python3
"""
VFWidgets Theme System - Integration Test Scenarios
Task 25: Real-world integration test scenarios

This module provides comprehensive integration test scenarios that test
the theme system under real-world conditions with complex applications.
"""

from .complex_application import ComplexApplicationScenario
from .error_recovery import ErrorRecoveryScenario
from .migration import MigrationScenario
from .performance_stress import PerformanceStressScenario
from .plugin_integration import PluginIntegrationScenario
from .runner import IntegrationTestRunner
from .theme_switching import ThemeSwitchingScenario

__all__ = [
    'ComplexApplicationScenario',
    'ThemeSwitchingScenario',
    'ErrorRecoveryScenario',
    'MigrationScenario',
    'PluginIntegrationScenario',
    'PerformanceStressScenario',
    'IntegrationTestRunner'
]

# Version information
__version__ = '1.0.0'
__author__ = 'VFWidgets Theme System'
__description__ = 'Integration test scenarios for theme system validation'

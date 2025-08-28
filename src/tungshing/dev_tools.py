"""
Advanced development and debugging tools for TungShing.

This module provides comprehensive development utilities including:
- Interactive debugging tools
- Performance analysis and optimization
- Code quality metrics
- Automated testing utilities
- Deployment and CI/CD helpers
"""
from __future__ import annotations

import ast
import inspect
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import tempfile


class DevelopmentSuite:
    """
    Comprehensive development suite for TungShing.
    
    Provides tools for development, testing, profiling, and deployment.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize development suite.
        
        Args:
            project_root: Path to project root (auto-detected if None)
        """
        self.project_root = project_root or self._find_project_root()
        self.src_path = self.project_root / "src" / "tungshing"
        self.tests_path = self.project_root / "tests"
        
    def _find_project_root(self) -> Path:
        """Find project root directory."""
        current = Path(__file__).parent
        while current.parent != current:
            if (current / "pyproject.toml").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def code_quality_analysis(self) -> Dict[str, Any]:
        """
        Comprehensive code quality analysis.
        
        Returns:
            Dictionary with code quality metrics and suggestions
        """
        results = {
            'files_analyzed': 0,
            'total_lines': 0,
            'docstring_coverage': 0,
            'type_annotation_coverage': 0,
            'complexity_issues': [],
            'suggestions': []
        }
        
        python_files = list(self.src_path.glob("**/*.py"))
        results['files_analyzed'] = len(python_files)
        
        for file_path in python_files:
            file_analysis = self._analyze_file(file_path)
            results['total_lines'] += file_analysis['lines']
            
            # Aggregate metrics
            if file_analysis['has_docstring']:
                results['docstring_coverage'] += 1
            
            if file_analysis['type_annotations'] > 0:
                results['type_annotation_coverage'] += 1
            
            results['complexity_issues'].extend(file_analysis['complexity_issues'])
        
        # Calculate percentages
        if results['files_analyzed'] > 0:
            results['docstring_coverage'] = (results['docstring_coverage'] / results['files_analyzed']) * 100
            results['type_annotation_coverage'] = (results['type_annotation_coverage'] / results['files_analyzed']) * 100
        
        # Generate suggestions
        results['suggestions'] = self._generate_quality_suggestions(results)
        
        return results
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analysis = {
                'file': str(file_path),
                'lines': len(content.splitlines()),
                'has_docstring': False,
                'type_annotations': 0,
                'complexity_issues': []
            }
            
            # Check for module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr) and 
                isinstance(tree.body[0].value, ast.Constant) and 
                isinstance(tree.body[0].value.value, str)):
                analysis['has_docstring'] = True
            
            # Analyze functions and classes
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._analyze_function(node, analysis)
                elif isinstance(node, ast.ClassDef):
                    self._analyze_class(node, analysis)
            
            return analysis
            
        except Exception as e:
            return {
                'file': str(file_path),
                'error': str(e),
                'lines': 0,
                'has_docstring': False,
                'type_annotations': 0,
                'complexity_issues': []
            }
    
    def _analyze_function(self, node: ast.FunctionDef, analysis: Dict) -> None:
        """Analyze a function node."""
        # Count type annotations
        if node.returns:
            analysis['type_annotations'] += 1
        
        for arg in node.args.args:
            if arg.annotation:
                analysis['type_annotations'] += 1
        
        # Check complexity (simple metric: number of nested structures)
        complexity = self._calculate_complexity(node)
        if complexity > 10:  # Threshold for complex functions
            analysis['complexity_issues'].append({
                'type': 'complex_function',
                'name': node.name,
                'complexity': complexity,
                'line': node.lineno
            })
    
    def _analyze_class(self, node: ast.ClassDef, analysis: Dict) -> None:
        """Analyze a class node."""
        # Count methods
        method_count = sum(1 for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
        
        if method_count > 20:  # Threshold for large classes
            analysis['complexity_issues'].append({
                'type': 'large_class',
                'name': node.name,
                'method_count': method_count,
                'line': node.lineno
            })
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a node."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
        
        return complexity
    
    def _generate_quality_suggestions(self, results: Dict) -> List[str]:
        """Generate code quality suggestions."""
        suggestions = []
        
        if results['docstring_coverage'] < 80:
            suggestions.append(
                f"Low docstring coverage ({results['docstring_coverage']:.1f}%). "
                "Add docstrings to improve documentation."
            )
        
        if results['type_annotation_coverage'] < 90:
            suggestions.append(
                f"Low type annotation coverage ({results['type_annotation_coverage']:.1f}%). "
                "Add type hints to improve code clarity."
            )
        
        if results['complexity_issues']:
            suggestions.append(
                f"Found {len(results['complexity_issues'])} complexity issues. "
                "Consider refactoring complex functions and large classes."
            )
        
        if results['total_lines'] > 10000:
            suggestions.append(
                f"Large codebase ({results['total_lines']} lines). "
                "Consider modularization and architectural review."
            )
        
        return suggestions
    
    def performance_profiling_suite(self) -> Dict[str, Any]:
        """
        Run comprehensive performance profiling.
        
        Returns:
            Profiling results and optimization recommendations
        """
        from .profiling import get_profiler, profile_tungshing_creation, memory_benchmark
        from .memory_optimization import get_memory_optimizer
        
        profiler = get_profiler()
        results = {
            'timestamp': datetime.now().isoformat(),
            'environment': self._get_environment_info(),
            'benchmarks': {},
            'memory_analysis': {},
            'optimization_suggestions': []
        }
        
        # Basic TungShing creation benchmark
        test_dates = [
            datetime(2025, 1, 1, 12, 0),
            datetime(2025, 2, 4, 10, 42, 13),
            datetime(2025, 6, 21, 10, 42),
            datetime(2025, 12, 22, 9, 21),
        ]
        
        results['benchmarks']['creation'] = profile_tungshing_creation(
            iterations=100, 
            dates=test_dates
        )
        
        # Memory usage analysis
        results['memory_analysis'] = memory_benchmark(duration=5.0)
        
        # Cache effectiveness
        from .cache import get_cache_stats
        results['cache_stats'] = get_cache_stats()
        
        # Memory optimization analysis
        optimizer = get_memory_optimizer()
        results['memory_stats'] = {
            'total_objects': optimizer.get_memory_stats().total_objects,
            'memory_bytes': optimizer.get_memory_stats().memory_bytes,
            'cache_size': optimizer.get_memory_stats().cache_size
        }
        
        # Generate optimization suggestions
        results['optimization_suggestions'] = self._generate_performance_suggestions(results)
        
        return results
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """Get environment information for profiling context."""
        import platform
        
        env_info = {
            'python_version': sys.version,
            'platform': platform.platform(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
        }
        
        try:
            import psutil
            env_info.update({
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available
            })
        except ImportError:
            pass
        
        return env_info
    
    def _generate_performance_suggestions(self, results: Dict) -> List[str]:
        """Generate performance optimization suggestions."""
        suggestions = []
        
        # Analyze benchmark results
        if 'creation' in results['benchmarks']:
            creation_results = results['benchmarks']['creation']
            if 'bottlenecks' in creation_results:
                for bottleneck in creation_results['bottlenecks']:
                    if bottleneck['percentage'] > 30:
                        suggestions.append(
                            f"High time spent in {bottleneck['operation']} "
                            f"({bottleneck['percentage']:.1f}%) - consider optimization"
                        )
        
        # Analyze memory usage
        if 'memory_analysis' in results:
            memory_data = results['memory_analysis']
            if memory_data.get('memory_leaks'):
                suggestions.append("Potential memory leaks detected - review object lifecycle")
        
        # Analyze cache effectiveness
        if 'cache_stats' in results:
            cache_stats = results['cache_stats']
            if cache_stats['total_size'] == 0:
                suggestions.append("Cache not being used - verify caching configuration")
            elif cache_stats.get('total_accesses', 0) < cache_stats['total_size'] * 2:
                suggestions.append("Low cache hit ratio - review caching strategy")
        
        return suggestions
    
    def automated_testing_suite(self) -> Dict[str, Any]:
        """
        Run comprehensive automated testing.
        
        Returns:
            Test results and coverage information
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'test_results': {},
            'coverage': {},
            'performance_tests': {},
            'recommendations': []
        }
        
        # Run basic tests
        if self.tests_path.exists():
            test_result = self._run_pytest()
            results['test_results'] = test_result
        
        # Run performance tests
        perf_result = self._run_performance_tests()
        results['performance_tests'] = perf_result
        
        # Generate test coverage report
        coverage_result = self._generate_coverage_report()
        results['coverage'] = coverage_result
        
        # Generate recommendations
        results['recommendations'] = self._generate_testing_recommendations(results)
        
        return results
    
    def _run_pytest(self) -> Dict[str, Any]:
        """Run pytest and capture results."""
        try:
            cmd = [sys.executable, '-m', 'pytest', str(self.tests_path), '-v', '--tb=short']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            return {
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def _run_performance_tests(self) -> Dict[str, Any]:
        """Run performance-specific tests."""
        try:
            perf_test_file = self.tests_path / "test_performance.py"
            if perf_test_file.exists():
                cmd = [sys.executable, '-m', 'pytest', str(perf_test_file), '-v']
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
                
                return {
                    'exit_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'success': result.returncode == 0
                }
            else:
                return {
                    'message': 'Performance tests not found',
                    'success': False
                }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def _generate_coverage_report(self) -> Dict[str, Any]:
        """Generate test coverage report."""
        try:
            # Try to run coverage if available
            cmd = [sys.executable, '-m', 'coverage', 'run', '-m', 'pytest', str(self.tests_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                # Get coverage report
                cmd_report = [sys.executable, '-m', 'coverage', 'report']
                report_result = subprocess.run(cmd_report, capture_output=True, text=True, cwd=self.project_root)
                
                return {
                    'available': True,
                    'report': report_result.stdout,
                    'success': report_result.returncode == 0
                }
            else:
                return {
                    'available': False,
                    'message': 'Coverage tool not available or failed'
                }
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }
    
    def _generate_testing_recommendations(self, results: Dict) -> List[str]:
        """Generate testing recommendations."""
        recommendations = []
        
        if 'test_results' in results and not results['test_results'].get('success', False):
            recommendations.append("Some tests are failing - review test results and fix issues")
        
        if 'performance_tests' in results and not results['performance_tests'].get('success', False):
            recommendations.append("Performance tests failed - review performance requirements")
        
        if 'coverage' in results and not results['coverage'].get('available', False):
            recommendations.append("Install coverage tool: pip install coverage")
        
        return recommendations
    
    def deployment_checklist(self) -> Dict[str, Any]:
        """
        Generate deployment readiness checklist.
        
        Returns:
            Deployment checklist with status and recommendations
        """
        checklist = {
            'timestamp': datetime.now().isoformat(),
            'items': [],
            'overall_status': 'unknown',
            'blocking_issues': [],
            'warnings': [],
            'ready_for_deployment': False
        }
        
        # Check pyproject.toml
        pyproject_status = self._check_pyproject_toml()
        checklist['items'].append({
            'category': 'Configuration',
            'name': 'pyproject.toml',
            'status': pyproject_status['status'],
            'details': pyproject_status.get('issues', [])
        })
        
        # Check documentation
        docs_status = self._check_documentation()
        checklist['items'].append({
            'category': 'Documentation', 
            'name': 'README and docs',
            'status': docs_status['status'],
            'details': docs_status.get('issues', [])
        })
        
        # Check tests
        tests_status = self._check_tests_ready()
        checklist['items'].append({
            'category': 'Testing',
            'name': 'Test suite',
            'status': tests_status['status'],
            'details': tests_status.get('issues', [])
        })
        
        # Check security
        security_status = self._check_security()
        checklist['items'].append({
            'category': 'Security',
            'name': 'Security scan',
            'status': security_status['status'],
            'details': security_status.get('issues', [])
        })
        
        # Determine overall status
        statuses = [item['status'] for item in checklist['items']]
        if 'error' in statuses:
            checklist['overall_status'] = 'error'
            checklist['blocking_issues'] = [
                item for item in checklist['items'] if item['status'] == 'error'
            ]
        elif 'warning' in statuses:
            checklist['overall_status'] = 'warning'
            checklist['warnings'] = [
                item for item in checklist['items'] if item['status'] == 'warning'
            ]
        else:
            checklist['overall_status'] = 'ready'
        
        checklist['ready_for_deployment'] = checklist['overall_status'] in ['ready', 'warning']
        
        return checklist
    
    def _check_pyproject_toml(self) -> Dict[str, Any]:
        """Check pyproject.toml for deployment readiness."""
        pyproject_path = self.project_root / "pyproject.toml"
        
        if not pyproject_path.exists():
            return {
                'status': 'error',
                'issues': ['pyproject.toml not found']
            }
        
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                return {
                    'status': 'warning',
                    'issues': ['Cannot parse TOML - install tomli or use Python 3.11+']
                }
        
        try:
            with open(pyproject_path, 'rb') as f:
                config = tomllib.load(f)
            
            issues = []
            
            # Check required fields
            project = config.get('project', {})
            required_fields = ['name', 'version', 'description', 'authors']
            
            for field in required_fields:
                if field not in project:
                    issues.append(f'Missing required field: project.{field}')
            
            # Check dependencies
            if 'dependencies' not in project:
                issues.append('No dependencies specified')
            
            # Check build system
            if 'build-system' not in config:
                issues.append('No build-system specified')
            
            status = 'error' if issues else 'ready'
            return {
                'status': status,
                'issues': issues
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'issues': [f'Error parsing pyproject.toml: {str(e)}']
            }
    
    def _check_documentation(self) -> Dict[str, Any]:
        """Check documentation readiness."""
        issues = []
        
        # Check README
        readme_files = ['README.md', 'README.rst', 'README.txt']
        readme_exists = any((self.project_root / readme).exists() for readme in readme_files)
        
        if not readme_exists:
            issues.append('No README file found')
        
        # Check docs directory
        docs_path = self.project_root / "docs"
        if not docs_path.exists():
            issues.append('No docs directory found')
        
        # Check CHANGELOG
        changelog_files = ['CHANGELOG.md', 'CHANGES.md', 'HISTORY.md']
        changelog_exists = any((self.project_root / changelog).exists() for changelog in changelog_files)
        
        if not changelog_exists:
            issues.append('No CHANGELOG file found')
        
        status = 'warning' if issues else 'ready'
        return {
            'status': status,
            'issues': issues
        }
    
    def _check_tests_ready(self) -> Dict[str, Any]:
        """Check test readiness."""
        issues = []
        
        if not self.tests_path.exists():
            issues.append('No tests directory found')
            return {
                'status': 'error',
                'issues': issues
            }
        
        # Check for test files
        test_files = list(self.tests_path.glob("test_*.py"))
        if not test_files:
            issues.append('No test files found')
        
        # Try to run tests
        try:
            cmd = [sys.executable, '-m', 'pytest', '--collect-only', str(self.tests_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                issues.append('Tests cannot be collected - syntax errors or missing dependencies')
        except Exception as e:
            issues.append(f'Cannot run pytest: {str(e)}')
        
        status = 'error' if issues else 'ready'
        return {
            'status': status,
            'issues': issues
        }
    
    def _check_security(self) -> Dict[str, Any]:
        """Check security readiness."""
        issues = []
        
        # Check for common security files
        security_files = ['SECURITY.md', 'security.md']
        security_exists = any((self.project_root / sec_file).exists() for sec_file in security_files)
        
        if not security_exists:
            issues.append('No SECURITY.md file found')
        
        # Try to run bandit if available
        try:
            cmd = [sys.executable, '-m', 'bandit', '-r', str(self.src_path), '-f', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                try:
                    bandit_results = json.loads(result.stdout)
                    if bandit_results.get('results'):
                        issues.append(f"Bandit found {len(bandit_results['results'])} security issues")
                except json.JSONDecodeError:
                    pass
        except Exception:
            issues.append('Bandit security scanner not available - install with: pip install bandit[toml]')
        
        status = 'warning' if issues else 'ready'
        return {
            'status': status,
            'issues': issues
        }
    
    def generate_development_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate comprehensive development report.
        
        Args:
            output_file: Optional file path to save the report
            
        Returns:
            Report content as string
        """
        print("🔍 Analyzing code quality...")
        quality_results = self.code_quality_analysis()
        
        print("📊 Running performance profiling...")
        performance_results = self.performance_profiling_suite()
        
        print("🧪 Running automated tests...")
        testing_results = self.automated_testing_suite()
        
        print("🚀 Checking deployment readiness...")
        deployment_results = self.deployment_checklist()
        
        # Generate report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("TungShing Development Report")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().isoformat()}")
        report_lines.append(f"Project root: {self.project_root}")
        report_lines.append("")
        
        # Code Quality Section
        report_lines.append("📋 Code Quality Analysis")
        report_lines.append("-" * 40)
        report_lines.append(f"Files analyzed: {quality_results['files_analyzed']}")
        report_lines.append(f"Total lines: {quality_results['total_lines']:,}")
        report_lines.append(f"Docstring coverage: {quality_results['docstring_coverage']:.1f}%")
        report_lines.append(f"Type annotation coverage: {quality_results['type_annotation_coverage']:.1f}%")
        
        if quality_results['complexity_issues']:
            report_lines.append(f"Complexity issues: {len(quality_results['complexity_issues'])}")
            for issue in quality_results['complexity_issues'][:5]:  # Top 5
                report_lines.append(f"  - {issue['type']}: {issue['name']} (line {issue['line']})")
        
        if quality_results['suggestions']:
            report_lines.append("\nSuggestions:")
            for suggestion in quality_results['suggestions']:
                report_lines.append(f"  • {suggestion}")
        report_lines.append("")
        
        # Performance Section
        report_lines.append("⚡ Performance Analysis")
        report_lines.append("-" * 40)
        if 'creation' in performance_results['benchmarks']:
            creation_stats = performance_results['benchmarks']['creation']['summary']
            report_lines.append(f"Average operation time: {creation_stats['avg_time_per_operation']:.4f}s")
            report_lines.append(f"Total benchmark time: {creation_stats['total_time']:.2f}s")
        
        if performance_results['optimization_suggestions']:
            report_lines.append("\nOptimization suggestions:")
            for suggestion in performance_results['optimization_suggestions']:
                report_lines.append(f"  • {suggestion}")
        report_lines.append("")
        
        # Testing Section
        report_lines.append("🧪 Testing Analysis") 
        report_lines.append("-" * 40)
        if testing_results['test_results'].get('success'):
            report_lines.append("✓ Basic tests: PASSED")
        else:
            report_lines.append("✗ Basic tests: FAILED")
        
        if testing_results['performance_tests'].get('success'):
            report_lines.append("✓ Performance tests: PASSED")
        else:
            report_lines.append("✗ Performance tests: FAILED")
        
        if testing_results['coverage'].get('available'):
            report_lines.append("✓ Coverage report: AVAILABLE")
        else:
            report_lines.append("⚠ Coverage report: NOT AVAILABLE")
        
        if testing_results['recommendations']:
            report_lines.append("\nTesting recommendations:")
            for rec in testing_results['recommendations']:
                report_lines.append(f"  • {rec}")
        report_lines.append("")
        
        # Deployment Section
        report_lines.append("🚀 Deployment Readiness")
        report_lines.append("-" * 40)
        report_lines.append(f"Overall status: {deployment_results['overall_status'].upper()}")
        report_lines.append(f"Ready for deployment: {'YES' if deployment_results['ready_for_deployment'] else 'NO'}")
        
        if deployment_results['blocking_issues']:
            report_lines.append("\nBlocking issues:")
            for issue in deployment_results['blocking_issues']:
                report_lines.append(f"  ✗ {issue['name']}: {', '.join(issue['details'])}")
        
        if deployment_results['warnings']:
            report_lines.append("\nWarnings:")
            for warning in deployment_results['warnings']:
                report_lines.append(f"  ⚠ {warning['name']}: {', '.join(warning['details'])}")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        
        report_content = "\n".join(report_lines)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"📄 Report saved to: {output_file}")
        
        return report_content


def main():
    """Main CLI for development tools."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="TungShing Development Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--action',
        choices=['quality', 'performance', 'testing', 'deployment', 'full-report'],
        default='full-report',
        help='Type of analysis to run'
    )
    
    parser.add_argument(
        '--output',
        help='Output file for the report'
    )
    
    parser.add_argument(
        '--project-root',
        help='Project root directory (auto-detected if not specified)'
    )
    
    args = parser.parse_args()
    
    # Initialize development suite
    project_root = Path(args.project_root) if args.project_root else None
    dev_suite = DevelopmentSuite(project_root)
    
    print(f"🛠️  TungShing Development Suite")
    print(f"📁 Project root: {dev_suite.project_root}")
    print()
    
    if args.action == 'quality':
        results = dev_suite.code_quality_analysis()
        print(json.dumps(results, indent=2))
    
    elif args.action == 'performance':
        results = dev_suite.performance_profiling_suite()
        print(json.dumps(results, indent=2, default=str))
    
    elif args.action == 'testing':
        results = dev_suite.automated_testing_suite()
        print(json.dumps(results, indent=2))
    
    elif args.action == 'deployment':
        results = dev_suite.deployment_checklist()
        print(json.dumps(results, indent=2))
    
    elif args.action == 'full-report':
        report = dev_suite.generate_development_report(args.output)
        if not args.output:
            print(report)


if __name__ == "__main__":
    main()
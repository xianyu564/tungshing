"""
Advanced validation and error handling for TungShing.

This module provides comprehensive validation, detailed error messages,
and intelligent error recovery mechanisms to enhance user experience
and debugging capabilities.
"""
from __future__ import annotations

import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple, Union
from zoneinfo import ZoneInfo


class TungShingError(Exception):
    """Base exception class for TungShing-specific errors."""
    
    def __init__(self, message: str, error_code: str = None, suggestions: List[str] = None):
        """
        Initialize TungShing error.
        
        Args:
            message: Human-readable error description
            error_code: Unique error identifier for programmatic handling
            suggestions: List of suggested solutions
        """
        super().__init__(message)
        self.error_code = error_code or "TUNGSHING_ERROR"
        self.suggestions = suggestions or []
        self.message = message
    
    def __str__(self) -> str:
        """Format error with suggestions."""
        result = f"{self.message}"
        if self.suggestions:
            result += f"\n\nSuggestions:\n" + "\n".join(f"  • {s}" for s in self.suggestions)
        return result


class ValidationError(TungShingError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str = None, value: Any = None, **kwargs):
        """
        Initialize validation error.
        
        Args:
            message: Error description
            field: Name of the field that failed validation
            value: The invalid value that caused the error
        """
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.field = field
        self.value = value


class TimezoneError(TungShingError):
    """Raised when timezone-related operations fail."""
    pass


class CalculationError(TungShingError):
    """Raised when astronomical calculations fail."""
    pass


class DateRangeError(ValidationError):
    """Raised when date is outside supported range."""
    pass


class TungShingValidator:
    """
    Comprehensive validator for TungShing inputs and operations.
    
    Provides detailed validation with helpful error messages and suggestions
    for common mistakes and edge cases.
    """
    
    # Supported date range (sxtwl library limitations)
    MIN_YEAR = 1900
    MAX_YEAR = 2100
    
    # Common timezone aliases
    TIMEZONE_ALIASES = {
        'beijing': 'Asia/Shanghai',
        'hong_kong': 'Asia/Hong_Kong',
        'taipei': 'Asia/Taipei',
        'utc': 'UTC',
        'gmt': 'GMT',
        'est': 'US/Eastern',
        'pst': 'US/Pacific',
        'jst': 'Asia/Tokyo',
        'kst': 'Asia/Seoul'
    }
    
    @classmethod
    def validate_datetime(cls, dt: Any, field_name: str = "datetime") -> datetime:
        """
        Validate and normalize datetime input.
        
        Args:
            dt: Input datetime object or None
            field_name: Name of the field for error reporting
            
        Returns:
            Validated datetime object
            
        Raises:
            ValidationError: If datetime is invalid
            DateRangeError: If date is outside supported range
        """
        if dt is None:
            return datetime.now()
        
        if not isinstance(dt, datetime):
            if isinstance(dt, date):
                # Convert date to datetime at midnight
                dt = datetime.combine(dt, datetime.min.time())
            else:
                raise ValidationError(
                    f"Invalid {field_name}: expected datetime object, got {type(dt).__name__}",
                    field=field_name,
                    value=dt,
                    suggestions=[
                        "Use datetime.datetime(year, month, day, hour, minute)",
                        "Use datetime.now() for current time",
                        "Convert date objects using datetime.combine(date, time)"
                    ]
                )
        
        # Check date range
        year = dt.year
        if year < cls.MIN_YEAR or year > cls.MAX_YEAR:
            raise DateRangeError(
                f"Date {dt.date()} is outside supported range ({cls.MIN_YEAR}-{cls.MAX_YEAR})",
                field=field_name,
                value=dt,
                suggestions=[
                    f"Use dates between {cls.MIN_YEAR}-01-01 and {cls.MAX_YEAR}-12-31",
                    "Check if you meant a different year",
                    "For historical dates, consider using specialized libraries"
                ]
            )
        
        return dt
    
    @classmethod
    def validate_timezone(cls, tz: str, field_name: str = "timezone") -> str:
        """
        Validate and normalize timezone string.
        
        Args:
            tz: Timezone string
            field_name: Name of the field for error reporting
            
        Returns:
            Normalized timezone string
            
        Raises:
            TimezoneError: If timezone is invalid
        """
        if not isinstance(tz, str):
            raise TimezoneError(
                f"Invalid {field_name}: expected string, got {type(tz).__name__}",
                suggestions=[
                    "Use timezone strings like 'Asia/Shanghai', 'UTC', 'America/New_York'",
                    "See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
                ]
            )
        
        # Handle common aliases
        tz_lower = tz.lower().replace('-', '_').replace(' ', '_')
        if tz_lower in cls.TIMEZONE_ALIASES:
            tz = cls.TIMEZONE_ALIASES[tz_lower]
        
        # Validate timezone
        try:
            ZoneInfo(tz)
            return tz
        except Exception as e:
            # Suggest similar timezones
            suggestions = [
                "Use timezone strings like 'Asia/Shanghai', 'UTC', 'America/New_York'",
                "Check spelling - timezone names are case-sensitive"
            ]
            
            # Add specific suggestions based on input
            if 'china' in tz_lower or 'beijing' in tz_lower:
                suggestions.append("For China, use 'Asia/Shanghai'")
            elif 'hong' in tz_lower:
                suggestions.append("For Hong Kong, use 'Asia/Hong_Kong'")
            elif 'taiwan' in tz_lower or 'taipei' in tz_lower:
                suggestions.append("For Taiwan, use 'Asia/Taipei'")
            
            raise TimezoneError(
                f"Invalid timezone '{tz}': {str(e)}",
                suggestions=suggestions
            )
    
    @classmethod
    def validate_parameters(cls, **params) -> Dict[str, Any]:
        """
        Validate all TungShing parameters.
        
        Args:
            **params: Parameter dictionary to validate
            
        Returns:
            Dictionary of validated parameters
            
        Raises:
            ValidationError: If any parameter is invalid
        """
        validated = {}
        
        # Validate datetime
        if 'date' in params:
            validated['date'] = cls.validate_datetime(params['date'], 'date')
        
        # Validate timezones
        for tz_field in ['tz', 'rule_tz']:
            if tz_field in params:
                validated[tz_field] = cls.validate_timezone(params[tz_field], tz_field)
        
        # Validate other parameters
        for key, value in params.items():
            if key not in validated:
                validated[key] = value
        
        return validated
    
    @classmethod
    def check_calculation_dependencies(cls) -> None:
        """
        Check if all required dependencies are available.
        
        Raises:
            CalculationError: If required dependencies are missing
        """
        try:
            import cnlunar
            import sxtwl
        except ImportError as e:
            missing_module = str(e).split("'")[1] if "'" in str(e) else "unknown"
            raise CalculationError(
                f"Required dependency '{missing_module}' is not installed",
                error_code="MISSING_DEPENDENCY",
                suggestions=[
                    f"Install the missing module: pip install {missing_module}",
                    "Install all dependencies: pip install tungshing[dev]",
                    "Check your virtual environment activation"
                ]
            )
    
    @classmethod
    def validate_lunar_date(cls, year: int, month: int, day: int, is_leap: bool = False) -> None:
        """
        Validate lunar calendar date.
        
        Args:
            year: Lunar year
            month: Lunar month (1-12)
            day: Lunar day (1-30)
            is_leap: Whether this is a leap month
            
        Raises:
            ValidationError: If lunar date is invalid
        """
        if not isinstance(year, int) or year < cls.MIN_YEAR or year > cls.MAX_YEAR:
            raise ValidationError(
                f"Invalid lunar year {year}",
                field="lunar_year",
                value=year,
                suggestions=[f"Use years between {cls.MIN_YEAR} and {cls.MAX_YEAR}"]
            )
        
        if not isinstance(month, int) or month < 1 or month > 12:
            raise ValidationError(
                f"Invalid lunar month {month}",
                field="lunar_month", 
                value=month,
                suggestions=["Use months between 1 and 12"]
            )
        
        if not isinstance(day, int) or day < 1 or day > 30:
            raise ValidationError(
                f"Invalid lunar day {day}",
                field="lunar_day",
                value=day,
                suggestions=["Use days between 1 and 30"]
            )
    
    @classmethod
    def suggest_timezone_fix(cls, error_tz: str) -> List[str]:
        """
        Suggest timezone corrections based on common mistakes.
        
        Args:
            error_tz: The invalid timezone string
            
        Returns:
            List of suggested corrections
        """
        suggestions = []
        error_lower = error_tz.lower()
        
        # Common mistakes and their corrections
        corrections = {
            'gmt+8': 'Asia/Shanghai',
            'utc+8': 'Asia/Shanghai', 
            'cst': 'Asia/Shanghai',
            'china': 'Asia/Shanghai',
            'beijing': 'Asia/Shanghai',
            'shanghai': 'Asia/Shanghai',
            'hongkong': 'Asia/Hong_Kong',
            'hong_kong': 'Asia/Hong_Kong',
            'taiwan': 'Asia/Taipei',
            'taipei': 'Asia/Taipei',
            'tokyo': 'Asia/Tokyo',
            'seoul': 'Asia/Seoul',
        }
        
        for mistake, correction in corrections.items():
            if mistake in error_lower:
                suggestions.append(f"Did you mean '{correction}'?")
        
        if not suggestions:
            suggestions.extend([
                "Use IANA timezone database names like 'Asia/Shanghai'",
                "Check https://en.wikipedia.org/wiki/List_of_tz_database_time_zones",
                "Common timezones: UTC, Asia/Shanghai, Asia/Hong_Kong, America/New_York"
            ])
        
        return suggestions


def validate_input(func):
    """
    Decorator for automatic input validation.
    
    Validates function arguments and provides helpful error messages
    for common mistakes and edge cases.
    """
    def wrapper(*args, **kwargs):
        try:
            # Let the validator handle parameter validation
            if kwargs:
                validated_kwargs = TungShingValidator.validate_parameters(**kwargs)
                kwargs.update(validated_kwargs)
            
            # Check dependencies
            TungShingValidator.check_calculation_dependencies()
            
            return func(*args, **kwargs)
            
        except TungShingError:
            # Re-raise TungShing errors as-is
            raise
        except Exception as e:
            # Wrap other exceptions with helpful context
            raise CalculationError(
                f"Calculation failed: {str(e)}",
                error_code="CALCULATION_FAILED",
                suggestions=[
                    "Check your input parameters",
                    "Ensure all dependencies are properly installed",
                    "Try with a different date if the issue persists"
                ]
            )
    
    return wrapper


def safe_calculation(default_value=None):
    """
    Decorator for safe calculations with graceful error handling.
    
    Args:
        default_value: Value to return if calculation fails
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if isinstance(e, TungShingError):
                    raise
                
                # Log the error and return default value
                import warnings
                warnings.warn(
                    f"Calculation in {func.__name__} failed: {str(e)}. "
                    f"Returning default value: {default_value}",
                    UserWarning
                )
                return default_value
        
        return wrapper
    return decorator
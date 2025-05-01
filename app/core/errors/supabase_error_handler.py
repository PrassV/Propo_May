from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import logging
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SupabaseError(Exception):
    """Base exception for Supabase errors"""
    def __init__(self, code: str, message: str, details: Optional[str] = None, status_code: int = 500):
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code
        super().__init__(self.message)

class SupabaseErrorHandler:
    """Handler for Supabase-specific errors"""
    
    @staticmethod
    def map_error_code_to_status(code: str) -> int:
        """Map Supabase error codes to HTTP status codes"""
        # Common Supabase/PostgreSQL error codes
        code_map = {
            "PGRST204": status.HTTP_404_NOT_FOUND,  # Column not found
            "PGRST116": status.HTTP_400_BAD_REQUEST,  # Invalid JSON
            "PGRST101": status.HTTP_400_BAD_REQUEST,  # Malformed query
            "PGRST205": status.HTTP_404_NOT_FOUND,  # Table not found
            "23505": status.HTTP_409_CONFLICT,  # Unique violation
            "23503": status.HTTP_409_CONFLICT,  # Foreign key violation
            "23502": status.HTTP_400_BAD_REQUEST,  # Not null violation
            "22P02": status.HTTP_400_BAD_REQUEST,  # Invalid input syntax
            "42P01": status.HTTP_404_NOT_FOUND,  # Undefined table
            "42703": status.HTTP_400_BAD_REQUEST,  # Undefined column
            # Add more mappings as needed
        }
        
        return code_map.get(code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def extract_error_info(error_str: str) -> Dict[str, Any]:
        """Extract error information from Supabase error string"""
        try:
            # Try to parse as JSON
            if error_str.startswith("{") and error_str.endswith("}"):
                error_json = json.loads(error_str)
                return {
                    "code": error_json.get("code", "UNKNOWN"),
                    "message": error_json.get("message", "Unknown error"),
                    "details": error_json.get("details", None)
                }
            
            # Handle formatted error strings
            if ":" in error_str:
                parts = error_str.split(":", 1)
                return {
                    "code": parts[0].strip(),
                    "message": parts[1].strip(),
                    "details": None
                }
            
            # Default fallback
            return {
                "code": "UNKNOWN",
                "message": error_str,
                "details": None
            }
        except Exception as e:
            logger.error(f"Error parsing Supabase error: {e}")
            return {
                "code": "UNKNOWN",
                "message": error_str,
                "details": None
            }
    
    @staticmethod
    async def handle_exception(request: Request, exc: Exception) -> JSONResponse:
        """Handle Supabase exceptions and convert to appropriate HTTP responses"""
        # Handle SupabaseError exceptions
        if isinstance(exc, SupabaseError):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "detail": {
                        "code": exc.code,
                        "message": exc.message,
                        "details": exc.details
                    }
                }
            )
        
        # Handle general exceptions that might be from Supabase
        error_str = str(exc)
        if "PGRST" in error_str or any(code in error_str for code in ["23505", "23503", "23502", "22P02", "42P01", "42703"]):
            error_info = SupabaseErrorHandler.extract_error_info(error_str)
            status_code = SupabaseErrorHandler.map_error_code_to_status(error_info["code"])
            
            return JSONResponse(
                status_code=status_code,
                content={
                    "detail": {
                        "code": error_info["code"],
                        "message": error_info["message"],
                        "details": error_info["details"]
                    }
                }
            )
        
        # For standard HTTPExceptions, maintain their format
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail}
            )
        
        # For other exceptions, return a generic error
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"}
        ) 
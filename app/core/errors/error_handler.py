from fastapi import HTTPException, status
import logging
from typing import Any, Dict, Optional, Type

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base exception class for API errors"""
    def __init__(
        self, 
        code: str, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

def handle_repository_error(
    operation: str, 
    entity: str, 
    error: Exception, 
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
) -> None:
    """
    Standardized error handler for repository operations
    
    Args:
        operation: The operation being performed (e.g., "create", "update")
        entity: The entity being operated on (e.g., "user", "property")
        error: The exception that was raised
        status_code: HTTP status code to return
        
    Raises:
        HTTPException: Always raised with appropriate status code and detail
    """
    error_code = f"{operation.upper()}_{entity.upper()}_ERROR"
    error_message = f"Failed to {operation} {entity}: {str(error)}"
    
    logger.error(f"{error_code}: {error_message}", exc_info=error)
    
    raise HTTPException(
        status_code=status_code,
        detail=error_message
    )

def handle_validation_error(
    entity: str,
    field: str,
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> None:
    """
    Handle validation errors in a standardized way
    
    Args:
        entity: The entity being validated (e.g., "user", "property")
        field: The field that failed validation
        message: The validation error message
        status_code: HTTP status code to return
        
    Raises:
        HTTPException: Always raised with appropriate status code and detail
    """
    error_code = f"INVALID_{entity.upper()}_{field.upper()}"
    error_message = f"Validation error for {entity}.{field}: {message}"
    
    logger.warning(f"{error_code}: {error_message}")
    
    raise HTTPException(
        status_code=status_code,
        detail=error_message
    )

def handle_not_found_error(
    entity: str,
    identifier: Any
) -> None:
    """
    Handle not found errors in a standardized way
    
    Args:
        entity: The entity that wasn't found (e.g., "user", "property")
        identifier: The identifier that was used to lookup the entity
        
    Raises:
        HTTPException: Always raised with 404 status code
    """
    error_code = f"{entity.upper()}_NOT_FOUND"
    error_message = f"{entity} with identifier {identifier} not found"
    
    logger.info(f"{error_code}: {error_message}")
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=error_message
    )

def handle_permission_error(
    entity: str,
    operation: str,
    user_role: str
) -> None:
    """
    Handle permission errors in a standardized way
    
    Args:
        entity: The entity being accessed (e.g., "user", "property")
        operation: The operation being attempted (e.g., "create", "update")
        user_role: The role of the current user
        
    Raises:
        HTTPException: Always raised with 403 status code
    """
    error_code = f"PERMISSION_DENIED_{operation.upper()}_{entity.upper()}"
    error_message = f"User with role '{user_role}' does not have permission to {operation} {entity}"
    
    logger.warning(f"{error_code}: {error_message}")
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=error_message
    ) 
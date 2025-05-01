# Property Management Portal Architecture

This document outlines the architecture of the Property Management Portal application.

## Overview

The Property Management Portal is a FastAPI-based application that provides APIs for property management. The application follows a clean architecture pattern with the following layers:

- **API Layer**: Handles HTTP requests and responses
- **Service Layer**: Contains business logic
- **Repository Layer**: Handles data access
- **Model Layer**: Defines database models and schema

## Database Access

### Supabase

This application uses **Supabase** as its primary data storage and authentication mechanism. All database operations should go through the Supabase client or repository classes:

```python
from app.db.supabase import supabase
from app.db.repositories.user_repository_supabase import UserRepositorySupabase
```

### Deprecated SQLAlchemy

Previously, the application used SQLAlchemy for direct database access. This approach has been deprecated in favor of Supabase. You may still find references to SQLAlchemy in the codebase, but these are being phased out.

If you see imports like:

```python
from app.db.session import get_db
```

These are deprecated and should not be used in new code. The `get_db` function is still present for backward compatibility but will generate deprecation warnings.

## Authentication

Authentication is handled by Supabase Auth. The application uses Supabase JWT tokens for authentication and authorization. The auth flow is:

1. User registers or logs in through Supabase Auth
2. Supabase returns access and refresh tokens
3. Tokens are validated on subsequent requests

## API Structure

The API follows a RESTful pattern and is organized by resource:

- `/api/auth`: Authentication endpoints
- `/api/users`: User management
- `/api/properties`: Property management
- `/api/units`: Unit management

## Error Handling

The application uses standardized error handling through the `app/core/errors/error_handler.py` module. This provides consistent error responses across all endpoints.

## Environment Variables

The application requires the following environment variables:

### Required
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous API key 
- `JWT_SECRET`: Secret key for JWT operations

### Optional
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key for admin operations
- `ENVIRONMENT`: Application environment (development, production)
- `DEBUG`: Enable debug mode (True/False)
- `PORT`: Application port
- `APP_HOST`: Application host
- `BASE_URL`: Base URL for the application
- `RESEND_API_KEY`: API key for Resend email service

## Development Guidelines

1. **Use Supabase repositories**: All data access should go through the Supabase repositories
2. **Consistent error handling**: Use the error handling utilities in `app/core/errors/error_handler.py`
3. **Role-based access control**: Use the auth dependencies to enforce permissions
4. **FastAPI best practices**: Follow FastAPI best practices for endpoint implementation
5. **Avoid direct database access**: Never use SQLAlchemy or direct database access in new code 
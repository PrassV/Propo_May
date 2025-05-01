import logging
from app.db.supabase import supabase
from app.core.config.settings import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

async def configure_supabase_auth_urls() -> bool:
    """
    Configure Supabase Auth redirect URLs to use the proper frontend URL.
    This should be called during application startup.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # This requires admin/service role key
        if not settings.SUPABASE_SERVICE_ROLE_KEY:
            logger.warning("Cannot configure Supabase Auth URLs: No service role key provided")
            return False
            
        # Create new client with service role key for admin operations
        from supabase import create_client
        admin_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        
        # Build the redirect URLs with the frontend URL
        redirect_urls = {
            "email_confirm_url": f"{settings.FRONTEND_URL}/auth/confirm",
            "email_change_confirm_url": f"{settings.FRONTEND_URL}/auth/confirm-email-change",
            "reset_password_url": f"{settings.FRONTEND_URL}/auth/reset-password",
            "email_invite_url": f"{settings.FRONTEND_URL}/auth/invite",
        }
        
        # Update the Supabase Auth settings
        # Note: Actual API endpoint may vary based on Supabase version
        response = admin_client.auth.admin.update_config(redirect_urls)
        
        logger.info(f"Supabase Auth URLs configured to use {settings.FRONTEND_URL}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to configure Supabase Auth URLs: {str(e)}")
        return False

async def customize_email_templates() -> bool:
    """
    Customize the email templates used by Supabase Auth.
    This should be called during application startup.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # This requires admin/service role key
        if not settings.SUPABASE_SERVICE_ROLE_KEY:
            logger.warning("Cannot customize email templates: No service role key provided")
            return False
            
        # Create new client with service role key for admin operations
        from supabase import create_client
        admin_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        
        # Define custom email templates
        email_templates = {
            "confirmation": {
                "subject": f"{settings.PROJECT_NAME} - Confirm Your Email",
                "content": """
                <h2>Welcome to {PROJECT_NAME}!</h2>
                <p>Please confirm your email by clicking the link below:</p>
                <p><a href="{{ .ConfirmationURL }}">Confirm Email Address</a></p>
                <p>If you didn't sign up for an account, you can safely ignore this email.</p>
                """.replace("{PROJECT_NAME}", settings.PROJECT_NAME),
            },
            "invite": {
                "subject": f"{settings.PROJECT_NAME} - You've been invited",
                "content": """
                <h2>You've been invited to join {PROJECT_NAME}!</h2>
                <p>Please click the link below to accept the invitation:</p>
                <p><a href="{{ .ConfirmationURL }}">Accept Invitation</a></p>
                """.replace("{PROJECT_NAME}", settings.PROJECT_NAME),
            },
            "magic_link": {
                "subject": f"{settings.PROJECT_NAME} - Your Magic Link",
                "content": """
                <h2>Login to {PROJECT_NAME}</h2>
                <p>Click the link below to log in:</p>
                <p><a href="{{ .ConfirmationURL }}">Log In</a></p>
                <p>If you didn't request this email, you can safely ignore it.</p>
                """.replace("{PROJECT_NAME}", settings.PROJECT_NAME),
            },
            "recovery": {
                "subject": f"{settings.PROJECT_NAME} - Reset Your Password",
                "content": """
                <h2>Reset Your Password</h2>
                <p>Click the link below to reset your password:</p>
                <p><a href="{{ .ConfirmationURL }}">Reset Password</a></p>
                <p>If you didn't request a password reset, you can safely ignore this email.</p>
                """.replace("{PROJECT_NAME}", settings.PROJECT_NAME),
            },
        }
        
        # Update the email templates
        # Note: Actual API endpoint may vary based on Supabase version
        response = admin_client.auth.admin.update_email_templates(email_templates)
        
        logger.info("Supabase Auth email templates customized")
        return True
        
    except Exception as e:
        logger.error(f"Failed to customize email templates: {str(e)}")
        return False 
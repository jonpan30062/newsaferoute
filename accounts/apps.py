from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    
    def ready(self):
        """
        Run when Django starts up
        """
        # Import scheduler here to avoid AppRegistryNotReady error
        from .scheduler import start_scheduler
        
        # Only start scheduler in runserver, not in migrate, shell, etc.
        import sys
        if 'runserver' in sys.argv:
            try:
                start_scheduler()
                logger.info("Background scheduler initialized")
            except Exception as e:
                logger.error(f"Failed to start scheduler: {str(e)}")

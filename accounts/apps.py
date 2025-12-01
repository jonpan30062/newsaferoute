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
        # Only start scheduler in runserver, not in migrate, shell, etc.
        import sys
        if 'runserver' in sys.argv:
            try:
                # Import scheduler here to avoid AppRegistryNotReady error
                from .scheduler import start_scheduler
                scheduler = start_scheduler()
                if scheduler:
                    logger.info("Background scheduler initialized")
                else:
                    logger.warning("Scheduler not started - APScheduler may not be installed")
            except ImportError as e:
                logger.warning(f"Scheduler not available: {str(e)}. Install apscheduler to enable scheduled tasks.")
            except Exception as e:
                logger.error(f"Failed to start scheduler: {str(e)}")

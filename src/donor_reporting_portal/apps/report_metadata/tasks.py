from celery.utils.log import get_task_logger

from donor_reporting_portal.apps.report_metadata.synchronizers import GrantSynchronizer
from donor_reporting_portal.config.celery import app

logger = get_task_logger(__name__)


@app.task
def grant_sync():
    logger.info('Grant Sync Area Sync Started')
    GrantSynchronizer().sync()
    logger.info('Grant Sync Area Sync Ended')

"""
Notifier — sends Slack webhooks and email alerts for pipeline events.
"""

import json
import logging
import smtplib
from email.mime.text import MIMEText
import requests

logger = logging.getLogger(__name__)


class Notifier:
    def __init__(self, cfg):
        self.cfg = cfg

    def send_success(self, video_id: str, title: str):
        msg = f"✅ *New video uploaded!*\n*Title:* {title}\n*URL:* https://youtu.be/{video_id}"
        self._slack(msg)
        logger.info(f"Success notification sent for {video_id}")

    def send_failure(self, error: str):
        msg = f"❌ *Pipeline failed!*\n```{error[:500]}```"
        self._slack(msg)
        logger.warning("Failure notification sent")

    def send_spike_alert(self, views: int, ctr: float):
        msg = f"🚀 *Viral spike detected!*\nViews: {views:,} | CTR: {ctr:.1%}"
        self._slack(msg)

    def _slack(self, text: str):
        if not self.cfg or not self.cfg.SLACK_WEBHOOK_URL:
            return
        try:
            requests.post(
                self.cfg.SLACK_WEBHOOK_URL,
                data=json.dumps({"text": text}),
                headers={"Content-Type": "application/json"},
                timeout=5,
            )
        except Exception as e:
            logger.debug(f"Slack notification failed: {e}")

"""
Analytics Tracker — pulls YouTube Analytics metrics and writes daily CSV reports.
"""

import csv
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)


class AnalyticsTracker:
    def __init__(self, cfg):
        self.cfg = cfg

    def _get_service(self):
        creds = Credentials(
            token=None,
            refresh_token=self.cfg.YOUTUBE_REFRESH_TOKEN,
            client_id=self.cfg.YOUTUBE_CLIENT_ID,
            client_secret=self.cfg.YOUTUBE_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=["https://www.googleapis.com/auth/yt-analytics.readonly"],
        )
        creds.refresh(Request())
        return build("youtubeAnalytics", "v2", credentials=creds)

    def run(self):
        logger.info("📊 Fetching YouTube Analytics…")
        try:
            service = self._get_service()
            end = date.today()
            start = end - timedelta(days=7)

            result = service.reports().query(
                ids="channel==MINE",
                startDate=str(start),
                endDate=str(end),
                metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained,annotationClickThroughRate",
                dimensions="day",
                sort="day",
            ).execute()

            rows = result.get("rows", [])
            self._save_csv(rows)
            self._check_alerts(rows)

        except Exception as e:
            logger.error(f"Analytics fetch failed: {e}")

    def _save_csv(self, rows: list):
        Path("logs").mkdir(exist_ok=True)
        out = Path(f"logs/analytics_{date.today()}.csv")
        with open(out, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "views", "watch_minutes", "avg_duration", "subscribers", "ctr"])
            writer.writerows(rows)
        logger.info(f"Analytics saved → {out}")

    def _check_alerts(self, rows: list):
        from src.analytics.notifier import Notifier
        if not rows:
            return
        latest = rows[-1]
        views = int(latest[1]) if len(latest) > 1 else 0
        ctr = float(latest[4]) if len(latest) > 4 else 0
        if ctr > 0.08:
            logger.info(f"🚀 High CTR detected: {ctr:.1%} — sending alert")
            Notifier(None).send_spike_alert(views=views, ctr=ctr)

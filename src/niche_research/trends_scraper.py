"""
Niche & Trend Research — discovers trending topics via Google Trends + YouTube API.
"""

import logging
from dataclasses import dataclass
from pytrends.request import TrendReq
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)


@dataclass
class Topic:
    keyword: str
    trend_score: float
    competition: str        # low / medium / high
    monthly_searches: int
    top_video_views: int


class TrendsScraper:
    def __init__(self, cfg):
        self.cfg = cfg
        self.pytrends = TrendReq(hl="en-US", tz=0)

    def get_trending_topics(self, niche: str, limit: int = 10) -> list[Topic]:
        """Return top trending topics in the given niche."""
        logger.info(f"Fetching trends for niche: '{niche}'")

        # ── Google Trends: rising queries ──────────────────────────────────────
        self.pytrends.build_payload([niche], timeframe="now 7-d")
        related = self.pytrends.related_queries()
        rising = related.get(niche, {}).get("rising")

        keywords = []
        if rising is not None and not rising.empty:
            keywords = rising["query"].tolist()[:limit]
        else:
            keywords = [f"{niche} tutorial", f"best {niche} 2025", f"{niche} for beginners"]

        topics = []
        for kw in keywords[:limit]:
            score = self._score_keyword(kw)
            topics.append(score)

        topics.sort(key=lambda t: t.trend_score, reverse=True)
        logger.info(f"Found {len(topics)} trending topics")
        return topics

    def _score_keyword(self, keyword: str) -> Topic:
        """Score a keyword for viability."""
        yt = build("youtube", "v3", developerKey=self.cfg.YOUTUBE_DATA_API_KEY) \
            if hasattr(self.cfg, "YOUTUBE_DATA_API_KEY") else None

        top_views = 0
        if yt:
            try:
                res = yt.search().list(q=keyword, part="snippet", type="video",
                                       order="viewCount", maxResults=1).execute()
                if res.get("items"):
                    vid_id = res["items"][0]["id"]["videoId"]
                    stats = yt.videos().list(part="statistics", id=vid_id).execute()
                    top_views = int(stats["items"][0]["statistics"].get("viewCount", 0))
            except Exception as e:
                logger.debug(f"YouTube API call skipped: {e}")

        return Topic(
            keyword=keyword,
            trend_score=min(100.0, top_views / 1000),
            competition="medium",
            monthly_searches=top_views // 30,
            top_video_views=top_views,
        )

    def pick_best_topic(self, topics: list[Topic]) -> str:
        """Return the highest-scoring keyword."""
        best = max(topics, key=lambda t: t.trend_score)
        logger.info(f"Best topic selected: '{best.keyword}' (score={best.trend_score:.1f})")
        return best.keyword

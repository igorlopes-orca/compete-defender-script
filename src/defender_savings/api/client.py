import logging

import requests

from defender_savings.config import ORCA_API_URL, ORCA_QUERY_ENDPOINT

logger = logging.getLogger(__name__)


class OrcaClient:
    """Orca Security API client using requests."""

    def __init__(self, api_token: str) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        self._base_url = ORCA_API_URL
        self._query_url = f"{self._base_url}{ORCA_QUERY_ENDPOINT}"

    def query(
        self,
        models: list[str],
        select: list[str],
        limit: int = 100,
        with_filter: dict | None = None,
    ) -> list[dict]:
        """Execute a serving-layer query and return all results with pagination."""
        all_items: list[dict] = []
        start_at = 0

        while True:
            body: dict = {
                "query": {
                    "models": models,
                    "type": "object_set",
                },
                "limit": limit,
                "start_at_index": start_at,
                "select": select,
                "get_results_and_count": False,
                "full_graph_fetch": {"enabled": True},
                "max_tier": 2,
            }

            if with_filter:
                body["query"]["with"] = with_filter

            logger.debug("POST %s models=%s start_at=%d", self._query_url, models, start_at)
            response = self._session.post(self._query_url, json=body)
            response.raise_for_status()
            data = response.json()

            items = data.get("data", [])
            all_items.extend(items)

            if len(items) < limit:
                break
            start_at += limit

        logger.info("Fetched %d items for models %s", len(all_items), models)
        return all_items

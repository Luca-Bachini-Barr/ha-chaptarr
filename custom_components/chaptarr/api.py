"""Minimal async client for the Chaptarr (Readarr-style v1) API."""

from __future__ import annotations

from typing import Any

import aiohttp


class ChaptarrError(Exception):
    """Generic API error."""


class ChaptarrAuthError(ChaptarrError):
    """Invalid API key."""


class ChaptarrApi:
    def __init__(self, session: aiohttp.ClientSession, url: str, api_key: str) -> None:
        self._session = session
        self._base = url.rstrip("/") + "/api/v1/"
        self._headers = {"X-Api-Key": api_key}

    async def _get(self, path: str, **params: Any) -> Any:
        try:
            async with self._session.get(
                self._base + path,
                headers=self._headers,
                params={k: str(v).lower() if isinstance(v, bool) else v for k, v in params.items()},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status == 401:
                    raise ChaptarrAuthError
                resp.raise_for_status()
                return await resp.json()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise ChaptarrError(str(err)) from err

    async def status(self) -> dict:
        return await self._get("system/status")

    async def queue(self) -> list[dict]:
        data = await self._get("queue", pageSize=1000, includeBook=True, includeAuthor=True)
        return data.get("records", [])

    async def wanted_missing_total(self) -> int:
        data = await self._get("wanted/missing", pageSize=1)
        return data.get("totalRecords", 0)

    async def health(self) -> list[dict]:
        return await self._get("health")

    async def calendar(self, start: str, end: str) -> list[dict]:
        return await self._get("calendar", start=start, end=end, includeAuthor=True)

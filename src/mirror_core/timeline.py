"""TimeLine module: version management for persona evolution."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from mirror_core.models import PersonaVersion, VersionDiff


class TimelineManager:
    """Manages persona version history."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.timeline_dir = data_dir / "timeline"
        self.timeline_dir.mkdir(parents=True, exist_ok=True)
        self.versions_file = self.timeline_dir / "versions.json"
        if not self.versions_file.exists():
            self.versions_file.write_text("[]", encoding="utf-8")

    def create_version(
        self,
        version: str,
        soul_snapshot: str,
        faculty_diff: dict[str, str],
        body_additions: list[str],
        changelog: str,
    ) -> PersonaVersion:
        """Create a new persona version."""
        pv = PersonaVersion(
            version=version,
            timestamp=datetime.now(),
            soul_snapshot=soul_snapshot,
            faculty_diff=faculty_diff,
            body_additions=body_additions,
            changelog=changelog,
        )

        versions = self._load_versions_raw()
        versions.append(
            {
                "version": pv.version,
                "timestamp": pv.timestamp.isoformat(),
                "soul_snapshot": pv.soul_snapshot,
                "faculty_diff": pv.faculty_diff,
                "body_additions": pv.body_additions,
                "changelog": pv.changelog,
            }
        )
        self.versions_file.write_text(
            json.dumps(versions, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return pv

    def list_versions(self) -> list[PersonaVersion]:
        """List all versions in chronological order."""
        raw = self._load_versions_raw()
        return [self._parse_version(v) for v in raw]

    def get_current_version(self) -> Optional[str]:
        """Get the latest version string."""
        versions = self._load_versions_raw()
        if not versions:
            return None
        return versions[-1]["version"]

    def get_version(self, version: str) -> Optional[PersonaVersion]:
        """Get a specific version."""
        raw = self._load_versions_raw()
        for v in raw:
            if v["version"] == version:
                return self._parse_version(v)
        return None

    def compare(self, v1: str, v2: str) -> VersionDiff:
        """Compare two versions and return a diff."""
        pv1 = self.get_version(v1)
        pv2 = self.get_version(v2)

        soul_changes = []
        if pv1 and pv2:
            lines1 = set(pv1.soul_snapshot.strip().split("\n"))
            lines2 = set(pv2.soul_snapshot.strip().split("\n"))
            added = lines2 - lines1
            removed = lines1 - lines2
            for line in added:
                if line.strip():
                    soul_changes.append(f"+ {line.strip()}")
            for line in removed:
                if line.strip():
                    soul_changes.append(f"- {line.strip()}")

        faculty_changes: dict[str, list[str]] = {}
        if pv2:
            for domain, change in pv2.faculty_diff.items():
                faculty_changes[domain] = [change]

        body_count = len(pv2.body_additions) if pv2 else 0

        return VersionDiff(
            v1=v1,
            v2=v2,
            soul_changes=soul_changes,
            faculty_changes=faculty_changes,
            body_changes_count=body_count,
            summary=f"版本 {v1} → {v2}",
        )

    def _load_versions_raw(self) -> list[dict]:
        text = self.versions_file.read_text(encoding="utf-8")
        return json.loads(text) if text.strip() else []

    def _parse_version(self, raw: dict) -> PersonaVersion:
        try:
            ts = datetime.fromisoformat(raw["timestamp"])
        except (ValueError, TypeError):
            ts = datetime.now()

        return PersonaVersion(
            version=raw["version"],
            timestamp=ts,
            soul_snapshot=raw.get("soul_snapshot", ""),
            faculty_diff=raw.get("faculty_diff", {}),
            body_additions=raw.get("body_additions", []),
            changelog=raw.get("changelog", ""),
        )

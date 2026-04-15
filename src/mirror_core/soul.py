"""Soul layer: manages persona identity, values, style, and decision patterns."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from mirror_core.models import SoulData


class SoulManager:
    """Load, save, and version Soul layer data."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.soul_path = data_dir / "soul" / "soul.md"
        self.versions_dir = data_dir / "soul" / "versions"
        self.versions_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        version: str,
        identity: dict[str, str],
        values: list[str],
        language_style: dict[str, str],
        decision_patterns: list[str],
        personality_tags: dict[str, str] | None = None,
    ) -> None:
        """Save soul data and create a version snapshot."""
        now = datetime.now().isoformat()
        content = self._build_markdown(
            version=version,
            created_at=now,
            updated_at=now,
            identity=identity,
            values=values,
            language_style=language_style,
            decision_patterns=decision_patterns,
            personality_tags=personality_tags or {},
        )
        self.soul_path.parent.mkdir(parents=True, exist_ok=True)
        self.soul_path.write_text(content, encoding="utf-8")

        snapshot_path = self.versions_dir / f"soul_v{version}.md"
        shutil.copy2(self.soul_path, snapshot_path)

    def load(self, version: Optional[str] = None) -> Optional[SoulData]:
        """Load soul data. If version specified, load from version snapshot."""
        if version:
            path = self.versions_dir / f"soul_v{version}.md"
        else:
            path = self.soul_path

        if not path.exists():
            return None

        return self._parse_file(path)

    def get_raw_content(self, version: Optional[str] = None) -> Optional[str]:
        """Get raw markdown content for prompt injection."""
        if version:
            path = self.versions_dir / f"soul_v{version}.md"
        else:
            path = self.soul_path

        if not path.exists():
            return None

        return path.read_text(encoding="utf-8")

    def _build_markdown(
        self,
        version: str,
        created_at: str,
        updated_at: str,
        identity: dict[str, str],
        values: list[str],
        language_style: dict[str, str],
        decision_patterns: list[str],
        personality_tags: dict[str, str] | None = None,
    ) -> str:
        frontmatter = yaml.dump(
            {
                "version": version,
                "created_at": created_at,
                "updated_at": updated_at,
            },
            allow_unicode=True,
            default_flow_style=False,
        ).strip()

        lines = [f"---\n{frontmatter}\n---\n"]

        lines.append("# 身份认同")
        for k, v in identity.items():
            lines.append(f"- {k}：{v}")
        lines.append("")

        if personality_tags:
            lines.append("# 人格标签")
            for k, v in personality_tags.items():
                lines.append(f"- {k}：{v}")
            lines.append("")

        lines.append("# 核心价值观")
        for v in values:
            lines.append(f"- {v}")
        lines.append("")

        lines.append("# 语言风格")
        for k, v in language_style.items():
            lines.append(f"- {k}：{v}")
        lines.append("")

        lines.append("# 决策模式")
        for p in decision_patterns:
            lines.append(f"- {p}")
        lines.append("")

        return "\n".join(lines)

    def _parse_file(self, path: Path) -> SoulData:
        text = path.read_text(encoding="utf-8")

        parts = text.split("---", 2)
        frontmatter = yaml.safe_load(parts[1]) if len(parts) >= 3 else {}
        body = parts[2] if len(parts) >= 3 else text

        identity = {}
        values = []
        language_style = {}
        decision_patterns = []
        personality_tags = {}

        current_section = None
        for line in body.strip().split("\n"):
            line = line.strip()
            if line.startswith("# "):
                current_section = line[2:].strip()
            elif line.startswith("- ") and current_section:
                item = line[2:].strip()
                if current_section == "身份认同" and "：" in item:
                    k, v = item.split("：", 1)
                    identity[k] = v
                elif current_section == "人格标签" and "：" in item:
                    k, v = item.split("：", 1)
                    personality_tags[k] = v
                elif current_section == "核心价值观":
                    values.append(item)
                elif current_section == "语言风格" and "：" in item:
                    k, v = item.split("：", 1)
                    language_style[k] = v
                elif current_section == "决策模式":
                    decision_patterns.append(item)

        created_at_str = frontmatter.get("created_at", "")
        updated_at_str = frontmatter.get("updated_at", "")

        def parse_dt(s: str) -> datetime:
            if isinstance(s, datetime):
                return s
            try:
                return datetime.fromisoformat(str(s))
            except (ValueError, TypeError):
                return datetime.now()

        return SoulData(
            version=str(frontmatter.get("version", "1.0")),
            created_at=parse_dt(created_at_str),
            updated_at=parse_dt(updated_at_str),
            identity=identity,
            values=values,
            language_style=language_style,
            decision_patterns=decision_patterns,
            personality_tags=personality_tags,
        )

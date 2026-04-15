"""Faculty layer: manages professional expertise by domain."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from mirror_core.models import FacultyData


class FacultyManager:
    """Load, save, and list Faculty domain files."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.faculty_dir = data_dir / "faculty"
        self.faculty_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        domain: str,
        version: str,
        frameworks: dict[str, str],
        case_refs: list[str],
    ) -> None:
        """Save a faculty domain file."""
        content = self._build_markdown(domain, version, frameworks, case_refs)
        path = self.faculty_dir / f"{domain}.md"
        path.write_text(content, encoding="utf-8")

    def load(self, domain: str) -> Optional[FacultyData]:
        """Load a faculty domain file."""
        path = self.faculty_dir / f"{domain}.md"
        if not path.exists():
            return None
        return self._parse_file(path)

    def list_domains(self) -> list[str]:
        """List all available domains."""
        return [
            p.stem
            for p in self.faculty_dir.glob("*.md")
            if p.is_file()
        ]

    def get_raw_content(self, domain: str) -> Optional[str]:
        """Get raw markdown for prompt injection."""
        path = self.faculty_dir / f"{domain}.md"
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def _build_markdown(
        self,
        domain: str,
        version: str,
        frameworks: dict[str, str],
        case_refs: list[str],
    ) -> str:
        frontmatter = yaml.dump(
            {
                "domain": domain,
                "version": version,
                "last_updated": datetime.now().isoformat(),
            },
            allow_unicode=True,
            default_flow_style=False,
        ).strip()

        lines = [f"---\n{frontmatter}\n---\n"]

        lines.append("# 方法论")
        for name, desc in frameworks.items():
            lines.append(f"## {name}")
            lines.append(f"- {desc}")
            lines.append("")

        if case_refs:
            lines.append("# 案例库")
            for ref in case_refs:
                lines.append(f"- [{ref}]")
            lines.append("")

        return "\n".join(lines)

    def _parse_file(self, path: Path) -> FacultyData:
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        frontmatter = yaml.safe_load(parts[1]) if len(parts) >= 3 else {}
        body = parts[2] if len(parts) >= 3 else text

        frameworks = {}
        case_refs = []
        current_section = None
        current_framework_name = None

        for line in body.strip().split("\n"):
            line = line.strip()
            if line == "# 方法论":
                current_section = "frameworks"
            elif line == "# 案例库":
                current_section = "cases"
            elif line.startswith("## ") and current_section == "frameworks":
                current_framework_name = line[3:].strip()
            elif line.startswith("- ") and current_section == "frameworks" and current_framework_name:
                frameworks[current_framework_name] = line[2:].strip()
            elif line.startswith("- [") and current_section == "cases":
                ref = line[3:].rstrip("]").strip()
                case_refs.append(ref)

        last_updated_str = frontmatter.get("last_updated", "")
        if isinstance(last_updated_str, datetime):
            last_updated = last_updated_str
        else:
            try:
                last_updated = datetime.fromisoformat(str(last_updated_str))
            except (ValueError, TypeError):
                last_updated = datetime.now()

        return FacultyData(
            domain=frontmatter.get("domain", ""),
            version=str(frontmatter.get("version", "1.0")),
            last_updated=last_updated,
            frameworks=frameworks,
            case_refs=case_refs,
        )

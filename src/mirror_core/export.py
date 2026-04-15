"""Export module: export persona as a shareable Git repository."""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from mirror_core.soul import SoulManager
from mirror_core.faculty import FacultyManager


class ExportManager:
    """Exports persona data as an independent, shareable directory."""

    def export(
        self,
        data_dir: Path,
        output_dir: Path,
        name: str,
        include_knowledge: bool = False,
    ) -> Path:
        """Export persona data to a standalone directory."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Copy soul
        soul_src = data_dir / "soul"
        if soul_src.exists():
            shutil.copytree(soul_src, output_dir / "soul", dirs_exist_ok=True)

        # Copy faculty
        faculty_src = data_dir / "faculty"
        if faculty_src.exists():
            shutil.copytree(faculty_src, output_dir / "faculty", dirs_exist_ok=True)

        # Copy timeline
        timeline_src = data_dir / "timeline"
        if timeline_src.exists():
            shutil.copytree(timeline_src, output_dir / "timeline", dirs_exist_ok=True)

        # Optionally copy body (knowledge)
        if include_knowledge:
            body_src = data_dir / "body"
            if body_src.exists():
                shutil.copytree(body_src, output_dir / "body", dirs_exist_ok=True)

        # Generate README
        soul_mgr = SoulManager(data_dir=data_dir)
        soul_data = soul_mgr.load()
        faculty_mgr = FacultyManager(data_dir=data_dir)
        domains = faculty_mgr.list_domains()

        readme = self.generate_readme(name, soul_data, domains)
        (output_dir / "README.md").write_text(readme, encoding="utf-8")

        install = self.generate_install_guide(name)
        (output_dir / "INSTALL.md").write_text(install, encoding="utf-8")

        return output_dir

    def init_git(self, output_dir: Path, name: str) -> bool:
        """Initialize a Git repo in the output directory and make first commit."""
        try:
            subprocess.run(["git", "init"], cwd=output_dir, capture_output=True, check=True)
            subprocess.run(["git", "add", "."], cwd=output_dir, capture_output=True, check=True)
            subprocess.run(
                ["git", "commit", "-m", f"feat: initial export of {name}'s persona"],
                cwd=output_dir,
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def generate_readme(self, name: str, soul_data, domains: list[str]) -> str:
        """Generate a README for the exported persona."""
        lines = [f"# {name} 的数字分身\n"]

        if soul_data:
            tags = []
            if soul_data.personality_tags.get("MBTI"):
                tags.append(soul_data.personality_tags["MBTI"])
            if soul_data.personality_tags.get("星座"):
                tags.append(soul_data.personality_tags["星座"])
            role = soul_data.identity.get("role", "")
            if role:
                tags.append(role)
            if tags:
                lines.append(f"> {' | '.join(tags)}\n")

            lines.append("## 关于我\n")
            for k, v in soul_data.identity.items():
                lines.append(f"- **{k}**：{v}")
            lines.append("")

            if soul_data.values:
                lines.append("## 我的价值观\n")
                for v in soul_data.values:
                    lines.append(f"- {v}")
                lines.append("")

            if soul_data.language_style:
                lines.append("## 我的风格\n")
                for k, v in soul_data.language_style.items():
                    lines.append(f"- **{k}**：{v}")
                lines.append("")

        if domains:
            lines.append("## 我擅什么\n")
            for d in domains:
                lines.append(f"- {d}")
            lines.append("")

        lines.append("## 怎么跟我对话\n")
        lines.append("### Claude Code（推荐）\n")
        lines.append("```bash")
        lines.append(f"git clone <repo_url> ~/{name}-persona")
        lines.append(f"/mirror-core chat ~/{name}-persona")
        lines.append("```\n")
        lines.append("### CLI\n")
        lines.append("```bash")
        lines.append(f"git clone <repo_url> ~/{name}-persona")
        lines.append(f"cd mirror-core && python -m mirror_core.cli chat --data-dir ~/{name}-persona")
        lines.append("```\n")
        lines.append("---")
        lines.append("*由 [MirrorCore](https://github.com/chaosj1893-ai/mirror-core) 生成*\n")

        return "\n".join(lines)

    def generate_install_guide(self, name: str) -> str:
        """Generate an install guide."""
        return f"""# 安装指南

## 前置要求

- [MirrorCore](https://github.com/chaosj1893-ai/mirror-core) 已安装
- Claude Code（推荐）或 Python 3.11+

## 使用方式

### Claude Code

```bash
git clone <repo_url> ~/{name}-persona
/mirror-core chat ~/{name}-persona
```

### CLI

```bash
git clone <repo_url> ~/{name}-persona
cd ~/mirror-core
source .venv/bin/activate
python -m mirror_core.cli chat --data-dir ~/{name}-persona
```
"""

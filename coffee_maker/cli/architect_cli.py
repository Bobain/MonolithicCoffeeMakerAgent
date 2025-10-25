"""Architect CLI commands for spec creation.

This module provides CLI commands for architect's workflows:
- architect create-spec: Create technical specification for a priority
"""

import click
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.autonomous.spec_generator import SpecGenerator
from coffee_maker.autonomous.technical_spec_skill import TechnicalSpecSkill
from coffee_maker.cli.ai_service import AIService


@click.group()
def architect():
    """Architect agent CLI commands."""


@architect.command("create-spec")
@click.option("--priority", type=str, required=True, help="Priority number (e.g., 042 or 1.5)")
@click.option("--auto-approve", is_flag=True, help="Auto-approve spec creation without confirmation")
def create_spec(priority: str, auto_approve: bool):
    """Create technical specification for a priority.

    This command:
    1. Loads the priority from ROADMAP.md
    2. Generates a technical specification using AI
    3. Saves the spec to docs/architecture/specs/

    Example:
        architect create-spec --priority=042
        architect create-spec --priority=1.5 --auto-approve
    """
    try:
        # Load ROADMAP
        parser = RoadmapParser("docs/roadmap/ROADMAP.md")
        priorities = parser.get_priorities()

        # Find the priority
        matching_priority = None
        for p in priorities:
            if str(p["number"]) == priority or p["name"].endswith(priority):
                matching_priority = p
                break

        if not matching_priority:
            click.echo(f"❌ Priority {priority} not found in ROADMAP")
            return 1

        priority_name = matching_priority["name"]
        priority_title = matching_priority["title"]
        priority_content = matching_priority.get("content", "")

        click.echo(f"\n📋 Creating spec for: {priority_name} - {priority_title}\n")

        if not auto_approve:
            if not click.confirm("Continue with spec creation?"):
                click.echo("Cancelled")
                return 0

        # Generate spec using SpecGenerator
        click.echo("Generating technical specification (this may take 1-2 minutes)...\n")

        ai_service = AIService()
        generator = SpecGenerator(ai_service)
        user_story = f"{priority_name}: {priority_title}\n\n{priority_content}"

        spec = generator.generate_spec_from_user_story(
            user_story=user_story, feature_type="general", complexity="medium"
        )

        # Prepare spec identifiers (can't use .replace() or \n in f-strings)
        spec_number = priority.replace(".", "-")
        spec_title_slug = priority_title.lower().replace(" ", "-")[:40]
        spec_date = datetime.now().strftime("%Y-%m-%d")

        # Prepare spec content with defaults
        overview = spec.overview if hasattr(spec, "overview") else f"Technical specification for {priority_title}"
        requirements = spec.requirements if hasattr(spec, "requirements") else "- TBD"

        # Technical design with multiline default
        default_tech_design = "### Architecture\n\nTBD\n\n### Implementation\n\nTBD"
        technical_design = spec.technical_design if hasattr(spec, "technical_design") else default_tech_design

        total_hours = spec.total_hours if hasattr(spec, "total_hours") else None

        # Testing strategy with multiline default
        default_testing = "- Unit tests\n- Integration tests\n- Manual testing"
        testing_strategy = spec.testing_strategy if hasattr(spec, "testing_strategy") else default_testing

        # DoD with multiline default
        default_dod = "- [ ] All tests passing\n- [ ] Code reviewed\n- [ ] Documentation updated"
        definition_of_done = spec.definition_of_done if hasattr(spec, "definition_of_done") else default_dod

        # Format spec content
        spec_content = f"""# SPEC-{spec_number}: {priority_title}

**Priority**: {priority_name}
**Date**: {spec_date}
**Status**: Draft

## Overview

{overview}

## Requirements

{requirements}

## Technical Design

{technical_design}

## Effort Estimate

**Total**: {total_hours} hours

## Testing Strategy

{testing_strategy}

## Definition of Done

{definition_of_done}

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""

        # Create spec in database (with file backup)
        spec_skill = TechnicalSpecSkill(agent_name="architect")

        # Extract US number from priority (e.g., "US-104" or "042")
        try:
            # Try to extract US number from priority name
            if "US-" in priority_name:
                us_number = int(priority_name.split("US-")[1].split()[0])
            else:
                # Use priority number as fallback
                us_number = int(priority.replace(".", "").replace("-", ""))
        except (ValueError, IndexError):
            # If extraction fails, use a placeholder
            click.echo(f"⚠️  Warning: Could not extract US number from {priority_name}, using priority number")
            us_number = int(priority.replace(".", "").replace("-", ""))

        spec_id = spec_skill.create_monolithic_spec(
            us_number=us_number,
            title=priority_title,
            roadmap_item_id=priority_name,
            content=spec_content,
            estimated_hours=total_hours,
        )

        click.echo(f"✅ Spec created in database: {spec_id}")
        click.echo(f"   Type: monolithic")
        click.echo(f"   Content: {len(spec_content)} characters")
        click.echo(f"   Estimated hours: {total_hours}\n")

        return 0

    except Exception as e:
        click.echo(f"❌ Error creating spec: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    architect()

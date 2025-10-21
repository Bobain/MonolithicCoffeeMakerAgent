"""
Design System Skill for ux-design-expert.
Analyze Tailwind CSS usage, extract patterns, generate design tokens.
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict, Counter


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute design system generation."""
    scope = context.get("scope", "templates/")

    print(f"Analyzing design system: {scope}")

    # Step 1: Scan templates for Tailwind classes
    tailwind_classes = scan_templates(scope)

    # Step 2: Extract design tokens
    design_tokens = extract_design_tokens(tailwind_classes)

    # Step 3: Identify components
    components = identify_components(scope)

    # Step 4: Generate documentation
    report_path = generate_design_system_docs(design_tokens, components)

    # Step 5: Visualize relationships (optional - requires graphviz)
    try:
        visualize_components(components)
    except Exception as e:
        print(f"Warning: Could not create component graph: {e}")

    return {"design_tokens": design_tokens, "components": components, "report_path": str(report_path)}


def scan_templates(scope: str) -> List[str]:
    """Scan templates for Tailwind CSS classes."""
    tailwind_classes = []
    scope_path = Path(scope)

    if not scope_path.exists():
        print(f"Warning: {scope} does not exist, returning empty results")
        return tailwind_classes

    # Find all HTML/template files
    patterns = ["**/*.html", "**/*.jinja", "**/*.jinja2", "**/*.tsx", "**/*.jsx"]
    template_files = []

    for pattern in patterns:
        template_files.extend(scope_path.glob(pattern))

    # Extract class attributes
    class_pattern = re.compile(r'class="([^"]*)"')

    for file in template_files:
        try:
            content = file.read_text()
            matches = class_pattern.findall(content)
            for match in matches:
                # Split multiple classes
                classes = match.split()
                tailwind_classes.extend(classes)
        except Exception as e:
            print(f"Warning: Could not read {file}: {e}")

    return tailwind_classes


def extract_design_tokens(classes: List[str]) -> Dict[str, Any]:
    """Extract design tokens from Tailwind classes."""
    tokens = {
        "colors": defaultdict(int),
        "spacing": defaultdict(int),
        "typography": defaultdict(int),
        "layout": defaultdict(int),
        "effects": defaultdict(int),
    }

    for cls in classes:
        # Colors (bg-, text-, border-, etc.)
        if any(cls.startswith(prefix) for prefix in ["bg-", "text-", "border-"]):
            tokens["colors"][cls] += 1

        # Spacing (p-, m-, space-, gap-)
        elif any(cls.startswith(prefix) for prefix in ["p-", "m-", "space-", "gap-", "px-", "py-", "mx-", "my-"]):
            tokens["spacing"][cls] += 1

        # Typography (text-, font-, leading-, tracking-)
        elif any(cls.startswith(prefix) for prefix in ["font-", "leading-", "tracking-"]):
            tokens["typography"][cls] += 1

        # Layout (flex, grid, container, etc.)
        elif any(cls.startswith(prefix) for prefix in ["flex", "grid", "container", "col-", "row-"]):
            tokens["layout"][cls] += 1

        # Effects (shadow-, rounded-, opacity-)
        elif any(cls.startswith(prefix) for prefix in ["shadow-", "rounded-", "opacity-", "blur-"]):
            tokens["effects"][cls] += 1

    # Convert to regular dicts and get top 10 for each category
    return {category: dict(Counter(classes).most_common(10)) for category, classes in tokens.items()}


def identify_components(scope: str) -> List[str]:
    """Identify UI components from templates."""
    components = []
    scope_path = Path(scope)

    if not scope_path.exists():
        return components

    # Common component patterns
    component_patterns = {
        "button": r'<button|class="[^"]*btn',
        "card": r'<div[^>]*class="[^"]*card',
        "modal": r'<div[^>]*class="[^"]*modal',
        "navbar": r'<nav|class="[^"]*navbar',
        "form": r"<form",
        "input": r"<input",
        "table": r"<table",
        "alert": r'class="[^"]*alert',
    }

    # Find all HTML/template files
    patterns = ["**/*.html", "**/*.jinja", "**/*.jinja2", "**/*.tsx", "**/*.jsx"]
    template_files = []

    for pattern in patterns:
        template_files.extend(scope_path.glob(pattern))

    # Count component occurrences
    component_counts = defaultdict(int)

    for file in template_files:
        try:
            content = file.read_text()
            for component, pattern in component_patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    component_counts[component] += 1
        except Exception as e:
            print(f"Warning: Could not read {file}: {e}")

    # Return components sorted by usage
    components = sorted(component_counts.items(), key=lambda x: x[1], reverse=True)

    return [comp for comp, count in components]


def generate_design_system_docs(design_tokens: Dict[str, Any], components: List[str]) -> Path:
    """Generate design system documentation."""
    from datetime import datetime

    report = f"""# Design System Documentation

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Design Tokens

### Colors

Most frequently used color classes:

"""

    for cls, count in list(design_tokens.get("colors", {}).items())[:10]:
        report += f"- `{cls}` ({count} uses)\n"

    report += """

### Spacing

Most frequently used spacing classes:

"""

    for cls, count in list(design_tokens.get("spacing", {}).items())[:10]:
        report += f"- `{cls}` ({count} uses)\n"

    report += """

### Typography

Most frequently used typography classes:

"""

    for cls, count in list(design_tokens.get("typography", {}).items())[:10]:
        report += f"- `{cls}` ({count} uses)\n"

    report += """

## Components

Identified UI components:

"""

    for component in components:
        report += f"- **{component.capitalize()}**\n"

    report += """

## Recommendations

1. **Standardize Colors**: Create custom Tailwind color palette based on most-used colors
2. **Component Library**: Extract components into reusable library
3. **Design Tokens**: Define spacing/typography tokens in tailwind.config.js
4. **Consistency**: Remove rarely-used classes, enforce standard patterns

"""

    # Save report
    report_path = Path("evidence/design-system-report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)

    return report_path


def visualize_components(components: List[str]) -> None:
    """Create component dependency graph (requires graphviz)."""
    try:
        from graphviz import Digraph
    except ImportError:
        print("Warning: graphviz not installed, skipping visualization")
        return

    dot = Digraph(comment="Component Relationships")

    # Add component nodes
    for component in components:
        dot.node(component, component.capitalize())

    # Simple hierarchical structure (example)
    if "navbar" in components and "button" in components:
        dot.edge("navbar", "button")
    if "card" in components and "button" in components:
        dot.edge("card", "button")
    if "form" in components and "input" in components:
        dot.edge("form", "input")
    if "form" in components and "button" in components:
        dot.edge("form", "button")

    # Save graph
    output_path = Path("evidence/component-graph")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dot.render(str(output_path), format="png", cleanup=True)

    print(f"Component graph saved to {output_path}.png")


if __name__ == "__main__":
    context = json.load(sys.stdin)
    result = main(context)
    print(json.dumps(result, indent=2))

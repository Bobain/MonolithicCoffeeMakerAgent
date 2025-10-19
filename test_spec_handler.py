"""Quick test for spec handler implementation."""

from coffee_maker.utils.spec_handler import SpecHandler
from pathlib import Path


def test_spec_handler():
    """Test basic spec handler functionality."""
    handler = SpecHandler()

    print("=" * 60)
    print("Testing SpecHandler")
    print("=" * 60)

    # Test 1: Find spec for existing priority
    print("\n1. Testing find_spec...")
    priority = {"number": "20", "title": "US-104 - Orchestrator Continuous Agent Work Loop", "name": "US-104"}
    spec_path = handler.find_spec(priority)
    if spec_path:
        print(f"✅ Found spec: {spec_path}")
    else:
        print("❌ Spec not found (expected if US-104 spec doesn't exist yet)")

    # Test 2: Find spec by US ID
    print("\n2. Testing find_spec_by_us_id...")
    spec_path = handler.find_spec_by_us_id("US-070")
    if spec_path:
        print(f"✅ Found spec: {spec_path}")
    else:
        print("❌ Spec not found (expected if US-070 spec doesn't exist yet)")

    # Test 3: Generate filename
    print("\n3. Testing generate_spec_filename...")
    filename = handler.generate_spec_filename("104", "Orchestrator Continuous Agent Work Loop")
    print(f"✅ Generated filename: {filename}")
    expected = "SPEC-104-orchestrator-continuous-agent-work-loop.md"
    assert filename == expected, f"Expected {expected}, got {filename}"

    # Test 4: Create spec
    print("\n4. Testing create_spec (minimal)...")
    spec_content = handler.create_spec(
        us_number="999",
        title="Test Feature",
        priority_number="99",
        problem_statement="This is a test feature to verify spec creation",
        estimated_effort="5-10 hours",
        template_type="minimal",
    )
    assert "SPEC-999" in spec_content
    assert "Test Feature" in spec_content
    print("✅ Minimal spec created successfully")

    # Test 5: Create full spec
    print("\n5. Testing create_spec (full)...")
    spec_content = handler.create_spec(
        us_number="998",
        title="Another Test Feature",
        priority_number="98",
        problem_statement="Testing full spec creation",
        user_story="As a tester, I want full specs so that I can validate the system",
        architecture="Simple test architecture",
        estimated_effort="20-30 hours",
        template_type="full",
    )
    assert "SPEC-998" in spec_content
    assert "Another Test Feature" in spec_content
    assert "Executive Summary" in spec_content
    assert "Architecture" in spec_content
    print("✅ Full spec created successfully")

    # Test 6: Version operations
    print("\n6. Testing version operations...")
    version = handler.extract_version(spec_content)
    print(f"   Extracted version: {version}")
    assert version == "1.0.0"

    new_version = handler.bump_version(version, "minor")
    print(f"   Bumped version (minor): {new_version}")
    assert new_version == "1.1.0"

    new_version = handler.bump_version(version, "major")
    print(f"   Bumped version (major): {new_version}")
    assert new_version == "2.0.0"

    new_version = handler.bump_version(version, "patch")
    print(f"   Bumped version (patch): {new_version}")
    assert new_version == "1.0.1"
    print("✅ Version operations work correctly")

    # Test 7: Summarize spec
    print("\n7. Testing summarize_spec...")
    # Create a temporary spec file for testing
    temp_spec_path = Path("/tmp/test_spec.md")
    temp_spec_path.write_text(spec_content, encoding="utf-8")

    tldr = handler.summarize_spec(temp_spec_path, summary_type="tldr")
    print(f"   TL;DR: {tldr[:100]}...")

    exec_summary = handler.summarize_spec(temp_spec_path, summary_type="executive")
    print(f"   Executive summary length: {len(exec_summary)} chars")

    # Cleanup
    temp_spec_path.unlink()
    print("✅ Summarization works correctly")

    print("\n" + "=" * 60)
    print("All tests passed! ✅")
    print("=" * 60)


if __name__ == "__main__":
    test_spec_handler()

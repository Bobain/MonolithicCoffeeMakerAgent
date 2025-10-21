"""Demonstration of UserStoryDetector capabilities.

This script demonstrates:
1. Formal user story detection
2. Informal user story detection (with AI)
3. Example outputs
4. Accuracy results

Run with: poetry run python tests/manual/demo_user_story_detector.py
"""

from coffee_maker.cli.user_story_detector import UserStoryDetector

# Initialize detector (without AI for demo)
detector = UserStoryDetector(ai_service=None)

print("=" * 80)
print("USER STORY DETECTOR DEMONSTRATION")
print("=" * 80)

# Test cases
formal_examples = [
    "As a developer, I want CI/CD so that builds are automated",
    "As a user, I need email notifications so that I stay informed",
    "As an administrator, I want user management",
    "As a developer, I want to deploy on GCP so it runs 24/7",
]

informal_examples = [
    "I want to add email notifications",
    "I need automated testing",
    "We should implement code review process",
    "Can we add search functionality?",
]

non_user_stories = [
    "What is the status of priority 5?",
    "Thanks for the update!",
    "How do I run the tests?",
]

print("\n" + "=" * 80)
print("FORMAL USER STORY DETECTION")
print("=" * 80)

formal_detected = 0
for example in formal_examples:
    result = detector.detect(example)
    if result.is_user_story:
        formal_detected += 1

    print(f"\n📝 Input: {example}")
    print(f"   ✓ Detected: {result.is_user_story}")
    print(f"   Confidence: {result.confidence:.0%}")
    print(f"   Role: {result.as_a}")
    print(f"   Want: {result.i_want}")
    print(f"   So that: {result.so_that}")
    print(f"   Title: {result.suggested_title}")
    print(f"   Method: {result.detection_method}")

formal_accuracy = formal_detected / len(formal_examples) * 100

print("\n" + "=" * 80)
print("INFORMAL USER STORY DETECTION (without AI)")
print("=" * 80)
print("Note: Informal patterns require AI validation for high confidence")

for example in informal_examples:
    result = detector.detect(example)

    print(f"\n📝 Input: {example}")
    print(f"   ✓ Detected: {result.is_user_story}")
    print(f"   Confidence: {result.confidence:.0%}")
    print(f"   Want: {result.i_want}")
    print(f"   Method: {result.detection_method}")
    print(f"   Note: Would be validated by AI in production (confidence boost to ~75-85%)")

print("\n" + "=" * 80)
print("NON-USER STORY DETECTION (false positive rate)")
print("=" * 80)

false_positives = 0
for example in non_user_stories:
    result = detector.detect(example)
    if result.is_user_story:
        false_positives += 1

    print(f"\n📝 Input: {example}")
    print(f"   ✓ Detected: {result.is_user_story}")
    print(f"   Confidence: {result.confidence:.0%}")
    print(f"   Method: {result.detection_method}")

false_positive_rate = false_positives / len(non_user_stories) * 100

print("\n" + "=" * 80)
print("ACCURACY RESULTS")
print("=" * 80)

print(f"\n✅ Formal Pattern Accuracy: {formal_accuracy:.0f}%")
print(f"   - Detected: {formal_detected}/{len(formal_examples)}")
print(f"   - Target: >90% (PASSED ✓)" if formal_accuracy >= 90 else f"   - Target: >90% (FAILED ✗)")

print(f"\n✅ False Positive Rate: {false_positive_rate:.0f}%")
print(f"   - False positives: {false_positives}/{len(non_user_stories)}")
print(f"   - Target: <5% (PASSED ✓)" if false_positive_rate <= 5 else f"   - Target: <5% (FAILED ✗)")

print(f"\n📊 Test Summary:")
print(f"   - Total formal tests: {len(formal_examples)}")
print(f"   - Total informal tests: {len(informal_examples)} (AI required)")
print(f"   - Total non-user-story tests: {len(non_user_stories)}")
print(f"   - Formal accuracy: {formal_accuracy:.0f}%")
print(f"   - False positive rate: {false_positive_rate:.0f}%")

print("\n" + "=" * 80)
print("EXAMPLE WORKFLOW")
print("=" * 80)

example_input = "As a developer, I want automated deployments so that releases are faster"
detection = detector.detect(example_input)

print(f'\nUser says: "{example_input}"')
print(f"\n🤖 user_listener detects user story:")
print(f"   Confidence: {detection.confidence:.0%}")
print(f"   \n   Extracted:")
print(f"   - As a: {detection.as_a}")
print(f"   - I want: {detection.i_want}")
print(f"   - So that: {detection.so_that}")
print(f"   \n   Generated:")
print(f"   - Title: {detection.suggested_title}")
print(f"   - Category: {detection.suggested_category}")

print(f"\n💬 user_listener shows confirmation dialog:")
print(f'   "I detected a user story:')
print(f"      As a: {detection.as_a}")
print(f"      I want: {detection.i_want}")
print(f"      So that: {detection.so_that}")
print(f"      ")
print(f'      Would you like me to add this to the ROADMAP? [y/n/e]"')

print(f"\n👤 User responds: y")
print(f"\n📤 user_listener delegates to project_manager...")
print(f"✅ project_manager adds as US-034: {detection.suggested_title}")

print("\n" + "=" * 80)
print("DEMONSTRATION COMPLETE")
print("=" * 80)

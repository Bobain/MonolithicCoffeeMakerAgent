# .github/scripts/compare_versions.py
# co-author : Gemini 2.5 Pro Preview
import sys

from packaging.version import parse


def main():
    if len(sys.argv) != 3:
        print("::error::Usage: python compare_versions.py <pr_version> <main_version>", file=sys.stderr)
        sys.exit(1)

    pr_version_str = sys.argv[1]  # This is correct
    main_version_str = sys.argv[2]  # This is correct

    # This line was causing the problem in an earlier iteration if I recall correctly,
    # but the current script looks okay here based on what I provided.
    # Let's double check the print statement.
    print(
        f"Comparing PR version '{pr_version_str}' with main version '{main_version_str}'"
    )  # This uses the correct variables

    try:
        pr_v = parse(pr_version_str)
        main_v = parse(main_version_str)

        if pr_v > main_v:
            print(
                f"Success: PR version ({pr_version_str}) is greater than main version ({main_version_str})."
            )  # This uses the correct variables
            sys.exit(0)  # Success
        else:
            # This is where the error from the screenshot occurs:
            print(
                f"::error::Failure: PR version ({pr_version_str}) must be greater than main version ({main_version_str}).\n PLEASE GET SURE TO MERGE MAIN INTO YOUR PR as often as possible",
                file=sys.stderr,
            )  # This uses the correct variables
            sys.exit(1)  # Failure
    except Exception as e:
        print(f"::error::Invalid version format or comparison error: {e}", file=sys.stderr)  # Error message uses 'e'
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()

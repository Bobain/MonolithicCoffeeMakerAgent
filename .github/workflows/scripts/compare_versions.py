# .github/scripts/compare_versions.py
# co-author : Gemini 2.5 Pro Preview
import sys

from packaging.version import parse


def main():
    if len(sys.argv) != 3:
        print("::error::Usage: python compare_versions.py <pr_version> <main_version>", file=sys.stderr)
        sys.exit(1)

    pr_version_str = sys.argv[1]
    main_version_str = sys.argv[2]

    print(f"Comparing PR version '{pr_version_str}' with main version '{main_version_str}'")

    try:
        pr_v = parse(pr_version_str)
        main_v = parse(main_version_str)

        if pr_v > main_v:
            print(f"Success: PR version ({pr_v_str}) is greater than main version ({main_v_str}).")
            sys.exit(0)  # Success
        else:
            print(
                f"::error::Failure: PR version ({pr_v_str}) must be greater than main version ({main_v_str}).",
                file=sys.stderr,
            )
            sys.exit(1)  # Failure
    except Exception as e:
        print(f"::error::Invalid version format or comparison error: {e}", file=sys.stderr)
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()

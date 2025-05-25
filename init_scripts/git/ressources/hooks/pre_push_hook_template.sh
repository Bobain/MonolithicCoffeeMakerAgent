#!/bin/sh
#
# This hook is managed by git_init.py.
# It prevents direct pushes to the '{protected_branch_name}' branch.
# To bypass this hook for a specific push (e.g., an emergency hotfix), use:
#   git push --no-verify <remote> <branch>
#
# It's highly recommended to also set up branch protection rules
# on your remote repository (e.g., GitHub, GitLab) for true enforcement.

REMOTE="$1"
URL="$2"

PROTECTED_BRANCH="{protected_branch_name}"
BRANCH_REF="refs/heads/$PROTECTED_BRANCH"

while read local_ref local_sha remote_ref remote_sha; do
    if [ "$remote_ref" = "$BRANCH_REF" ]; then
        # Allow deleting the remote branch
        if [ "$local_sha" = "0000000000000000000000000000000000000000" ]; then
            exit 0
        fi

        echo "--------------------------------------------------------------------"
        echo "WARNING: Direct push to the protected branch '$PROTECTED_BRANCH' is discouraged."
        echo "Please use a feature branch and a Pull/Merge Request workflow."
        echo ""
        echo "If this is an emergency and you must push directly, you can bypass this hook with:"
        echo "  git push --no-verify $REMOTE $PROTECTED_BRANCH"
        echo "--------------------------------------------------------------------"
        exit 1 # Block the push
    fi
done

exit 0 # Allow other pushes

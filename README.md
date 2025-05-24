AI agent toy, written with agents AI.
No idea yet what it will do for real

# Unsolved issues

## git_init.py failure : Support for password authentication was removed on August 13, 2021 : GitHub Authentication for Pushing

When using git_init.py to push to a GitHub repository via HTTPS (e.g., `https://github.com/user/repo.git`), you will need to authenticate. GitHub no longer supports password authentication for Git operations over HTTPS since August 13, 2021.

**The recommended method is to use a Personal Access Token (PAT).**

### Using a Personal Access Token (PAT) - Recommended for HTTPS

A PAT is a more secure way to authenticate with GitHub for command-line operations or scripts.

**1. Generate a Personal Access Token on GitHub:**

   a. Go to your GitHub **Settings**. (Click your profile picture in the top-right corner, then "Settings").

   b. In the left sidebar, scroll down and click on **Developer settings**.

   c. In the left sidebar, click on **Personal access tokens**, then **Tokens (classic)**.
      *(While "Fine-grained tokens" exist, "Tokens (classic)" are often simpler for this direct script usage).*

   d. Click the **Generate new token** button (or **Generate new token (classic)**).

   e. Give your token a descriptive **Note** (e.g., "Git Initializer Script Token" or "My Laptop Git Access").

   f. Set an **Expiration** for your token. For security, avoid "No expiration" if possible. 30 or 90 days is a good start.

   g. Under **Select scopes**, you **must** check the **`repo`** scope. This scope grants full control of private and public repositories.
      ![GitHub PAT repo scope](https://i.stack.imgur.com/9N4yN.png) *(Illustrative image, UI might vary slightly)*

   h. Click **Generate token** at the bottom of the page.

**2. Copy Your Token:**

   *   **VERY IMPORTANT:** GitHub will only show you this token **ONCE**. Copy it immediately and store it in a safe place (like a password manager). If you lose it or navigate away from the page, you'll have to generate a new one.

**3. Use the Token with the Script (or Git):**

   When the script (or any Git command) prompts you for your password for `https://github.com`, do the following:
    Username for 'https://github.com': YOUR_GITHUB_USERNAME
    Password for 'https://YOUR_GITHUB_USERNAME@github.com': <PASTE_YOUR_PERSONAL_ACCESS_TOKEN_HERE>

**Do NOT enter your regular GitHub account password. Use the PAT you just generated.**

### Making it Easier: Credential Helpers

To avoid entering your PAT every time you push or pull, you can configure Git to use a credential helper. This will securely store your PAT after the first successful authentication.

*   **macOS:** Git can use the macOS Keychain. To enable this:
 ```bash
 git config --global credential.helper osxkeychain
 ```
 The first time you authenticate with your PAT, macOS should ask if you want to save it to your Keychain.

*   **Windows:** Git for Windows usually comes with "Git Credential Manager," which should handle this automatically. If not, you can configure it:
 ```bash
 git config --global credential.helper manager-core # or just 'manager' for older versions
 ```

*   **Linux:** You can use `libsecret` (if installed) or other helpers like `cache` or `store`:
 ```bash
 # For libsecret (recommended if available, integrates with GNOME Keyring, KWallet, etc.)
 git config --global credential.helper /usr/share/doc/git/contrib/credential/libsecret/git-credential-libsecret
 # Or to cache for a limited time (e.g., 1 hour)
 # git config --global credential.helper 'cache --timeout=3600'
 # Or to store in plain text (less secure, use with caution)
 # git config --global credential.helper store
 ```

### Alternative: Using SSH Keys

For a more seamless experience without needing tokens or passwords for each push/pull, consider setting up SSH keys with GitHub.

1.  [Generate a new SSH key and add it to the ssh-agent](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).
2.  [Add your SSH public key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
3.  Once set up, you can use the SSH URL for your repository with the script or when cloning/setting remotes:
 *   If the remote `origin` already exists with an HTTPS URL, change it:
     ```bash
     git remote set-url origin git@github.com:YOUR_USERNAME/YOUR_REPOSITORY.git
     ```
 *   When using this script, provide the SSH URL:
     ```bash
     python your_script_name.py -u git@github.com:YOUR_USERNAME/YOUR_REPOSITORY.git
     ```

By following these instructions, you should be able to authenticate successfully when the script attempts to push your newly initialized repository to GitHub.

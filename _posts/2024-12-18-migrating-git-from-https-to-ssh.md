---
layout: post
title: "Short Notes: Upgrade Your GitHub Workflow - Migrate from HTTPS to SSH"
modified:
categories: 
tags: [git, ssh, https]
description: "A step-by-step guide to transitioning from HTTPS to SSH for secure and seamless GitHub repository management."
thumbnail: 
giscus_comments: true
featured: False
share:
toc:
  beginning: true
date: 2024-12-21 12:16:00
---

If you're currently using HTTPS to interact with your GitHub repositories and want to switch to SSH for better security and convenience, this guide walks you through the migration process step-by-step.

---

## Why Switch to SSH?
SSH allows secure, password-less authentication using a key pair. Unlike HTTPS, you won’t need to repeatedly enter your GitHub credentials, making your workflow faster and more secure.

---

## Steps to Migrate from HTTPS to SSH

### 1. Generate a New SSH Key
First, create a new SSH key if you don’t already have one: `ssh-keygen -t rsa -b 4096 -C "your_email@example.com"`
- Replace `"your_email@example.com"` with your GitHub email.
- Follow the prompts to save the key to the default location and set a passcode (optional but recommended).

### 2. Add Your SSH Key to GitHub
Copy the public key to your clipboard: 
```
pbcopy < ~/.ssh/id_rsa.pub
```
If `pbcopy` is unavailable, use:
```
cat ~/.ssh/id_rsa.pub
```

Then, add the key to your GitHub account:
- Go to **Settings** > **SSH and GPG Keys** on GitHub.
- Click **New SSH Key**, paste the key, and save.

### 3. Remove Stored GitHub Credentials (Optional)
If you've used HTTPS before, your system might have cached your GitHub credentials. To avoid conflicts:
- On macOS or Linux: Look for credentials in your credential manager or `~/.git-credentials` and remove them.
- On Windows: Clear stored credentials via the Credential Manager.

This step is optional but helps ensure a clean transition to SSH.

### 4. Update the Remote URL
Convert your Git repository's remote URL from HTTPS to SSH:
```
git remote set-url origin <SSH url>
```

For example, if your HTTPS URL is: `https://github.com/username/repo_name.git`

Convert it to: `git@github.com:username/repo_name.git`

### 5. Verify the New Remote URL
Ensure your repository is now configured to use SSH:
```
git remote -v
```
The output should display the SSH URL.

### 6. Test Your SSH Connection
Run the following command to test the SSH connection:
```
ssh -T git@github.com
```

If everything is set up correctly, you'll see a message like:
Hi username! You've successfully authenticated, but GitHub does not provide shell access.

### 7. Enter Your SSH Key Passcode
The first time you interact with GitHub via SSH, you'll be prompted for your key's passcode if you set one.

---


Switching from HTTPS to SSH not only improves security but also streamlines your Git workflow by eliminating the need for repeated credential input. Follow these steps to make the transition smooth and hassle-free. 

Happy coding!

# CVE Intelligence Automation for Bug Bounty Hunters

This repository contains a powerful automation setup to help bug bounty hunters stay ahead of the curve. It uses a GitHub Action to daily analyze CVE data from this repository, identify high-value targets (CVEs with public exploits that are trending on social media), and send a report directly to a Discord channel.

## Features

- **Automated Daily Analysis**: Runs every day at 00:00 UTC automatically.
- **High-Value Target Identification**: Finds CVEs that have both a public PoC and are trending on social media (X).
- **Discord Notifications**: Delivers a clean, actionable report to your Discord server.
- **Easy Setup**: Requires minimal configuration to get started.

## Setup Instructions

To get the automation working, you need to connect it to your Discord server. This is done using a Discord Webhook. Follow these simple steps:

### Step 1: Create a Discord Webhook

1.  **Open Server Settings**: In your Discord server, click on the server name at the top-left and go to `Server Settings`.
2.  **Go to Integrations**: In the left-hand menu, find and click on `Integrations`.
3.  **Create Webhook**: Click the `Webhooks` button and then `New Webhook`.
4.  **Customize and Copy URL**:
    *   Give your webhook a name (e.g., "CVE Intelligence Bot").
    *   Choose the channel you want the reports to be sent to.
    *   Click `Copy Webhook URL`. Keep this URL safe!

![Discord Webhook Setup](https://i.imgur.com/8Vb3e1T.png)

### Step 2: Add Required Secrets to GitHub

Secrets are encrypted environment variables that allow you to store sensitive information, like your webhook URL and API tokens, securely in your repository. You need to add two secrets for this system to work.

1.  **Go to Repository Settings**: In this GitHub repository, click on the `Settings` tab.
2.  **Navigate to Secrets**: In the left-hand menu, go to `Secrets and variables` > `Actions`.
3.  **Create Secret 1: `DISCORD_WEBHOOK_URL`**
    *   Click `New repository secret`.
    *   **Name**: `DISCORD_WEBHOOK_URL`
    *   **Secret**: Paste the webhook URL you copied from Discord.
    *   Click `Add secret`.
4.  **Create Secret 2: `GH_PERSONAL_ACCESS_TOKEN`**
    *   Click `New repository secret` again.
    *   **Name**: `GH_PERSONAL_ACCESS_TOKEN`
    *   **Secret**: Paste your GitHub Personal Access Token (see instructions below).
    *   Click `Add secret`.

![GitHub Secret Setup](https://i.imgur.com/1G3q8hA.png)

#### How to Create a GitHub Personal Access Token (PAT)

The data collector script uses the GitHub API to find new CVEs. To avoid strict rate limits, you should use a Personal Access Token.

1.  Go to your GitHub **Settings**.
2.  Scroll down and click on **Developer settings**.
3.  Click on **Personal access tokens** > **Tokens (classic)**.
4.  Click **Generate new token** and select **Generate new token (classic)**.
5.  Give your token a **Note** (e.g., "CVE Data Collector").
6.  Set an **Expiration** date (e.g., 90 days).
7.  For **Select scopes**, you only need to check the `public_repo` permission under the `repo` section. This allows the script to read data from public repositories.
8.  Click **Generate token** and copy the token immediately. You won't be able to see it again.

## That's It!

The setup is complete. The GitHub Action will now run automatically at its scheduled time. If you want to test it immediately, you can go to the `Actions` tab in the repository, click on `Daily CVE Intelligence Report` in the sidebar, and use the `Run workflow` button.

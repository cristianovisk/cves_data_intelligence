import os
import pandas as pd
import requests
import sys

# --- Configuration ---
# File paths for the CSV data
EXPLOITS_CSV_PATH = "exploits/github/cves_github.csv"
SOCIAL_CSV_PATH = "social_media/x/tweet_cves_resumo.csv"
# Discord Webhook URL is read from GitHub Secrets
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_cves_with_exploits():
    """Reads the exploits CSV and returns a set of CVE IDs."""
    try:
        df = pd.read_csv(EXPLOITS_CSV_PATH, sep=';')
        # Assuming the CVE ID is in a column named 'cve' or 'CVE'
        # Let's find the correct column name case-insensitively
        cve_column = [col for col in df.columns if col.lower() == 'cve']
        if not cve_column:
            print(f"Error: No 'cve' column found in {EXPLOITS_CSV_PATH}")
            return set()
        return set(df[cve_column[0]].dropna().unique())
    except FileNotFoundError:
        print(f"Error: {EXPLOITS_CSV_PATH} not found.")
        return set()

def get_trending_cves():
    """Reads the social media CSV and returns a set of CVE IDs."""
    try:
        df = pd.read_csv(SOCIAL_CSV_PATH)
        # Assuming the CVE ID is in a column named 'cve'
        cve_column = [col for col in df.columns if col.lower() == 'cve']
        if not cve_column:
            print(f"Error: No 'cve' column found in {SOCIAL_CSV_PATH}")
            return set()
        return set(df[cve_column[0]].dropna().unique())
    except FileNotFoundError:
        print(f"Error: {SOCIAL_CSV_PATH} not found.")
        return set()

def send_to_discord(message):
    """Sends a formatted message to the configured Discord webhook."""
    if not DISCORD_WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL is not set. Cannot send message.")
        # To avoid failing the GitHub Action, we'll just print the message
        print("--- Message Content ---")
        print(message)
        print("-----------------------")
        return

    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        print("Successfully sent message to Discord.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Discord: {e}")
        sys.exit(1) # Exit with error code to make the GitHub Action fail

def main():
    """Main function to find valuable CVEs and report them."""
    print("Starting CVE hunter script...")
    cves_with_exploits = get_cves_with_exploits()
    trending_cves = get_trending_cves()

    if not cves_with_exploits and not trending_cves:
        print("No data found in CSV files. Exiting.")
        return

    # Find the intersection: CVEs that have exploits AND are trending
    valuable_cves = cves_with_exploits.intersection(trending_cves)

    if not valuable_cves:
        message = " M No new valuable CVEs found today. Keep hunting!"
        print(message)
    else:
        print(f"Found {len(valuable_cves)} valuable CVE(s).")
        # Format the message for Discord
        message_header = " M **Daily CVE Intelligence Report** M \n"
        message_header += "Found CVEs with public exploits that are currently trending. Time to hunt! M \n\n"

        cve_links = [f"- **{cve}**: `https://nvd.nist.gov/vuln/detail/{cve}`" for cve in sorted(list(valuable_cves))]

        message = message_header + "\n".join(cve_links)

    send_to_discord(message)
    print("Script finished.")

if __name__ == "__main__":
    main()

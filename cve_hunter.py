import os
import pandas as pd
import requests
import sys

# --- Configuration ---
NEW_CVES_FILE = "new_cves.txt"
SOCIAL_CSV_PATH = "social_media/x/tweet_cves_resumo.csv"
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_newly_discovered_cves_with_exploits():
    """Reads the list of new CVEs with exploits from the temporary file."""
    try:
        with open(NEW_CVES_FILE, "r") as f:
            cves = {line.strip() for line in f if line.strip()}
        print(f"Read {len(cves)} new CVEs with exploits from {NEW_CVES_FILE}.")
        return cves
    except FileNotFoundError:
        print(f"Warning: {NEW_CVES_FILE} not found. This can happen if no new exploits were discovered.")
        return set()

def get_trending_cves():
    """Reads the social media CSV and returns a set of trending CVE IDs."""
    try:
        df = pd.read_csv(SOCIAL_CSV_PATH)
        cve_column = [col for col in df.columns if col.lower() == 'cve']
        if not cve_column:
            print(f"Error: No 'cve' column found in {SOCIAL_CSV_PATH}")
            return set()
        # You might want to add logic here to define "trending" (e.g., based on audience_total)
        # For now, we consider any CVE mentioned in the file as "trending".
        trending_cves = set(df[cve_column[0]].dropna().unique())
        print(f"Found {len(trending_cves)} trending CVEs in {SOCIAL_CSV_PATH}.")
        return trending_cves
    except FileNotFoundError:
        print(f"Error: {SOCIAL_CSV_PATH} not found. Cannot check for trending CVEs.")
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
    """Finds and reports new CVEs that have exploits AND are trending on social media."""
    print("Starting CVE hunter script...")
    new_exploits = get_newly_discovered_cves_with_exploits()
    trending_cves = get_trending_cves()

    if not new_exploits:
        print("No new exploits were discovered in the last 24 hours. Exiting.")
        # No need to send a message, as the workflow already handles this.
        return

    # Find the intersection: CVEs that are new AND trending
    valuable_cves = new_exploits.intersection(trending_cves)

    if not valuable_cves:
        print("Found new exploits, but none are currently trending in the social media dataset.")
        message = f" M **Daily CVE Intelligence Summary** M \nFound {len(new_exploits)} new exploit(s), but none are currently trending. It might be worth checking them manually."
    else:
        print(f"Found {len(valuable_cves)} high-value CVE(s): New, Exploitable, AND Trending!")
        # Format the message for Discord
        message_header = " M **High-Value CVE Alert!** M \n"
        message_header += "Found newly discovered PoC exploits for the following trending CVEs. Time to hunt! M \n\n"

        cve_links = [f"- **{cve}**: `https://nvd.nist.gov/vuln/detail/{cve}`" for cve in sorted(list(valuable_cves))]

        message = message_header + "\n".join(cve_links)

    send_to_discord(message)
    print("Script finished.")

if __name__ == "__main__":
    main()

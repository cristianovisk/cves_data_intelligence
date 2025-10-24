import os
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- Configuration ---
GITHUB_TOKEN = os.getenv("GH_PERSONAL_ACCESS_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
EXPLOITS_CSV_PATH = "exploits/github/cves_github.csv"

def search_github_for_new_cves():
    """Searches GitHub for repositories mentioning CVEs created in the last 24 hours."""
    if not GITHUB_TOKEN:
        print("Warning: GH_PERSONAL_ACCESS_TOKEN is not set. Skipping data collection to avoid rate limiting.")
        return []

    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    # A more targeted query to find exploit PoCs
    query = f'"CVE-" created:>{yesterday} in:name,description,readme'

    url = f"https://api.github.com/search/repositories?q={query}&sort=updated&order=desc"

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        print(f"GitHub API search found {data.get('total_count', 0)} new potential CVE repositories.")
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        print(f"Error searching GitHub API: {e}")
        return []

def format_repo_data(repo):
    """Formats a GitHub repository item into a dictionary matching the CSV structure."""
    # This function needs to be carefully implemented to match the existing CSV columns.
    # Based on the previous analysis, the CSV has many columns. We'll fill the essential ones.
    owner = repo.get("owner", {})

    # Safely handle potential None values for name and description
    repo_name = repo.get("name") or ""
    repo_description = repo.get("description") or ""

    return {
        "cve": extract_cve_id(repo_name + " " + repo_description),
        "poc_github": "True",
        "full_name": repo.get("full_name"),
        "owner_login": owner.get("login"),
        "owner_id": owner.get("id"),
        "owner_html_url": owner.get("html_url"),
        "owner_avatar_url": owner.get("avatar_url"),
        "html_url": repo.get("html_url"),
        "description": repo.get("description", ""),
        "fork": repo.get("fork"),
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
        "pushed_at": repo.get("pushed_at"),
        "stargazers_count": repo.get("stargazers_count"),
        "watchers_count": repo.get("watchers_count"),
        "forks_count": repo.get("forks_count"),
        "visibility": repo.get("visibility"),
        # Fill other columns with defaults if not available from API
        "has_discussions": repo.get("has_discussions", False),
        "allow_forking": repo.get("allow_forking", True),
        "is_template": repo.get("is_template", False),
        "web_commit_signoff_required": repo.get("web_commit_signoff_required", False),
        "topics": str(repo.get("topics", [])),
        "forks": repo.get("forks"),
        "watchers": repo.get("watchers"),
        "score": repo.get("score", 0),
        "subscribers_count": repo.get("subscribers_count", 0) # Fallback if not present
    }

def extract_cve_id(text):
    """Extracts the first CVE ID found in a string."""
    import re
    if not text:
        return "N/A"
    # Regex to find CVE-YYYY-NNNN format
    match = re.search(r"CVE-\d{4}-\d{4,7}", text, re.IGNORECASE)
    return match.group(0).upper() if match else "N/A"

def update_csv(new_data):
    """
    Appends new, unique data to the exploits CSV file and sets an output for the GitHub Action.
    """
    new_cves_found = False
    newly_added_cves = []
    try:
        try:
            df_existing = pd.read_csv(EXPLOITS_CSV_PATH, sep=';')
            existing_repos = set(df_existing['full_name'].dropna())
        except FileNotFoundError:
            print(f"{EXPLOITS_CSV_PATH} not found. A new file will be created.")
            df_existing = pd.DataFrame()
            existing_repos = set()

        unique_new_data = [item for item in new_data if item['full_name'] not in existing_repos]

        if not unique_new_data:
            print("All collected data is already present in the CSV. No updates needed.")
        else:
            new_cves_found = True
            print(f"Adding {len(unique_new_data)} new unique entries to the CSV.")

            df_new = pd.DataFrame(unique_new_data)
            newly_added_cves = df_new['cve'].unique().tolist()

            if not df_existing.empty:
                df_new = df_new.reindex(columns=df_existing.columns)

            df_updated = pd.concat([df_existing, df_new], ignore_index=True)
            df_updated.to_csv(EXPLOITS_CSV_PATH, sep=';', index=False)
            print(f"Successfully updated {EXPLOITS_CSV_PATH}.")

            # Save the list of new CVEs to a temporary file for the next step
            with open("new_cves.txt", "w") as f:
                for cve in newly_added_cves:
                    f.write(f"{cve}\n")
            print(f"Saved {len(newly_added_cves)} new CVE IDs to new_cves.txt")

    except Exception as e:
        print(f"An error occurred while updating the CSV: {e}")

    # Set GitHub Actions output
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            print(f'new_cves_found={str(new_cves_found).lower()}', file=f)

def main():
    """Main function to collect new data and update the CSV."""
    print("Starting data collection script...")
    new_repos = search_github_for_new_cves()

    if not new_repos:
        print("No new repositories found. Exiting.")
        return

    new_data = [format_repo_data(repo) for repo in new_repos]

    # Filter out entries where no CVE could be extracted
    new_data = [item for item in new_data if item["cve"] != "N/A"]

    if not new_data:
        print("Found repositories, but could not extract valid CVE IDs. Exiting.")
        return

    print(f"Successfully formatted data for {len(new_data)} repositories.")

    update_csv(new_data)

    print("Data collection script finished.")


if __name__ == "__main__":
    main()

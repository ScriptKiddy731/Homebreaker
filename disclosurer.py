import requests
from urllib.parse import urlparse
import time
from colorama import init, Fore, Style
import random

init()

ASCII_ART = """
 _   _                      _                    _
| | | | ___  _ __ ___   ___| |__  _ __ ___  __ _| | _____ _ __
| |_| |/ _ \| '_ ` _ \ / _ \ '_ \| '__/ _ \/ _` | |/ / _ \ '__|
|  _  | (_) | | | | | |  __/ |_) | | |  __/ (_| |   <  __/ |
|_| |_|\___/|_| |_| |_|\___|_.__/|_|  \___|\__,_|_|\_\___|_|
"""

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1.2 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.70",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def extract_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain

def remove_duplicates(urls):
    unique_urls = set()
    cleaned_urls = []
    for url in urls:
        parsed = urlparse(url)
        clean_url = parsed.netloc + parsed.path.rstrip('/')
        clean_url = clean_url.lower()
        if clean_url not in unique_urls:
            unique_urls.add(clean_url)
            cleaned_urls.append(url)
    return cleaned_urls

def fetch_wayback_data(domain, max_retries=3, delay=2, batch_size=10000):
    url = "https://web.archive.org/cdx/search/cdx"
    offset = 0
    all_results = []

    while True:
        params = {
            "url": f"*.{domain}/*",
            "collapse": "urlkey",
            "output": "text",
            "fl": "original",
            "limit": batch_size,
            "offset": offset
        }

        headers = {
            "User-Agent": get_random_user_agent()
        }

        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                results = response.text.strip().split("\n")
                if not results or results == ['']:
                    return all_results
                all_results.extend(results)
                offset += batch_size
                break
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    print(f"{Fore.RED}Failed to fetch data after {max_retries} attempts: {e}{Style.RESET_ALL}")
                    return all_results
                time.sleep(delay)

def filter_interesting_findings(results):
    interesting_extensions = [
        '.xls', '.xml', '.xlsx', '.json', '.pdf', '.sql', '.doc', '.docx', '.pptx',
        '.txt', '.zip', '.tar.gz', '.tgz', '.bak', '.7z', '.rar', '.log', '.cache',
        '.secret', '.db', '.backup', '.yml', '.gz', '.config', '.csv', '.yaml', '.md',
        '.md5', '.exe', '.dll', '.bin', '.ini', '.bat', '.sh', '.tar', '.deb', '.rpm',
        '.iso', '.img', '.apk', '.msi', '.dmg', '.tmp', '.crt', '.pem', '.key', '.pub', '.asc'
    ]
    
    interesting_results = []
    for result in results:
        for ext in interesting_extensions:
            if result.lower().endswith(ext):
                interesting_results.append(result)
                break
    return interesting_results

def get_available_snapshots(file_url):
    snapshot_url = "https://web.archive.org/cdx/search/cdx"
    params = {
        "url": file_url,
        "output": "json",
        "fl": "timestamp,original"
    }
    headers = {
        "User-Agent": get_random_user_agent()
    }
    response = requests.get(snapshot_url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()[1:]
    return []

def download_file(file_url, timestamp):
    wayback_url = f"https://web.archive.org/web/{timestamp}id_/{file_url}"
    headers = {
        "User-Agent": get_random_user_agent()
    }
    response = requests.get(wayback_url, headers=headers, stream=True)
    if response.status_code == 200:
        file_name = file_url.split('/')[-1]
        with open(file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"{Fore.GREEN}File {file_name} downloaded successfully.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Failed to download the file.{Style.RESET_ALL}")

def save_results_to_txt(results, filename="interesting_results.txt"):
    with open(filename, "w") as file:
        for result in results:
            file.write(result + "\n")
    print(f"{Fore.GREEN}Results saved to {filename}.{Style.RESET_ALL}")

def main():
    print(f"{Fore.BLUE}{ASCII_ART}{Style.RESET_ALL}")
    print("Made by #731. Contact me in Telegram: @lmaoimsoweak. Much thanks for using my tools! <3")
    user_url = input(f"{Fore.GREEN}Enter URL: {Style.RESET_ALL}")
    domain = extract_domain(user_url)
    
    if domain:
        print(f"{Fore.BLUE}Extracted domain: {domain}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Fetching data from Wayback Machine... This may take a while.{Style.RESET_ALL}")
        
        wayback_data = fetch_wayback_data(domain)
        
        if wayback_data:
            wayback_data = remove_duplicates(wayback_data)
            print(f"{Fore.GREEN}Found {len(wayback_data)} unique results:{Style.RESET_ALL}")
            for result in wayback_data:
                print(f"{Fore.CYAN}{result}{Style.RESET_ALL}")
            
            interesting_findings = filter_interesting_findings(wayback_data)
            if interesting_findings:
                print(f"\n{Fore.MAGENTA}Potentially interesting findings:{Style.RESET_ALL}")
                for idx, finding in enumerate(interesting_findings):
                    print(f"{idx + 1}. {Fore.CYAN}{finding}{Style.RESET_ALL}")
                
                save_choice = input(f"{Fore.GREEN}Do you want to save the results? (yes/no): {Style.RESET_ALL}").strip().lower()
                if save_choice == "yes":
                    save_results_to_txt(interesting_findings)
                
                choice = input(f"{Fore.GREEN}Enter the file number to download (or 0 to exit): {Style.RESET_ALL}")
                if choice.isdigit() and 0 < int(choice) <= len(interesting_findings):
                    selected_file = interesting_findings[int(choice) - 1]
                    snapshots = get_available_snapshots(selected_file)
                    if snapshots:
                        print(f"{Fore.BLUE}Available snapshots for {selected_file}:{Style.RESET_ALL}")
                        for snap_idx, snap in enumerate(snapshots):
                            print(f"{snap_idx + 1}. {snap[0]} - {snap[1]}")
                        snap_choice = input(f"{Fore.GREEN}Enter the snapshot number to download (or 0 to exit): {Style.RESET_ALL}")
                        if snap_choice.isdigit() and 0 < int(snap_choice) <= len(snapshots):
                            selected_snapshot = snapshots[int(snap_choice) - 1]
                            download_file(selected_file, selected_snapshot[0])
                        else:
                            print(f"{Fore.YELLOW}Download canceled.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}No snapshots available for the selected file.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Download canceled.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}No potentially interesting findings detected.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Failed to fetch data from Wayback Machine.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Failed to extract domain from URL.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
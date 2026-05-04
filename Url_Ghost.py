
import time
import sys
import os
import random
import requests
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from colorama import Fore, Style, init

init(autoreset=True)

if not os.path.exists("results"):
    os.makedirs("results")

def matrix_typing(text, speed=0.04, color=Fore.GREEN):
    chars = "ABCDEFGHJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*"
    build_text = ""
    for char in text:
        for _ in range(2):
            temp_char = random.choice(chars)
            sys.stdout.write(f"\r{build_text}{color}{temp_char}")
            sys.stdout.flush()
            time.sleep(0.01)
        build_text += char
        sys.stdout.write(f"\r{build_text}")
        sys.stdout.flush()
    print()

def spinner_anim(message, duration=2):
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    while time.time() < end_time:
        for char in chars:
            sys.stdout.write(f"\r{Fore.CYAN}[{char}]{Fore.WHITE} {message}")
            sys.stdout.flush()
            time.sleep(0.08)
    sys.stdout.write(f"\r{Fore.GREEN}[+]{Fore.WHITE} {message} Done!          \n")

class GopherEngine:
    def __init__(self, target):
        self.target = target.rstrip('/')
        self.domain = urlparse(target).netloc
        self.found_links = set()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }

    def save_result(self, category, data):
        filename = f"results/{self.domain}_{category}.txt"
        with open(filename, "a") as f:
            f.write(data + "\n")

    def crawler(self):
        print(f"\n{Fore.CYAN}[*] Mapping Surface Endpoints...")
        try:
            with requests.Session() as s:
                s.headers.update(self.headers)
                r = s.get(self.target, timeout=10)
                soup = BeautifulSoup(r.text, 'html.parser')
                for tag in soup.find_all(['a', 'script', 'link'], href=True, src=True):
                    attr = 'href' if tag.name in ['a', 'link'] else 'src'
                    url = urljoin(self.target, tag.get(attr)).split('?')[0].split('#')[0]
                    if self.domain in url and url not in self.found_links:
                        print(f"{Fore.GREEN}[+] Found: {url}")
                        self.found_links.add(url)
                        self.save_result("crawler", url)
        except Exception as e:
            print(f"{Fore.RED}[-] Crawler Error: {e}")

    async def fetch_status(self, session, path):
        url = urljoin(self.target, path)
        try:
            async with session.get(url, timeout=4, allow_redirects=True) as response:
                if response.status == 200:
                    if str(response.url).rstrip('/') != self.target:
                        print(f"{Fore.GREEN}[!] VALID DIR: {url}")
                        self.save_result("fuzzer", url)
                elif response.status == 403:
                    print(f"{Fore.YELLOW}[*] FORBIDDEN: {url}")
        except: pass

    async def run_fuzzer(self, wordlist):
        print(f"\n{Fore.MAGENTA}[*] Launching Async Fuzzer (High Speed)...")
        conn = aiohttp.TCPConnector(limit=50)
        async with aiohttp.ClientSession(headers=self.headers, connector=conn) as session:
            tasks = [self.fetch_status(session, path) for path in wordlist]
            await asyncio.gather(*tasks)

def show_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(Fore.GREEN + "╔" + "═"*58 + "╗")
    matrix_typing("║            URL. GHOST - ELITE EDITION v3.5             ║")
    print(Fore.GREEN + "╚" + "═"*58 + "╝")
    print(f"{Fore.RED}    [+] Developer: Kinho0Woner")
    print(f"{Fore.RED}    [+] Engine: Asynchronous I/O & Stealth Wordlist 2026")
    print()

def main():
    show_banner()
    target = ""
    wordlist = [
        ".env", ".git/config", "docker-compose.yml", "wp-config.php", 
        "api/v1/", "api/v2/", "swagger-ui.html", "graphql", "phpinfo.php", 
        "robots.txt", "backup.sql", ".aws/credentials", "admin/"
    ]
    
    while True:
        cmd = input(f"{Style.BRIGHT}{Fore.RED}gopher-ghost {Fore.WHITE}> ").strip()
        if cmd.lower().startswith("set target"):
            target = cmd.split(" ")[-1]
            if not target.startswith("http"): target = "https://" + target
            print(f"target => {target}")
        elif cmd.lower() == "run":
            if not target: continue
            engine = GopherEngine(target)
            spinner_anim("Crawling target surface...", 1.5)
            engine.crawler()
            spinner_anim("Brute-forcing hidden paths...", 1.5)
            asyncio.run(engine.run_fuzzer(wordlist))
        elif cmd.lower() == "clear": show_banner()
        elif cmd.lower() == "exit": break

if __name__ == "__main__":
    main()

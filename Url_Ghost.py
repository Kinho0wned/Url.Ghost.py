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

# Inicializa o colorama para cores no terminal
init(autoreset=True)

# Garante que a pasta de resultados exista
if not os.path.exists("results"):
    os.makedirs("results")

def matrix_typing(text, speed=0.04, color=Fore.GREEN):
    """Efeito de digitação estilo Matrix"""
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

def spinner_anim(message, duration=1.5):
    """Animação de carregamento estilizada"""
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    while time.time() < end_time:
        for char in chars:
            sys.stdout.write(f"\r{Fore.CYAN}[{char}]{Fore.WHITE} {message}")
            sys.stdout.flush()
            time.sleep(0.08)
    sys.stdout.write(f"\r{Fore.GREEN}[+]{Fore.WHITE} {message} Concluído!          \n")

class GopherEngine:
    def __init__(self, target):
        self.target = target.rstrip('/')
        self.domain = urlparse(target).netloc
        self.found_links = set()
        self.fuzzer_findings = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) GopherGhost/3.6'
        }

    def save_result(self, category, data):
        """Salva os achados em arquivos de texto na pasta results"""
        filename = f"results/{self.domain}_{category}.txt"
        with open(filename, "a") as f:
            f.write(data + "\n")

    def crawler(self):
        """Mapeia a superfície do alvo em busca de links e scripts"""
        print(f"\n{Fore.CYAN}[*] Mapeando Endpoints de Superfície...")
        try:
            with requests.Session() as s:
                s.headers.update(self.headers)
                r = s.get(self.target, timeout=10)
                soup = BeautifulSoup(r.text, 'html.parser')
                for tag in soup.find_all(['a', 'script', 'link'], href=True, src=True):
                    attr = 'href' if tag.name in ['a', 'link'] else 'src'
                    url = urljoin(self.target, tag.get(attr)).split('?')[0].split('#')[0]
                    if self.domain in url and url not in self.found_links:
                        print(f"{Fore.GREEN}[+] Identificado: {url}")
                        self.found_links.add(url)
                        self.save_result("crawler", url)
        except Exception as e:
            print(f"{Fore.RED}[-] Erro no Crawler: {e}")

    async def fetch_status(self, session, path):
        """Testa caminhos ocultos de forma assíncrona"""
        url = urljoin(self.target, path)
        try:
            async with session.get(url, timeout=4, allow_redirects=True) as response:
                if response.status == 200:
                    # Filtra redirecionamentos falsos para a home
                    if str(response.url).rstrip('/') != self.target:
                        print(f"{Fore.GREEN}[!] DIRETÓRIO VÁLIDO: {url}")
                        self.fuzzer_findings.append(url)
                        self.save_result("fuzzer", url)
                elif response.status == 403:
                    print(f"{Fore.YELLOW}[*] PROTEGIDO (403): {url}")
        except: pass

    async def run_fuzzer(self, wordlist):
        """Gerencia as tarefas de fuzzing de alta velocidade"""
        print(f"\n{Fore.MAGENTA}[*] Iniciando Fuzzer Assíncrono (Alta Velocidade)...")
        conn = aiohttp.TCPConnector(limit=50) # Limite de 50 conexões simultâneas
        async with aiohttp.ClientSession(headers=self.headers, connector=conn) as session:
            tasks = [self.fetch_status(session, path) for path in wordlist]
            await asyncio.gather(*tasks)

    def generate_report(self):
        """Gera um relatório profissional em HTML com os achados"""
        report_path = f"results/REPORT_{self.domain}.html"
        
        html_template = f"""
        <html>
        <head>
            <title>Gopher Ghost Report - {self.domain}</title>
            <style>
                body {{ font-family: 'Courier New', Courier, monospace; background: #0d0d0d; color: #00ff00; padding: 30px; }}
                .card {{ background: #1a1a1a; border: 1px solid #333; padding: 20px; border-radius: 5px; box-shadow: 0 0 15px rgba(0,255,0,0.1); }}
                h1 {{ color: #ff0000; text-transform: uppercase; border-bottom: 2px solid #333; }}
                .stat {{ color: #ffffff; font-weight: bold; margin: 10px 0; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ background: #262626; margin: 5px 0; padding: 8px; border-left: 3px solid #ff0000; word-wrap: break-word; }}
                .footer {{ margin-top: 50px; font-size: 0.8em; color: #555; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>👻 Gopher Ghost Recon Report</h1>
                <p class="stat">Alvo: <span style="color:#00ffff;">{self.target}</span></p>
                <p class="stat">Data: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <hr style="border: 0; border-top: 1px solid #333;">
                <h3>📂 Diretórios e Arquivos Sensíveis</h3>
                <ul>
                    {"".join([f"<li>{item}</li>" for item in self.fuzzer_findings]) if self.fuzzer_findings else "<li>Nenhum dado sensível detectado.</li>"}
                </ul>
                <div class="footer">Gerado por Url_Ghost v3.6 | Desenvolvido por Kinho0Woner</div>
            </div>
        </body>
        </html>
        """
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html_template)
            print(f"\n{Fore.YELLOW}[📊] RELATÓRIO PROFISSIONAL GERADO: {Fore.WHITE}{report_path}")
        except Exception as e:
            print(f"{Fore.RED}[-] Falha ao gerar relatório: {e}")

def show_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(Fore.GREEN + "╔" + "═"*58 + "╗")
    matrix_typing("║            URL GHOST - ELITE EDITION v3.6               ║")
    print(Fore.GREEN + "╚" + "═"*58 + "╝")
    print(f"{Fore.RED}    [+] Desenvolvedor: Kinho0Woner")
    print(f"{Fore.RED}    [+] Recursos: Async Fuzzer, HTML Reporter, Surface Map")
    print()

def main():
    show_banner()
    target = ""
    # Wordlist moderna focada em falhas críticas
    wordlist = [
        ".env", ".git/config", "docker-compose.yml", "wp-config.php", 
        "api/v1/", "api/v2/", "swagger-ui.html", "graphql", "phpinfo.php", 
        "robots.txt", "backup.sql", ".aws/credentials", "admin/", ".vscode/sftp.json"
    ]
    
    while True:
        try:
            cmd = input(f"{Style.BRIGHT}{Fore.RED}url-ghost {Fore.WHITE}> ").strip()
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break

        if cmd.lower().startswith("set target"):
            target = cmd.split(" ")[-1]
            if not target.startswith("http"): target = "https://" + target
            print(f"{Fore.CYAN}Alvo definido para => {Fore.WHITE}{target}")
        
        elif cmd.lower() == "run":
            if not target:
                print(f"{Fore.RED}[!] Erro: Defina um alvo primeiro com 'set target <url>'")
                continue
            
            engine = GopherEngine(target)
            
            # Etapa 1: Crawler
            spinner_anim("Mapeando superfícies...", 1.2)
            engine.crawler()
            
            # Etapa 2: Fuzzing Assíncrono
            spinner_anim("Escaneando arquivos ocultos...", 1.2)
            asyncio.run(engine.run_fuzzer(wordlist))
            
            # Etapa 3: Relatório
            engine.generate_report()
            print(f"\n{Fore.GREEN}═══ Scan Finalizado com Sucesso ═══\n")

        elif cmd.lower() == "help":
            print(f"\n{Fore.WHITE}Comandos Disponíveis:")
            print(f"  {Fore.YELLOW}set target <url>{Fore.WHITE} - Define o alvo do scan")
            print(f"  {Fore.YELLOW}run{Fore.WHITE}              - Inicia o processo completo de recon")
            print(f"  {Fore.YELLOW}clear{Fore.WHITE}            - Limpa a tela do terminal")
            print(f"  {Fore.YELLOW}exit{Fore.WHITE}             - Fecha a ferramenta\n")

        elif cmd.lower() == "clear":
            show_banner()

        elif cmd.lower() == "exit":
            matrix_typing("DESCONECTANDO DO SERVIDOR...", color=Fore.RED)
            break
        
        elif cmd == "": continue
        else:
            print(f"{Fore.RED}[!] Comando inválido. Digite 'help' para ver as opções.")

if __name__ == "__main__":
    main()

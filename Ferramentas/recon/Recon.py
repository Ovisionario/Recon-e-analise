#!/usr/bin/env python3
import os
import sys
import csv
from datetime import datetime

# Importação do my_utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from my_utils import which, ensure_dir, safe_run

HOME = os.path.expanduser("~")
BASE_DIR = os.path.join(HOME, "Ferramentas", "recon", "resultados") 
WORDLIST = os.path.join(HOME, "Ferramentas", "recon", "wordlists", "subdomains-top1million-110000.txt")

def simple_html_report(csv_path, html_path, domain):
    """Gera o relatório visual a partir do CSV do httpx."""
    if not os.path.exists(csv_path): return
    
    html = [
        f"<html><head><meta charset='utf-8'><title>Recon {domain}</title>",
        "<style>body{font-family:sans-serif;background:#f4f7f6;padding:20px}table{width:100%;border-collapse:collapse;background:#fff;box-shadow:0 2px 5px rgba(0,0,0,0.1)}th,td{border:1px solid #ddd;padding:12px;text-align:left}th{background:#2c3e50;color:#fff}tr:nth-child(even){background:#f2f2f2}tr:hover{background:#e9ecef}</style></head><body>",
        f"<h1>Relatório de Reconhecimento: {domain}</h1>",
        "<table><tr><th>URL</th><th>Status</th><th>Título</th><th>IP</th><th>Servidor</th></tr>"
    ]

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # O httpx em modo CSV usa nomes específicos de colunas
                url = row.get('url', 'N/A')
                sc = row.get('status_code', row.get('status-code', 'N/A'))
                title = row.get('title', 'N/A')
                ip = row.get('host', row.get('ip', 'N/A'))
                server = row.get('server', 'N/A')
                html.append(f"<tr><td>{url}</td><td>{sc}</td><td>{title}</td><td>{ip}</td><td>{server}</td></tr>")
    except Exception as e:
        html.append(f"<tr><td colspan='5'>Erro ao ler CSV: {e}</td></tr>")

    html.append("</table><p>Gerado em: " + datetime.now().strftime("%d/%m/%Y %H:%M") + "</p></body></html>")
    with open(html_path, "w", encoding='utf-8') as h:
        h.write("\n".join(html))

def main():
    if len(sys.argv) != 2:
        print(f"Uso: python3 {sys.argv[0]} <dominio>")
        return

    domain = sys.argv[1].strip()
    target_dir = os.path.join(BASE_DIR, domain.replace(".", "_"))
    ensure_dir(target_dir)

    # Caminhos
    out_sub = os.path.join(target_dir, "raw_subfinder.txt")
    out_amass = os.path.join(target_dir, "raw_amass.txt")
    out_pure = os.path.join(target_dir, "raw_puredns.txt")
    final_clean = os.path.join(target_dir, "all_unique.txt")
    final_csv = os.path.join(target_dir, "dados_analise.csv")
    final_html = os.path.join(target_dir, "resultado.html")

    print(f"\n🚀 [RECON FÊNIX V2] Alvo: {domain}")

    # 1. Execução das ferramentas (Captura Direta)
    if which("subfinder"):
        print("   [1/4] Subfinder...")
        _, res = safe_run(f"subfinder -d {domain} -silent")
        with open(out_sub, "w") as f: f.write(res)

    if which("amass"):
        print("   [2/4] Amass (Modo Passivo)...")
        _, res = safe_run(f"amass enum -passive -d {domain}", timeout=300)
        with open(out_amass, "w") as f: f.write(res)

    if which("puredns") and os.path.exists(WORDLIST):
        print("   [3/4] Puredns (Bruteforce)...")
        _, res = safe_run(f"puredns resolve {WORDLIST} {domain} -r 1.1.1.1 --quiet")
        with open(out_pure, "w") as f: f.write(res)

  # 2. Consolidação
    print("   [4/4] Filtrando resultados únicos...")
    subs = set()
    
    # FORÇA incluir o domínio alvo (o "mínimo viável")
    subs.add(domain.lower())

    for f in [out_sub, out_amass, out_pure]:
        if os.path.exists(f):
            with open(f, "r") as fh:
                for line in fh:
                    l = line.strip().lower()
                    if l and "." in l: # Verifica se parece um domínio
                        subs.add(l)

    # Agora o script nunca será zero, pois incluímos o 'domain' acima
    with open(final_clean, "w") as f:
        f.write("\n".join(sorted(subs)))

    print(f"   ✅ {len(subs)} alvos prontos para validação.")

    # 3. HTTPX & Relatórios
    if which("httpx"):
        print(f"   [*] Validando alvos e gerando relatórios...")
        # Adicionei -nc (no color) para o CSV não vir com lixo
        cmd_httpx = f"httpx -l {final_clean} -silent -sc -title -ip -server -nc -csv -o {final_csv}"
        safe_run(cmd_httpx)
        
        if os.path.exists(final_csv):
            simple_html_report(final_csv, final_html, domain)
            print(f"\n✅ SUCESSO! Relatório: {final_html}")
            
    # 3. HTTPX & Relatórios
    if which("httpx"):
        print(f"   [*] Validando {len(subs)} alvos e gerando relatórios...")
        # -csv gera a saída estruturada perfeita para o Analyzer e para o nosso HTML
        cmd_httpx = f"httpx -l {final_clean} -silent -sc -title -ip -server -csv -o {final_csv}"
        safe_run(cmd_httpx)
        
        # Gera o HTML baseado no CSV que o httpx acabou de criar
        simple_html_report(final_csv, final_html, domain)
        
        print(f"\n✅ SUCESSO ABSOLUTO!")
        print(f"   -> Visualize aqui: {final_html}")
        print(f"   -> Dados para Analyzer: {final_csv}")

if __name__ == "__main__":
    main()

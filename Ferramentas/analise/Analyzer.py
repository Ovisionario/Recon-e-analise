#!/usr/bin/env python3
import os
import sys
import csv
import xml.etree.ElementTree as ET
from datetime import datetime

# Importação do seu arquivo de utilitários
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from my_utils import which, ensure_dir, safe_run

# Configurações de Caminho
HOME = os.path.expanduser("~")
BASE_RECON = os.path.join(HOME, "Ferramentas", "recon", "resultados")
BASE_ANALYZE = os.path.join(HOME, "Ferramentas", "analise", "resultados")

def get_targets(domain):
    """Puxa os subdomínios ativos do seu Recon para o Nuclei e WhatWeb."""
    project_folder = domain.replace(".", "_")
    all_unique = os.path.join(BASE_RECON, project_folder, "all_unique.txt")
    if os.path.exists(all_unique):
        return all_unique
    return None

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 analyzer.py <dominio>")
        return

    domain = sys.argv[1]
    target_dir = os.path.join(BASE_ANALYZE, domain.replace(".", "_"))
    ensure_dir(target_dir)
    
    print(f"\n🧠 [ANALYZER] Iniciando Análise Estratégica: {domain}")

    # 1. Identificação de Tecnologias (WhatWeb)
    if which("whatweb"):
        targets = get_targets(domain)
        if targets:
            print("   [1/3] Mapeando tecnologias com WhatWeb...")
            ww_out = os.path.join(target_dir, "tech_fingerprint.txt")
            # Aggression 1 é rápido e discreto
            safe_run(f"whatweb -i {targets} --aggression 1", out_path=ww_out)
            print(f"   ✅ Fingerprint concluído: {ww_out}")

    # 2. Varredura de Vulnerabilidades (Nuclei)
    if which("nuclei"):
        targets = get_targets(domain)
        if targets:
            print("   [2/3] Caçando vulnerabilidades com Nuclei (High/Critical)...")
            nuc_out = os.path.join(target_dir, "vulnerabilidades.txt")
            # -severity: foca no que dá dinheiro/invasão | -silent: limpa a saída
            cmd_nuclei = f"nuclei -l {targets} -severity critical,high -silent -o {nuc_out}"
            safe_run(cmd_nuclei)
            
            if os.path.exists(nuc_out) and os.path.getsize(nuc_out) > 0:
                print(f"   🔥 ALERTA: Vulnerabilidades encontradas! Veja: {nuc_out}")
            else:
                print("   ✅ Nuclei não encontrou falhas críticas óbvias.")

    # 3. Scan de Portas Profundo (Nmap) nos IPs do CSV
    # (Mantemos o Nmap para ver a infraestrutura de rede)
    print("   [3/3] Detalhando Portas e Versões com Nmap...")
    csv_path = os.path.join(BASE_RECON, domain.replace(".", "_"), "dados_analise.csv")
    if os.path.exists(csv_path):
        ips = set()
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ip = row.get('host') or row.get('ip')
                if ip and ip != 'N/A': ips.add(ip)
        
        if ips:
            iplist = os.path.join(target_dir, "ips_targets.txt")
            with open(iplist, "w") as f: f.write("\n".join(ips))
            xml_out = os.path.join(target_dir, "nmap_detailed.xml")
            # Versão agressiva que corrigimos antes
            safe_run(f"nmap -sV --version-intensity 5 -T4 -Pn -iL {iplist} -oX {xml_out}")
            print(f"   ✅ Scan de rede concluído: {xml_out}")

    print(f"\n🏁 Análise de {domain} finalizada. Relatórios em: {target_dir}")

if __name__ == "__main__":
    main()

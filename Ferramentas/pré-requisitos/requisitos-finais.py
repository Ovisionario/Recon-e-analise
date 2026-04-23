#!/usr/bin/env python3
"""
requisitos.py - Versão Evoluída
Instala, verifica e configura o ambiente para Recon e Bug Bounty.
"""

import os
import sys
import subprocess
import shutil

# --- Lista de Ferramentas Atualizada ---
GO_TOOLS = [
    "httpx", 
    "subfinder", 
    "assetfinder", 
    "amass", 
    "puredns", 
    "whatweb", 
    "nuclei", 
    "subzy",
    "naabu"   # Nova ferramenta para scan de portas rápido
]

APT_TOOLS = ["nmap", "curl", "jq"]

# -----------------------------
# Utilitários
# -----------------------------
def which(program):
    return shutil.which(program)

def check_go_installed():
    if which("go"):
        print("✅ Go (Golang) encontrado.")
        return True
    else:
        print("❌ Go não encontrado. Instale-o: sudo apt install golang")
        return False

def install_go_tool(tool_name):
    print(f"   -> Tentando instalar {tool_name} via go install...")
    
    # Mapeamento de repositórios atualizado para 2024/2025
    repos = {
        "subfinder": "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
        "httpx": "github.com/projectdiscovery/httpx/cmd/httpx@latest",
        "nuclei": "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
        "naabu": "github.com/projectdiscovery/naabu/cmd/naabu@latest",
        "puredns": "github.com/d3mondev/puredns/v2@latest",
        "assetfinder": "github.com/tomnomnom/assetfinder@latest",
        "amass": "github.com/owasp-amass/amass/v4/...@master", # Atualizado para v4
        "subzy": "github.com/PentestPad/subzy@latest",
        "whatweb": "github.com/urbanadventurer/WhatWeb@latest" # WhatWeb via Go (experimental) ou via repositório
    }

    repo = repos.get(tool_name, f"github.com/projectdiscovery/{tool_name}/cmd/{tool_name}@latest")
        
    env = os.environ.copy()
    # Garante que o ~/go/bin esteja acessível durante a instalação
    go_bin = os.path.join(os.path.expanduser("~"), "go", "bin")
    env["PATH"] = f"{env.get('PATH')}:{go_bin}"
        
    try:
        subprocess.run(
            ["go", "install", "-v", repo], 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            env=env
        )
        print(f"   ✅ {tool_name} instalado/atualizado.")
        
       # Se for o Nuclei, já atualiza os templates
        if tool_name == "nuclei":
            print("   🔄 Baixando/Atualizando templates do Nuclei (isso pode demorar)...")
            # Tiramos o DEVNULL para você ver o progresso real na tela
            subprocess.run([os.path.join(go_bin, "nuclei"), "-update-templates"])
            
        return True
    except Exception as e:
        print(f"   ❌ ERRO ao instalar {tool_name}. Verifique sua conexão ou o repositório.")
        return False

# -----------------------------
# Função Principal
# -----------------------------
def main():
    print("--- 🛡️  Configuração de Ambiente Bug Bounty ---")
    
    if not check_go_installed():
        sys.exit(1)

    # Verificação do PATH
    go_bin_path = os.path.join(os.path.expanduser("~"), "go", "bin")
    if go_bin_path not in os.environ.get("PATH", ""):
        print(f"\n⚠️  ALERTA DE PATH: Adicione isso ao seu ~/.bashrc ou ~/.zshrc:")
        print(f'   export PATH=$PATH:{go_bin_path}')
        # Tenta adicionar temporariamente para esta sessão de script
        os.environ["PATH"] += f":{go_bin_path}"

    # Processamento Go Tools
    print("\n--- Verificando Ferramentas Go ---")
    missing_go = []
    for tool in GO_TOOLS:
        if which(tool):
            print(f"✅ {tool.ljust(12)} [INSTALADO]")
        else:
            print(f"❌ {tool.ljust(12)} [FALTANDO]")
            missing_go.append(tool)

    if missing_go:
        resp = input(f"\nDeseja instalar {len(missing_go)} ferramentas agora? (s/n): ").lower()
        if resp == 's':
            for tool in missing_go:
                install_go_tool(tool)

    # Processamento APT Tools
    print("\n--- Verificando Ferramentas APT (Sistema) ---")
    missing_apt = []
    for tool in APT_TOOLS:
        if which(tool):
            print(f"✅ {tool.ljust(12)} [INSTALADO]")
        else:
            print(f"❌ {tool.ljust(12)} [FALTANDO]")
            missing_apt.append(tool)

    if missing_apt:
        print(f"\n⚠️  Execute: sudo apt update && sudo apt install {' '.join(missing_apt)} -y")

    # Finalização
    print("\n--- ✨ Verificação Concluída ---")
    print(f"Diretório de resultados: ~/Ferramentas/analise/resultados")

if __name__ == "__main__":
    main()

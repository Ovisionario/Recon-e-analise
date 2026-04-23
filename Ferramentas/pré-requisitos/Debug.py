#!/usr/bin/env python3
import os
import sys

# Garante que o Python ache o my_utils.py
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from my_utils import which, ensure_dir, safe_run

HOME = os.path.expanduser("~")
BASE_DIR = os.path.join(HOME, "Ferramentas", "recon", "resultados") 

def main():
    if len(sys.argv) != 2:
        print(f"Uso: python3 {sys.argv[0]} <dominio>")
        return

    domain = sys.argv[1].strip()
    target_dir = os.path.join(BASE_DIR, domain.replace(".", "_"))
    ensure_dir(target_dir)

    # Arquivos de saída
    sub_out = os.path.join(target_dir, "subfinder.txt")

    print(f"\n🔬 [TESTE DE DIAGNÓSTICO] Alvo: {domain}")
    
    # --- TESTE 1: SUBFINDER ---
    if which("subfinder"):
        print("   -> Tentando Subfinder...")
        # Rodando DIRETAMENTE para ver o erro na tela se houver
        cmd = ["subfinder", "-d", domain, "-silent", "-o", sub_out]
        code, output = safe_run(cmd)
        
        if os.path.exists(sub_out) and os.path.getsize(sub_out) > 0:
            print(f"   ✅ SUCESSO: Subfinder criou o arquivo com {os.path.getsize(sub_out)} bytes.")
        else:
            print(f"   ❌ FALHA: Subfinder não gerou arquivo ou está vazio.")
            print(f"   DEBUG SAÍDA: {output[:200]}") # Mostra os primeiros 200 caracteres do erro

    # --- TESTE 2: PERMISSÃO DE ESCRITA ---
    test_file = os.path.join(target_dir, "teste.txt")
    try:
        with open(test_file, "w") as f:
            f.write("teste")
        print(f"   ✅ SUCESSO: Permissão de escrita na pasta {target_dir} OK.")
        os.remove(test_file)
    except Exception as e:
        print(f"   ❌ FALHA DE PERMISSÃO: {e}")

if __name__ == "__main__":
    main()

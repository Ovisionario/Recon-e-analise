import os
import shutil
import subprocess
import re

# Expressão regular para encontrar códigos ANSI
ANSI_CLEANER = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def clean_ansi(text):
    """Remove códigos de cores e formatação do texto."""
    return ANSI_CLEANER.sub('', text)

ANSI_RE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def which(program):
    """Verifica se o executável existe no sistema."""
    return shutil.which(program)

def ensure_dir(path):
    """Cria o diretório se ele não existir."""
    os.makedirs(path, exist_ok=True)

def safe_run(cmd, out_path=None, timeout=None):
    try:
        # Garante que o comando seja uma string única
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
        
        proc = subprocess.run(
            cmd_str, 
            shell=True, 
            executable='/bin/bash', # Força o bash
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            timeout=timeout, 
            universal_newlines=True, 
            encoding='utf-8', 
            errors='ignore'
        )
        
        output = proc.stdout if proc.stdout else ""
        if out_path:
            with open(out_path, "w") as f:
                f.write(output)
        
        return proc.returncode, output
    except Exception as e:
        return 1, str(e)
        

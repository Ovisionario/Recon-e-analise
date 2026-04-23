#!/bin/bash

# --- O ORQUESTRADOR DO SCRIPT MONSTRO ---

clear
echo "=========================================="
echo "      INICIANDO SUITE SCRIPT MONSTRO      "
echo "=========================================="

# 1. Pergunta o alvo
read -p "Qual o domínio alvo? (ex: site.com): " ALVO

# 2. Define o caminho do arquivo que o Recon deve gerar
# Ajuste o caminho abaixo para onde o seu Recon salva os resultados
ARQUIVO_RESULTADO="ferramentas/resultados/${ALVO}.txt"

echo -e "\n[+] PASSO 1: Iniciando RECON em $ALVO..."
python3 ferramentas/recon/recon.py "$ALVO"

# 3. O CHECKPOINT (A Pausa de Segurança)
echo -e "\n[!] Aguardando validação dos dados..."
sleep 2 # Uma pausa dramática de 2 segundos para o sistema respirar

if [ -f "$ARQUIVO_RESULTADO" ]; then
    echo -e "[\e[32mOK\e[0m] Arquivo de resultados localizado com sucesso!"
    
    echo -e "\n[+] PASSO 2: Iniciando ANÁLISE DE VULNERABILIDADES..."
    python3 ferramentas/analise/analyzer.py "$ALVO"
else
    echo -e "[\e[31mERRO\e[0m] O Recon falhou ou o arquivo $ARQUIVO_RESULTADO não foi criado."
    echo "Operação abortada para evitar análise sem dados."
    exit 1
fi

echo -e "\n=========================================="
echo "      OPERAÇÃO FINALIZADA COM SUCESSO     "
echo "=========================================="

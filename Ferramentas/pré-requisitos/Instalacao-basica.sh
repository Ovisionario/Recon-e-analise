#!/bin/bash

echo "[1/9] Atualizando pacotes..."
sudo apt update && sudo apt install -y git curl wget unzip snapd

echo "[+] Iniciando instalação completa das ferramentas de Recon..."

echo "[2/9] Instalando dependências básicas..."
sudo apt install -y golang git curl python3-pip build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev

echo "[3/9] Configurando Go (se necessário)..."
if ! grep -q "export GOPATH=" ~/.bashrc; then
  echo 'export GOPATH=$HOME/go' >> ~/.bashrc
  echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc
  export GOPATH=$HOME/go
  export PATH=$PATH:$GOPATH/bin
fi

mkdir -p ~/Ferramentas

echo "Preparando e instalando ferramentas..."

instalar_go subfinder github.com/projectdiscovery/subfinder/v2/cmd/subfinder
instalar_go httpx github.com/projectdiscovery/httpx/cmd/httpx
instalar_go dnsx github.com/projectdiscovery/dnsx/cmd/dnsx

if ! command -v amass &> /dev/null; then
    echo "[+] Instalando amass..."
    sudo snap install amass
else
    echo "[✓] amass já instalado."
fi

echo "[4/9] Instalando nuclei..."
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

echo "[5/9] Atualizando templates do nuclei..."
nuclei -update-templates

echo "[6/9] Instalando whatweb e nikto..."
sudo apt install -y whatweb nikto

echo "[7/9] Instalando assetfinder..."
go install -v github.com/tomnomnom/assetfinder@latest

echo "[8/9] Instalando waybackurls..."
go install -v github.com/tomnomnom/waybackurls@latest

echo "[9/9] Instalando dnsx..."
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

#Garantindo que os binários do Go estejam sempre disponíveis
if ! grep -q "export PATH=\$PATH:\$HOME/go/bin" ~/.bashrc; then
    echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
fi

ec

echo "✅ Ferramentas instaladas com sucesso!"
echo "⚠️ Se for o primeiro uso do Go, pode ser necessário reiniciar o terminal para PATH funcionar 100%."

echo "⚠️  Rode 'source ~/.bashrc' ou reinicie o terminal se algum comando ainda não estiver funcionando."

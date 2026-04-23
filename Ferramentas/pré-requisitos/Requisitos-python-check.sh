#!/usr/bin/env bash
# check_recon_env.sh
# Verifica presença de ferramentas CLI e pacotes Python e gera recon_env_report.txt no diretório atual.

OUTFILE="$(pwd)/recon_env_report_local.txt"
echo "Recon environment local check report" > "$OUTFILE"
echo "Generated: $(date --iso-8601=seconds)" >> "$OUTFILE"
echo "===================================" >> "$OUTFILE"
echo "" >> "$OUTFILE"

CLI_TOOLS=(subfinder httpx dnsx amass curl jq dig nmap nikto masscan git chromedriver)
echo "Checking CLI tools..." | tee -a "$OUTFILE"
for t in "${CLI_TOOLS[@]}"; do
  path=$(which $t 2>/dev/null || true)
  if [ -n "$path" ]; then
    # try to get a version string
    ver="$($t --version 2>&1 | head -n1 2>/dev/null || true)"
    echo " - $t: INSTALLED (path: $path) version: ${ver:-unknown}" | tee -a "$OUTFILE"
  else
    echo " - $t: MISSING" | tee -a "$OUTFILE"
  fi
done

echo "" >> "$OUTFILE"
PY_PKGS=(selenium pyautogui requests beautifulsoup4 pandas lxml html5lib webdriver_manager)
echo "Checking Python packages (using pip for current python3)..." | tee -a "$OUTFILE"
python_cmd=$(which python3 || which python)
if [ -z "$python_cmd" ]; then
  echo "No python3 found in PATH. Aborting python checks." | tee -a "$OUTFILE"
else
  echo "Using Python at: $python_cmd" | tee -a "$OUTFILE"
  for pkg in "${PY_PKGS[@]}"; do
    $python_cmd - <<PYCODE > /dev/null 2>&1
try:
    import pkgutil, sys
    if pkgutil.find_loader("$pkg") is None:
        raise SystemExit(2)
    # try to get version
    mod = __import__("$pkg")
    ver = getattr(mod, '__version__', None) or getattr(mod, 'VERSION', None) or ''
    if ver:
        print("$pkg:INSTALLED:"+str(ver))
    else:
        print("$pkg:INSTALLED")
except Exception:
    print("$pkg:MISSING")
PYCODE
    # read last line printed by the subshell
    line=$(tail -n1 <( $python_cmd - <<PYCODE
try:
    import pkgutil, sys
    if pkgutil.find_loader("$pkg") is None:
        raise SystemExit(2)
    mod = __import__("$pkg")
    ver = getattr(mod, '__version__', None) or getattr(mod, 'VERSION', None) or ''
    if ver:
        print("$pkg:INSTALLED:"+str(ver))
    else:
        print("$pkg:INSTALLED")
except Exception:
    print("$pkg:MISSING")
PYCODE
)
    echo " - $line" | tee -a "$OUTFILE"
  done
fi

echo "" >> "$OUTFILE"
echo "Environment summary:" | tee -a "$OUTFILE"
echo " - user: $(whoami)" | tee -a "$OUTFILE"
echo " - cwd: $(pwd)" | tee -a "$OUTFILE"
echo " - python: $($python_cmd --version 2>&1 || echo 'no python')" | tee -a "$OUTFILE"
echo "" >> "$OUTFILE"

echo "Report saved to: $OUTFILE"
echo ""
echo "Quick summary (console):"
grep -E "INSTALLED|MISSING" "$OUTFILE" | sed -n '1,60p'

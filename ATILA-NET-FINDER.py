#!/usr/bin/env python3
import os, sys, time, signal, ipaddress, json, csv
from concurrent.futures import ThreadPoolExecutor, as_completed

for p in ["requests", "tqdm", "colorama"]:
    try:
        __import__(p)
    except:
        os.system(f"pip install {p} -q")
        __import__(p)

import requests
from tqdm import tqdm
from colorama import Fore, Style, init
init(autoreset=True)

V = "2.3.0-GEO"
DP = [80, 443, 8080, 3128, 1080, 8888, 9090]
VU = "http://httpbin.org/ip"

def get_country(ip):
    try:
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3)
        return r.json().get("country_name", "Desconocido")
    except:
        return "Desconocido"

class Scanner:
    def __init__(self, ci, po, wo, to, ve, fo, cf=None):
        self.ci = ci; self.po = po
        self.wo = max(1, min(wo, 150)); self.to = max(1.0, min(to, 10.0))
        self.ve = ve; self.fo = fo; self.re = []
        self.cf = cf.strip().lower() if cf else None
        self._vci(); signal.signal(signal.SIGINT, self._hex)

    def _vci(self):
        try:
            self.ne = ipaddress.ip_network(self.ci, strict=False)
            self.ip = list(self.ne.hosts())
            if len(self.ip) > 5000: self.ip = self.ip[:5000]
        except:
            print(f"{Fore.RED}❌ CIDR inválido{Style.RESET_ALL}"); sys.exit(1)

    def _hex(self, si, fr):
        print(f"\n{Fore.RED}[!] Guardando y saliendo...{Style.RESET_ALL}")
        self._sr(); sys.exit(0)

    def _vp(self, ip, po):
        pu = f"http://{ip}:{po}"; st = time.time()
        try:            r = requests.get(VU, proxies={"http": pu, "https": pu}, timeout=self.to, allow_redirects=True)
            if r.status_code == 200:
                la = time.time() - st; orig = r.json().get("origin", "N/A")
                an = "Elite" if "X-Forwarded-For" not in r.headers and "Via" not in r.headers else "Transparente"
                res = {"ip": ip, "port": po, "latency": round(la, 3), "an": an, "exit": orig, "country": "N/A"}
                if self.cf:
                    co = get_country(ip)
                    if self.cf not in co.lower(): return None
                    res["country"] = co
                return res
        except: pass
        return None

    def run(self):
        to = len(self.ip) * len(self.po)
        filt = f" | 🌍 Filtro: {self.cf.upper()}" if self.cf else ""
        print(f"\n{Fore.CYAN}🎯 Escaneando {self.ci} | {to} pruebas | {self.wo} hilos{filt}{Style.RESET_ALL}")
        ex = ThreadPoolExecutor(max_workers=self.wo)
        fu = [ex.submit(self._vp, str(i), p) for i in self.ip for p in self.po]
        try:
            for f in tqdm(as_completed(fu), total=to, desc=f"{Fore.BLUE}Progreso{Style.RESET_ALL}", unit="proxy", leave=True, colour="cyan"):
                re = f.result()
                if re:
                    self.re.append(re)
                    if self.ve: tqdm.write(f"{Fore.GREEN}[+] {re['ip']}:{re['port']} | ⏱️ {re['latency']}s | 🌍 {re['country']} | 🛡️ {re['an']}{Style.RESET_ALL}")
        finally: ex.shutdown(wait=True)
        print(f"\n{Fore.YELLOW}[✓] Listo. {len(self.re)} proxies válidos.{Style.RESET_ALL}"); self._sr()

    def _sr(self):
        if not self.re: print(f"{Fore.YELLOW}Sin proxies funcionales.{Style.RESET_ALL}"); return
        ts = time.strftime("%Y%m%d_%H%M%S"); nm = f"proxies_{ts}"
        if self.fo == "json":
            with open(f"{nm}.json", "w") as f: json.dump(self.re, f, indent=2, ensure_ascii=False)
        elif self.fo == "csv":
            with open(f"{nm}.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=self.re[0].keys()); w.writeheader(); w.writerows(self.re)
        else:
            with open(f"{nm}.txt", "w") as f:
                for p in self.re: f.write(f"{p['ip']}:{p['port']}\n")
        print(f"{Fore.GREEN}💾 Guardado en {nm}.{self.fo}{Style.RESET_ALL}")

def menu():
    while True:
        print(f"\n{Fore.BLUE}╭━━━┳━━━━┳━━┳╮╱╱╭━━━╮╱╭━━━━┳━━━┳━━━┳━━━━╮")
        print(f"┃╭━╮┃╭╮╭╮┣┫┣┫┃╱╱┃╭━╮┃╱┃╭╮╭╮┃╭━━┫╭━╮┃╭╮╭╮┃")
        print(f"┃┃╱┃┣╯┃┃╰╯┃┃┃╱╱┃┃╱┃┃╱╰╯┃┃╰┫╰━━┫╰━━╋╯┃┃╰╯")
        print(f"┃╰━╯┃╱┃┃╱╱┃┃┃╱╱┃┃╱┃┃╱╭┫╰━╯┣━━╮┃┃╱┃╭━━┻━━╮┃╱┃┃")
        print(f"┃╭━╮┃╱┃┃╱╭┫┣┫╰━╯┃╭━╮┣━━╯┃┃╱┃╰━━┫╰━╯┃╱┃┃")
        print(f"╰╯╱╰╯╱╰╯╱╰━━┻━━━┻╯╱╰╯╱╱╱╰╯╱╰━━━┻━━━╯╱╰╯{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  ATILA-NET-FINDER v{V} - Menú{Style.RESET_ALL}")        print(f"{Fore.YELLOW}1. Escanear\n2. Salir{Style.RESET_ALL}")
        op = input("\n👉 Opción: ").strip()
        if op == "1":
            ci = input("🌐 CIDR (ej: 104.16.0.0/12): ").strip()
            if not ci: continue
            ps = input("🔌 Puertos (Enter=default): ").strip()
            po = [int(p) for p in ps.split(",")] if ps else DP
            w = input("⚙️ Hilos (Enter=80): ").strip(); wo = int(w) if w else 80
            t = input("⏱️ Timeout (Enter=3): ").strip(); to = float(t) if t else 3.0
            cf = input("🌍 País (ej: Mexico, US, Spain o Enter=ninguno): ").strip() or None
            fo = input("📄 Formato [json/csv/txt] (Enter=json): ").strip().lower() or "json"
            Scanner(ci, po, wo, to, True, fo, cf).run()
            input(f"\n{Fore.CYAN}Enter para volver...{Style.RESET_ALL}")
        elif op == "2":
            print(f"{Fore.RED}Saliendo...{Style.RESET_ALL}"); break
        else:
            print(f"{Fore.RED}Opción inválida.{Style.RESET_ALL}")

if __name__ == "__main__":
    menu()

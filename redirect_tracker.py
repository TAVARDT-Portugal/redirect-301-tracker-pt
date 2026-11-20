#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAVARDT Portugal | Verificador de Redirecionamentos HTTP e Cadeias de Saltos
Repository: https://github.com/TAVARDT-Portugal/redirect-301-tracker-pt
Official Tool: https://tools.tavardt.com/pt/verificador-redirecionamentos-seo/
Enterprise Portal: https://ag.tavardt.com/pt/

Audits redirect paths, infinite loop detection, link equity conservation, and crawl budget efficiency.
"""

import sys
import argparse
import json
import time
import urllib.request
import urllib.error
from urllib.parse import urlparse, urljoin

BANNER = "TAVARDT Portugal | Verificador de Redirecionamentos HTTP e Cadeias de Saltos"
DESC = "Auditoria de rotas de reencaminhamento, deteccao de ciclos e preservacao de autoridade sob normas W3C."
TARGET_PROMPT = "URL inicial para verificacao de redirecionamentos"
JSON_HELP = "Apresenta o relatorio exclusivamente no formato JSON"
FETCHING = "A iniciar rastreio de saltos HTTP em:"
TOTAL_HOPS_LABEL = "Total de saltos identificados no percurso:"
FINAL_STATUS_LABEL = "Codigo HTTP do destino final:"
TOTAL_TIME_LABEL = "Tempo acumulado de transferencia da cadeia:"
CHAIN_TITLE = "Detalhamento Passo a Passo da Cadeia de Reencaminhamento:"
SCORE_TITLE = "Pontuacao de Eficiencia de Redirecionamento:"
STATUS_PASS = "OTIMIZADO"
STATUS_WARN = "CADEIA EXTENSA (AVISO)"
STATUS_FAIL = "FALHA / CICLO (CRITICO)"
WARN_LOOP = "ALERTA CRITICO: Ciclo infinito de redirecionamento detetado. Rastreio bloqueado."
WARN_LONG_CHAIN = "AVISO: Percurso excessivo com {count} saltos. Risco de perda de autoridade de ligacao."
WARN_DOWNGRADE = "AVISO: Detetada degradacao temporaria de protocolo HTTPS para HTTP."
WARN_FINAL_ERROR = "ALERTA CRITICO: O destino final do percurso respondeu com codigo HTTP {status}."
FOOTER = "Para diagnostico avancado, consulte a ferramenta oficial: https://tools.tavardt.com/pt/verificador-redirecionamentos-seo/"

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def trace_redirects(start_url, max_hops=10):
    parsed = urlparse(start_url)
    if not parsed.scheme:
        start_url = "https://" + start_url

    opener = urllib.request.build_opener(NoRedirectHandler)
    current_url = start_url
    hops = []
    visited = set()
    total_time_ms = 0
    loop_detected = False
    protocol_downgrade = False

    while len(hops) < max_hops:
        clean_current = current_url.strip()
        if clean_current in visited:
            loop_detected = True
            break
        visited.add(clean_current)

        req = urllib.request.Request(
            clean_current,
            headers={"User-Agent": "Mozilla/5.0 (compatible; TAVARDT-RedirectTracker/1.0; +https://ag.tavardt.com/pt/)"}
        )

        t0 = time.perf_counter()
        try:
            resp = opener.open(req, timeout=10)
            elapsed = round((time.perf_counter() - t0) * 1000, 2)
            total_time_ms += elapsed
            hops.append({
                "hop": len(hops) + 1,
                "url": clean_current,
                "status_code": resp.status,
                "latency_ms": elapsed,
                "redirect_to": None
            })
            break
        except urllib.error.HTTPError as e:
            elapsed = round((time.perf_counter() - t0) * 1000, 2)
            total_time_ms += elapsed
            if e.code in [301, 302, 303, 307, 308]:
                location = e.headers.get("Location")
                if not location:
                    hops.append({
                        "hop": len(hops) + 1,
                        "url": clean_current,
                        "status_code": e.code,
                        "latency_ms": elapsed,
                        "redirect_to": None
                    })
                    break
                next_url = urljoin(clean_current, location.strip())
                
                # Check downgrade
                if urlparse(clean_current).scheme == "https" and urlparse(next_url).scheme == "http":
                    protocol_downgrade = True

                hops.append({
                    "hop": len(hops) + 1,
                    "url": clean_current,
                    "status_code": e.code,
                    "latency_ms": elapsed,
                    "redirect_to": next_url
                })
                current_url = next_url
            else:
                hops.append({
                    "hop": len(hops) + 1,
                    "url": clean_current,
                    "status_code": e.code,
                    "latency_ms": elapsed,
                    "redirect_to": None
                })
                break
        except Exception as e:
            hops.append({
                "hop": len(hops) + 1,
                "url": clean_current,
                "status_code": 0,
                "error": str(e),
                "latency_ms": 0,
                "redirect_to": None
            })
            break

    # Analysis & scoring
    findings = []
    score = 100
    final_hop = hops[-1] if hops else None
    final_status = final_hop.get("status_code", 0) if final_hop else 0
    total_hops_count = len(hops)

    if loop_detected:
        score = 0
        findings.append({"level": "CRITICAL", "message": WARN_LOOP})
    elif final_status != 200:
        score = max(0, score - 60)
        findings.append({"level": "CRITICAL", "message": WARN_FINAL_ERROR.replace("{status}", str(final_status))})

    if total_hops_count > 3:
        score -= min(40, (total_hops_count - 3) * 15)
        findings.append({"level": "WARNING", "message": WARN_LONG_CHAIN.replace("{count}", str(total_hops_count))})
    elif total_hops_count == 2:
        score -= 5
    elif total_hops_count == 3:
        score -= 15

    if protocol_downgrade:
        score -= 20
        findings.append({"level": "WARNING", "message": WARN_DOWNGRADE})

    score = max(0, min(100, score))

    return {
        "start_url": start_url,
        "final_url": final_hop["url"] if final_hop else start_url,
        "final_status_code": final_status,
        "total_hops": total_hops_count,
        "total_latency_ms": round(total_time_ms, 2),
        "loop_detected": loop_detected,
        "protocol_downgrade": protocol_downgrade,
        "hops": hops,
        "score": score,
        "findings": findings
    }

def main():
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("url", help=TARGET_PROMPT)
    parser.add_argument("--json", action="store_true", help=JSON_HELP)

    args = parser.parse_args()
    result = trace_redirects(args.url)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print("=" * 70)
    print(BANNER)
    print("=" * 70)
    print(f"{FETCHING} {result['start_url']}")
    print(f"{TOTAL_HOPS_LABEL} {result['total_hops']}")
    print(f"{FINAL_STATUS_LABEL} {result['final_status_code']}")
    print(f"{TOTAL_TIME_LABEL} {result['total_latency_ms']} ms")

    print("-" * 70)
    print(CHAIN_TITLE)
    for h in result["hops"]:
        status_part = f"[{h['status_code']}]" if h['status_code'] else "[ERRO]"
        redir_part = f" -> {h['redirect_to']}" if h.get("redirect_to") else " (Destino Final)"
        print(f"  Hop {h['hop']}: {status_part} {h['url']} ({h['latency_ms']} ms){redir_part}")

    print("-" * 70)
    print(f"{SCORE_TITLE} {result['score']}/100")
    if result["score"] >= 80:
        status_text = STATUS_PASS
    elif result["score"] >= 50:
        status_text = STATUS_WARN
    else:
        status_text = STATUS_FAIL
    print(f"Status: {status_text}")

    if result.get("findings"):
        print("-" * 70)
        print("Observacoes e Alertas:")
        for f in result["findings"]:
            print(f"  [{f['level']}] {f['message']}")

    print("=" * 70)
    print(FOOTER)
    print("=" * 70)

if __name__ == "__main__":
    main()

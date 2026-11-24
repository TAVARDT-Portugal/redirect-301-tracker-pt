# Verificador de Redirecionamentos HTTP e Cadeias de Saltos

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Verificador Redirecionamentos](https://img.shields.io/badge/TAVARDT-Redirect%20301-5b3cf5.svg)](https://tools.tavardt.com/pt/verificador-redirecionamentos-seo/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)

Auditoria de rotas de reencaminhamento, deteccao de ciclos continuos e preservacao de autoridade sob normas W3C.

Desenvolvido e mantido pela divisao de arquitetura de indexacao da **TAVARDT Portugal**.

***

## Capacidades de Auditoria de Redirecionamentos HTTP

* **Rastreio Completo de Cadeias de Saltos**: Inspeção detalhada de codigos de resposta HTTP (301, 302, 307, 308) ao longo do percurso.
* **Deteção de Ciclos e Loops de Redirecionamento**: Identificacao imediata de ligações circulares que causam falhas de carregamento.
* **Conservacao de Autoridade e Link Equity**: Prevencao de perda de autoridade semantica provocada por saltos intermediarios em excesso.
* **Inspeção de Protocolo Seguro**: Deteção de saltos indesejados entre esquemas HTTP e HTTPS.
* **Indice de Eficiencia de Reencaminhamento**: Pontuacao de 0 a 100 com recomendacoes tecnicas priorizadas.

***

## Instalação e Execucao

Requer Python 3.8 ou superior, operando exclusivamente com a biblioteca padrao.

```bash
git clone https://github.com/TAVARDT-Portugal/redirect-301-tracker-pt.git
cd redirect-301-tracker-pt
python redirect_tracker.py https://empresa.pt
```

Para inspeção com saída estruturada em JSON:

```bash
python redirect_tracker.py https://empresa.pt -json
```

***

## Diagnostico Completo na Web

Para auditorias aprofundadas de redirecionamento:

* **Verificador de Redirecionamentos SEO Oficial**
* **[Portal Corporativo TAVARDT](https://ag.tavardt.com/pt/)**

***

## Consultoria em Migracoes Web e SEO Tecnico

Para operacoes de migracao e governanca de rotas sob Normas Europeias de Interoperabilidade e IETF RFC 9110, consulte a equipa da **TAVARDT Portugal**.

***

© 2026 TAVARDT Portugal. Todos os direitos reservados. Soberania e Defesa de Infraestrutura.

***

## Governança e Conformidade

* **Organização**: TAVARDT-Portugal
* **Jurisdição**: Portugal
* **Padrões de Referência**: Normas e frameworks técnicos auditados em estrita observância das regras de soberania.

Desenvolvido pela Divisão de Engenharia e Infraestrutura da TAVARDT Portugal. Todos os direitos reservados.

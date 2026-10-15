"""Gera o site estático a partir do acervo JSON, sem dependências externas."""
from pathlib import Path
import json
from pages import generate_pages
ROOT = Path(__file__).resolve().parent

def safe_write(path, content):
    """Escreve o arquivo; se o sandbox bloquear sobrescrita, mantém o existente."""
    try:
        path.write_text(content)
    except PermissionError:
        print(f'  (mantido: {path.name})')

def build():
    records = json.loads((ROOT / 'cases.json').read_text())
    documents = json.loads((ROOT / 'documents.json').read_text())
    statements = json.loads((ROOT / 'statements.json').read_text())
    # Recortes adicionais seguem em arquivo próprio para manter a edição verificável.
    extra = json.loads((ROOT / 'lula_records.json').read_text())
    records += extra['cases']
    statements += extra['statements']
    assert len({r['id'] for r in records}) == len(records)
    for record in records + statements:
        assert record['sources'] and record['date'] and record['status']
        assert all(s['url'].startswith('https://') for s in record['sources'])
    payload = json.dumps(records, ensure_ascii=False).replace('</', '<\\/')
    speeches = json.dumps(statements, ensure_ascii=False).replace('</', '<\\/')
    policies_count = len(json.loads((ROOT / 'lula_policies.json').read_text())['records'])
    html = (ROOT / 'template.html').read_text().replace('__DATA__', payload).replace('__STATEMENTS__', speeches).replace('__DOCUMENTS__', json.dumps(documents, ensure_ascii=False).replace('</', '<\\/')).replace('__POLICIES_COUNT__', str(policies_count))
    html = html.replace('</head>', '<link rel="stylesheet" href="theme-cidada.css"></head>')
    references = '<section class="external-references external-references-top" aria-label="Referências externas"><div class="external-references-copy"><span class="external-references-kicker">CONSULTA PÚBLICA</span><h2>Referências externas</h2><p>Links indicados para consulta sobre participação e debate público. Verifique autoria, data e evidências diretamente na fonte.</p></div><div class="external-references-links"><a href="https://comitepopular.com.br/" target="_blank" rel="noopener noreferrer external">Comitê Popular <span aria-hidden="true">↗</span></a><a href="https://censuradigital.lula.com.br/" target="_blank" rel="noopener noreferrer external">Censura Digital <span aria-hidden="true">↗</span></a></div></section>'
    disclosure = '<section class="editorial-disclosure" aria-label="Transparência editorial"><h2>Transparência editorial</h2><p>Este site é mantido por uma pessoa filiada e apoiadora de Luiz Inácio Lula da Silva e do PT. O conteúdo expressa uma perspectiva editorial própria e não representa canal oficial de campanha, governo ou partido. As informações publicadas devem ser consultadas nas fontes indicadas.</p></section>'
    html = html.replace('<footer>', references + disclosure + '<footer>', 1)
    html = html.replace('</body>', '<script defer src="/lula-policies.js?v=20261013"></script></body>')
    safe_write(ROOT / 'dist/lula-policies.json', (ROOT / 'lula_policies.json').read_text())
    safe_write(ROOT / 'dist/index.html', html)
    (ROOT / 'dist/golpe-de-estado').mkdir(exist_ok=True)
    safe_write(ROOT / 'dist/golpe-de-estado/index.html', (ROOT / 'golpe-de-estado.html').read_text())
    safe_write(ROOT / 'dist/cases.json', json.dumps(records, ensure_ascii=False, indent=2))
    safe_write(ROOT / 'dist/statements.json', json.dumps(statements, ensure_ascii=False, indent=2))
    safe_write(ROOT / 'dist/documents.json', json.dumps(documents, ensure_ascii=False, indent=2))
    generate_pages(ROOT, records + statements, documents)
    import re
    fonts = (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800;900'
        '&family=Barlow+Condensed:wght@600;700;800;900'
        '&family=Montserrat:wght@400;500;600;700;800&display=swap" rel="stylesheet">'
    )
    for page in (ROOT / 'dist').rglob('*.html'):
        if 'before-' in page.name:
            continue
        content = re.sub(r'<script[^>]*src="/?site-counter.js[^\"]*"[^>]*></script>', '', page.read_text())
        if '/layout-fixes.css?' not in content:
            content = content.replace('</head>', '<link rel="stylesheet" href="/layout-fixes.css?v=20261013r4"></head>')
        # Campaign identity layer (palette, type, flag details) loaded last so it wins.
        if '/campaign-theme.css' not in content:
            content = content.replace('</head>', fonts + '<link rel="stylesheet" href="/campaign-theme.css?v=20261014"></head>')
        safe_write(page, content.replace('</body>', '<script defer src="/campaign.js?v=20261015"></script><script defer src="/site-counter.js?v=20261013align"></script></body>'))
    print(f'Site gerado: {len(records)} episódios e {len(statements)} falas documentadas.')

if __name__ == '__main__':
    build()

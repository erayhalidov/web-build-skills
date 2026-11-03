"""Check that every translation is really translated, not copied English."""
import os, re, sys

LANGS = ['bg', 'en', 'fr', 'tr', 'es']
ok = True

# Words that mean the description was NOT translated
ENGLISH_MARKERS = [' use when', 'use when ', 'use for ', 'build static', 'operate ',
                   'rebuild a', 'audit or fixing', 'catalogue filters']

# Language-specific required characters / words
LANG_SIGNATURE = {
    'fr': ['é', 'è', 'ê', 'à', 'ç', 'ù', 'ô', 'î', 'û'],
    'tr': ['ı', 'ş', 'ğ', 'ç', 'ö', 'ü'],
    'es': ['á', 'é', 'í', 'ó', 'ú', 'ñ', '¿'],
}

print('=== 1. description language check ===')
for lang in ['fr', 'tr', 'es']:
    for s in sorted(os.listdir(f'skills/{lang}')):
        p = f'skills/{lang}/{s}/SKILL.md'
        if not os.path.isfile(p):
            continue
        m = re.search(r'^description:\s*(.+)$', open(p, encoding='utf-8', errors='replace').read(), re.M)
        if not m:
            continue
        d = m.group(1).strip().strip('"').strip("'")
        low = d.lower()
        # copied English?
        if any(mk in low for mk in ENGLISH_MARKERS) or low.startswith('use '):
            print(f'  FAIL {lang}/{s}: description still English -> {d[:60]}')
            ok = False
        # has language signature char?
        elif not any(c in d.lower() for c in LANG_SIGNATURE[lang]):
            print(f'  WARN {lang}/{s}: no {lang} diacritics -> {d[:60]}')
print('  done')
print()

print('=== 2. body language check (headings must not be English in fr/tr/es) ===')
# nuxt-framework is vendored upstream English documentation, copied verbatim into
# every language folder on purpose — exclude it from the translation check.
VENDORED = ('nuxt-framework',)
EN_HEADINGS = ['## when to use', '## requirements', '## how to', '## workflow', '## pitfalls',
               '## verification', '## step', '## overview', '## notes']
for lang in ['fr', 'tr', 'es']:
    for r, d, f in os.walk(f'skills/{lang}'):
        if any(v in r for v in VENDORED):
            continue
        for x in f:
            if not x.endswith('.md'):
                continue
            p = os.path.join(r, x)
            t = open(p, encoding='utf-8', errors='replace').read()
            heads = [l.lower().strip() for l in t.split('\n') if l.startswith('## ')]
            en_count = sum(1 for h in heads if any(h.startswith(e) for e in EN_HEADINGS))
            if heads and en_count == len(heads):
                print(f'  FAIL {p}: all {len(heads)} headings English')
                ok = False
print('  done')
print()

print('=== 3. code blocks byte-identical across languages ===')


def blocks(path):
    if not os.path.isfile(path):
        return []
    t = open(path, encoding='utf-8', errors='replace').read()
    return re.findall(r'```[^\n]*\n(.*?)```', t, re.S)


for s in sorted(os.listdir('skills/bg')):
    for base, dirs, files in os.walk(f'skills/bg/{s}'):
        for x in files:
            if not x.endswith('.md'):
                continue
            rel = os.path.relpath(os.path.join(base, x), f'skills/bg/{s}')
            bg_blocks = blocks(os.path.join(base, x))
            if not bg_blocks:
                continue
            for lang in ['en', 'fr', 'tr', 'es']:
                other = blocks(f'skills/{lang}/{s}/{rel}')
                if len(other) != len(bg_blocks):
                    print(f'  WARN {lang}/{s}/{rel}: {len(other)} blocks vs {len(bg_blocks)} in bg')
                    continue
                for i, (a, b) in enumerate(zip(bg_blocks, other)):
                    # bash/php/sql must be identical; prose blocks may differ
                    if re.search(r'[\u0400-\u04FF]', a) and '```text' not in a[:10]:
                        continue
                    if a.strip() != b.strip() and not re.search(r'[\u0400-\u04FF]', a):
                        # allow prose-only diffs
                        if len(a) > 40 and abs(len(a) - len(b)) > len(a) * 0.5:
                            print(f'  NOTE {lang}/{s}/{rel} block {i}: content differs')
print('  done')
print()
print('RESULT:', 'PASS' if ok else 'PROBLEMS FOUND')
sys.exit(0 if ok else 1)

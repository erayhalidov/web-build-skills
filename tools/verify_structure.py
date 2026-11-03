import os, re, sys

LANGS = ['bg', 'en', 'fr', 'tr', 'es']
ok = True


def skill_dirs(lang):
    base = f'skills/{lang}'
    if not os.path.isdir(base):
        return []
    return sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)))


bg_skills = skill_dirs('bg')
print(f'BG skills: {len(bg_skills)}')
print()

# 1. same skill set in every language
for lang in LANGS:
    got = skill_dirs(lang)
    if got != bg_skills:
        print(f'FAIL {lang}: skill set differs -> {set(got) ^ set(bg_skills)}')
        ok = False
print('1. skill sets identical:', 'OK' if ok else 'FAIL')
print()

# 2. same file count per skill
bad = []
for s in bg_skills:
    counts = {}
    for lang in LANGS:
        p = f'skills/{lang}/{s}'
        counts[lang] = sum(1 for r, d, f in os.walk(p) for x in f) if os.path.isdir(p) else 0
    if len(set(counts.values())) != 1:
        bad.append((s, counts))
print('2. file counts per skill:', 'OK' if not bad else 'FAIL')
for s, c in bad:
    print('   ', s, c)
if bad:
    ok = False
print()

# 3. name: field identical across languages
bad = []
for s in bg_skills:
    p = f'skills/bg/{s}/SKILL.md'
    if not os.path.isfile(p):
        continue
    m = re.search(r'^name:\s*(\S+)', open(p, encoding='utf-8', errors='replace').read(), re.M)
    if not m:
        continue
    base = m.group(1)
    for lang in ['en', 'fr', 'tr', 'es']:
        q = f'skills/{lang}/{s}/SKILL.md'
        if not os.path.isfile(q):
            bad.append(f'missing {q}')
            continue
        m2 = re.search(r'^name:\s*(\S+)', open(q, encoding='utf-8', errors='replace').read(), re.M)
        if not m2 or m2.group(1) != base:
            bad.append(f'{lang}/{s}: {m2.group(1) if m2 else "?"} != {base}')
print('3. name fields match:', 'OK' if not bad else 'FAIL')
for b in bad[:5]:
    print('   ', b)
if bad:
    ok = False
print()

# 4. no cyrillic left in translations
bad = {}
for lang in ['en', 'fr', 'tr', 'es']:
    tot = 0
    for r, d, f in os.walk(f'skills/{lang}'):
        for x in f:
            if x.endswith('.md'):
                tot += len(re.findall(r'[\u0400-\u04FF]',
                                      open(os.path.join(r, x), encoding='utf-8', errors='replace').read()))
    bad[lang] = tot
print('4. cyrillic remaining:', 'OK' if all(v == 0 for v in bad.values()) else 'FAIL', bad)
if any(v > 0 for v in bad.values()):
    ok = False
print()

# 5. descriptions <= 60 chars in every language
bad = []
for lang in LANGS:
    for s in bg_skills:
        p = f'skills/{lang}/{s}/SKILL.md'
        if not os.path.isfile(p):
            continue
        m = re.search(r'^description:\s*(.+)$', open(p, encoding='utf-8', errors='replace').read(), re.M)
        if not m:
            continue
        d = m.group(1).strip().strip('"').strip("'")
        if len(d) > 60:
            bad.append(f'{lang}/{s}: {len(d)} chars')
print('5. descriptions <=60 chars:', 'OK' if not bad else 'FAIL')
for b in bad[:8]:
    print('   ', b)
if bad:
    ok = False
print()

# 6. no secrets / personal data anywhere
patterns = ['halidov', 'eray', 'battleborn', '206693403', '0243245045', 'my-agro', 'oem.bg',
            'powerparts', 'loveadults', 'ercoknives', 'ercopc', '178.217.', 'kucoin', 'binance',
            'PRIVATE KEY', 'password=', 'api_key=', 'office@', '@gmail']
leaks = []
for r, d, f in os.walk('skills'):
    for x in f:
        p = os.path.join(r, x)
        try:
            t = open(p, encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        low = t.lower()
        for pat in patterns:
            if pat.lower() in low:
                leaks.append(f'{p}: {pat}')
print('6. leak scan:', 'OK' if not leaks else f'FAIL ({len(leaks)})')
for l in leaks[:8]:
    print('   ', l)
if leaks:
    ok = False
print()

total_files = sum(1 for r, d, f in os.walk('skills') for x in f)
print(f'TOTAL files: {total_files}')
print()
print('RESULT:', 'ALL CHECKS PASS' if ok else 'PROBLEMS FOUND')
sys.exit(0 if ok else 1)

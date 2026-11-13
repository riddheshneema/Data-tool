"""Point the workspace scripts at this checkout. Run it once after cloning, and again if you move the folder:

    python3 workspace/fix_paths.py

The scripts were written in a cloud container and use absolute paths. This rewrites those paths to
match this machine. It remembers the last paths it wrote in .paths.json, so it is safe to run again."""
import glob, json, os, re
W = os.path.dirname(os.path.abspath(__file__)) + '/'                    # .../Data-tool/workspace/
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'  # .../Data-tool/
cfg_f = W + '.paths.json'
old = json.load(open(cfg_f))
pat = re.compile('|'.join(re.escape(p) for p in sorted({old['workspace'], old['repo']}, key=len, reverse=True)))
new = {old['workspace']: W, old['repo']: REPO}
n = 0
for f in glob.glob(W + '**/*.py', recursive=True) + glob.glob(W + '**/*.js', recursive=True):
    if os.path.abspath(f) == os.path.abspath(__file__): continue
    t = open(f, encoding='utf-8').read()
    u = pat.sub(lambda m: new[m.group(0)], t)
    if u != t:
        open(f, 'w', encoding='utf-8').write(u); n += 1
json.dump({'workspace': W, 'repo': REPO}, open(cfg_f, 'w'), indent=1)
print(f'updated {n} files\n  workspace -> {W}\n  repo      -> {REPO}')

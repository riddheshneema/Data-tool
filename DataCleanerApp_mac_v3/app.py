import streamlit as st
import pandas as pd
import numpy as np
import io, os, re, json, yaml, hashlib, datetime, glob, subprocess, platform, shutil, hmac
import sqlite3, math
from rapidfuzz import process, fuzz
try:
    from rapidfuzz.distance import Levenshtein as RFLev
    def levenshtein(a, b): return RFLev.distance(a, b)
except Exception:
    def levenshtein(a, b):
        a = str(a); b = str(b)
        dp = list(range(len(b)+1))
        for i, ca in enumerate(a, 1):
            prev = dp[0]; dp[0] = i
            for j, cb in enumerate(b, 1):
                cur = dp[j]
                dp[j] = min(prev + (ca != cb), dp[j] + 1, dp[j-1] + 1)
                prev = cur
        return dp[-1]
from openpyxl import load_workbook  # used in "Other tools" Intake Split

# =========================================================
# VERSION / PATHS
# =========================================================
APP_VERSION = "6.30 (Built-in login; AI vector reuse + SQLite cache; per-run tokens; Rule Generator; wide AI panel; export/import; collapsible sections; deterministic enrichment; caching)"
BASE_STORE_DIR      = "store"
PROJECTS_DIR        = os.path.join(BASE_STORE_DIR, "projects")
GLOBAL_ASSETS_DIR   = os.path.join(BASE_STORE_DIR, "assets")
GLOBAL_MEMORY_PATH  = os.path.join(BASE_STORE_DIR, "global_mapping_memory.yaml")

os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(GLOBAL_ASSETS_DIR, exist_ok=True)
os.makedirs(BASE_STORE_DIR, exist_ok=True)

OUTPUT_ROOT = "output"
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# AI persistence and embeddings
AI_DB_PATH = os.path.join(BASE_STORE_DIR, "ai_cache.sqlite")
EMBEDDING_MODEL = "text-embedding-3-small"
SIMILARITY_DEFAULT = 0.80

# Per project file names
TEMPLATE_FILE   = "template.xlsx"
ENRICH_FILE     = "enrichment.yaml"
MAPPING_FILE    = "mapping.yaml"
RUN_META_FILE   = "run_meta.yaml"
OVERRIDES_FILE  = "enrichment_overrides.yaml"
LAST_PROCESSED  = "last_processed.xlsx"
SNAPSHOT_PROCESSED = "snapshot_processed.csv"
SNAPSHOT_AUDIT     = "snapshot_audit.csv"

GLOBAL_LOGO_BASENAME = "logo"  # stored as logo.png / logo.jpg

# =========================================================
# SESSION DEFAULTS
# =========================================================
SESSION_DEFAULTS = {
    "active_project": None,
    "raw_df": None,
    "processed_df": None,
    "enrich_audit_df": None,
    "flagged_df": None,
    "run_meta": None,
    "global_memory": None,
    "overrides": None,
    "mapping": {},
    "logo_path": None,
    "last_processing_targets": [],
    # Overrides UI state
    "ov_selected_target": None,
    "ov_selected_fields": [],
    "add_rule_kw": "",
    "ov_wrap_text": False,
    "last_comp": None,         # comparison analytics cache
    # Merge state
    "merge_folder": "",
    "merge_output_bytes": None,
    "merge_output_name": "",
    # UI toggles
    "show_delete_dropdown": False,
    "other_tools_selected": "",
    # Bulk populate rules
    "bulk_groups": [
        {
            "target_col": "",
            "target_vals": [],
            "populate_col": "",
            "new_populate_col": "",
            "value": "",
            "filter_col": "",
            "filter_op": "",
            "filter_val": ""
        }
    ],
    # Mapping suggestion cache (headers-only)
    "map_sim_cache": {},   # {headers_hash: {template_col: [(raw_col,score), ...]}}
    # AI Suggestions panel
    "ai_cache": {},        # (proj,target,rowIndex,ctxHash,model)-> {suggested_value,confidence,rationale,new_keywords,suggested_weight}
    "ai_tokens_used": {"input":0, "output":0, "cached":0},         # cumulative
    "ai_last_run_tokens": {"input":0,"output":0,"cached":0,"total":0}, # last run
    "ai_form_state": {
        "target": None,
        "model": "gpt-4o-mini",
        "temperature": 0.2,
        "row_cap": 500,
        "statuses": ["UNCLASSIFIED","MULTI"],
        "fields_to_show": [],
        "refresh_cache": False
    },
    "ai_table_state": { "records": [] },  # current suggestion rows
    "ai_sel_rows": [],                    # row indexes checked for Apply Override?
    "ai_undo": [],                        # [{"target":..., "changes":[{row,old,new}], "rules_added":[...]}]
    "ai_redo": [],
    # Simple Auth
    "authentication_status": None,  # True/False/None
    "username": None,
    "name": None,
}
def ensure_session_keys():
    for k, v in SESSION_DEFAULTS.items():
        if k not in st.session_state:
            if isinstance(v, list):
                st.session_state[k] = [json.loads(json.dumps(x)) if isinstance(x, dict) else x for x in v]
            elif isinstance(v, dict):
                st.session_state[k] = json.loads(json.dumps(v))
            else:
                st.session_state[k] = v
ensure_session_keys()

# =========================================================
# UI CONFIG & STYLE
# =========================================================
st.set_page_config(page_title="Learner Connect Data Optimising Tool", layout="wide", page_icon="🎓")

STYLE = """
<style>
html, body, .stApp {font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont,'Segoe UI',Roboto;}
h1,h2,h3,h4 {font-weight:600; letter-spacing:.25px;}
:root {
  --bg:#ffffff;
  --bg-alt:#f5f7fa;
  --panel:#ffffff;
  --border:#dbe2ea;
  --accent:#1f5fa0;
  --accent2:#3293d8;
  --muted:#647687;
  --multi:#fff4c6;
  --none:#dfefff;
  --override:#eceff1;
}
.stApp {background:var(--bg);}

/* Simple cards */
.section-box { background:var(--panel); border:1px solid var(--border); padding:14px 16px; border-radius:14px; margin-bottom:16px; box-shadow:0 1px 2px rgba(0,0,0,0.04); }
.inline-note {font-size:11px; opacity:.65;}

/* Wrap for dataframes/editors */
[data-testid="stDataFrame"] [role="row"] { align-items: start !important; }
[data-testid="stDataFrame"] div[role="gridcell"],
[data-testid="stDataFrame"] td div,
[data-testid="stDataFrame"] .cell {
  white-space: normal !important;
  overflow-wrap: anywhere !important;
  word-break: break-word !important;
  line-height: 1.25 !important;
}
[data-testid="stDataFrame"] [role="row"] {
  height: auto !important;
  min-height: 28px !important;
}

/* Mapping grid */
.mapping-grid-head, .mapping-grid-row { display:grid; grid-template-columns: 280px 1fr 90px; gap:10px; align-items:center; }
.mapping-grid-head { background:var(--bg-alt); border:1px solid var(--border); border-radius:12px 12px 0 0; padding:10px 12px; font-size:12px; font-weight:600; text-transform:uppercase; color:var(--muted); }
.mapping-grid-body { border:1px solid var(--border); border-top:none; border-radius:0 0 12px 12px; overflow:hidden; }
.mapping-grid-row { padding:8px 12px; border-bottom:1px solid #edf1f5; font-size:13px; }
.mapping-grid-row:nth-child(even){background:#fafbfd;}
.mapping-grid-row:hover {background:#f2f7fc;}
.badge { display:inline-block; padding:2px 6px; border:1px solid #e0e4ea; border-radius:8px; margin-right:6px; font-size:11px; color:#4a5663; background:#fafbfc;}

/* Logo */
.logo-wrap { position:relative; display:inline-block; }
.logo-wrap img { max-height:100px; border-radius:10px; box-shadow:0 2px 6px rgba(0,0,0,.08); }
.logo-close { position:absolute; top:-8px; right:-8px; width:20px; height:20px; border-radius:50%; background:#ff6b6b; color:#fff; border:none; font-size:14px; line-height:20px; text-align:center; cursor:pointer; box-shadow:0 1px 3px rgba(0,0,0,.2); }
.logo-close:hover { background:#e65a5a; }

/* Compact toolbar (single line) */
.toolbar { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
.toolbar .stButton>button, .toolbar .stDownloadButton>button { padding:6px 10px; font-size:12px; }
.toolbar .stCheckbox { margin-top:2px; }

/* Reduce default button padding globally a bit */
.stButton>button { padding:6px 10px; }
.stDownloadButton>button { padding:6px 10px; }

footer, .viewerBadge_container__1QSob {display:none;}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

# =========================================================
# HELPERS
# =========================================================
def safe_float(x, default=1.0):
    if x is None: return default
    if isinstance(x, (int, float)): return float(x)
    sx = str(x).strip()
    if sx == "": return default
    try:
        return float(sx)
    except:
        return default

def load_yaml(path):
    if not os.path.exists(path): return {}
    try:
        with open(path, "r") as f: return yaml.safe_load(f) or {}
    except: return {}

def save_yaml(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f: yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

def safe_read_excel(obj):
    try: return pd.read_excel(obj)
    except Exception as e:
        st.error(f"Failed to read Excel: {e}")
        return None

def ensure_columns(df, cols):
    for c in cols:
        if c not in df.columns: df[c] = ""
    return df[[c for c in cols]]

def project_dir(name): return os.path.join(PROJECTS_DIR, name)
def project_file(name, filename): return os.path.join(project_dir(name), filename)
def ensure_project(name): os.makedirs(project_dir(name), exist_ok=True)

# Raw uploads memory (keep last 5)
def raw_uploads_dir(project): return project_file(project, "raw_uploads")
def ensure_raw_uploads(project):
    d = raw_uploads_dir(project)
    os.makedirs(d, exist_ok=True)
    return d
def list_recent_raw_uploads(project, limit=5):
    d = ensure_raw_uploads(project)
    files = [os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith(".xlsx")]
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    out=[]
    for p in files[:limit]:
        try: ts = datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M")
        except: ts = ""
        out.append({"path": p, "name": os.path.basename(p), "ts": ts})
    return out
def save_uploaded_raw_copy(project, uploaded_file):
    d = ensure_raw_uploads(project)
    base = os.path.basename(uploaded_file.name)
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(d, f"{ts}__{base}")
    with open(path, "wb") as f: f.write(uploaded_file.getbuffer())
    files = [os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith(".xlsx")]
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    for p in files[5:]:
        try: os.remove(p)
        except: pass
    return path

# Global mapping memory
def load_global_memory():
    if st.session_state["global_memory"] is None:
        mem = load_yaml(GLOBAL_MEMORY_PATH)
        if not mem: mem = {"pairs":[]}
        st.session_state["global_memory"] = mem
    return st.session_state["global_memory"]
def save_global_memory(mem): save_yaml(GLOBAL_MEMORY_PATH, mem)
def update_global_memory(template_col, raw_col):
    mem = load_global_memory()
    for p in mem["pairs"]:
        if p["template_col"] == template_col and p["raw_col"] == raw_col:
            p["count"] += 1; break
    else:
        mem["pairs"].append({"template_col": template_col, "raw_col": raw_col, "count": 1})
    save_global_memory(mem)
def suggest_from_global(template_col, raw_cols):
    mem = load_global_memory()
    cands = [p for p in mem["pairs"] if p["template_col"] == template_col and p["raw_col"] in raw_cols]
    if not cands: return None
    cands.sort(key=lambda x: x.get("count",0), reverse=True)
    return cands[0]["raw_col"]

# Enrichment config
def load_enrichment(project):
    path = project_file(project, ENRICH_FILE)
    data = load_yaml(path) or {}
    data.setdefault("targets", {})
    for tgt, node in data["targets"].items():
        node.setdefault("sources", [])
        node.setdefault("rules", [])
        fixed=[]
        for r in node["rules"]:
            fixed.append({
                "output_value": r.get("output_value",""),
                "keyword": r.get("keyword",""),
                "weight": safe_float(r.get("weight",5.0), 5.0),
                "regex": False, "fuzzy": False
            })
        node["rules"] = fixed
    return data
def save_enrichment(project, cfg):
    save_yaml(project_file(project, ENRICH_FILE), cfg)

# Deterministic enrichment
def build_prepared_rules(enrichment_cfg):
    prepared = {}
    for tgt, node in enrichment_cfg.get("targets", {}).items():
        pr=[]
        for r in node.get("rules", []):
            ov = str(r.get("output_value","")).strip()
            kw = str(r.get("keyword","")).strip().lower()
            if ov and kw:
                pr.append((ov, kw, safe_float(r.get("weight",5.0), 5.0)))
        prepared[tgt] = pr
    return prepared

def classify_context(ctx_lc: str, rules_list: list):
    if not rules_list:
        return {"value":"", "status":"UNCLASSIFIED", "winners":[], "totals":{}, "matched":{}, "audit_str":"No matching keyword"}
    totals={}; matched={}
    for ov, kw_l, w in rules_list:
        if kw_l and kw_l in ctx_lc:
            totals[ov] = totals.get(ov, 0.0) + w
            matched.setdefault(ov, []).append(kw_l)
    if not totals:
        return {"value":"", "status":"UNCLASSIFIED", "winners":[], "totals":{}, "matched":{}, "audit_str":"No matching keyword"}
    min_w = min(totals.values())
    winners = sorted(set([ov for ov, tw in totals.items() if tw == min_w]))
    value = ", ".join(winners)
    status = "OK" if len(winners)==1 else "MULTI"
    parts=[]
    for ov in winners:
        kws = ", ".join(sorted(set(matched.get(ov, []))))
        parts.append(f"{ov}: {kws}" if kws else f"{ov}:")
    return {"value": value, "status": status, "winners": winners, "totals": totals, "matched": matched, "audit_str": " | ".join(parts)}

# Overrides I/O + reset
def load_overrides(project):
    path = project_file(project, OVERRIDES_FILE)
    ov = load_yaml(path)
    if not ov: ov = {"overrides": {}}
    ov.setdefault("overrides", {})
    return ov
def save_overrides(project, ov): save_yaml(project_file(project, OVERRIDES_FILE), ov)
def apply_overrides_to_processed(processed_df, audit_df, overrides):
    if not overrides or "overrides" not in overrides: return processed_df, audit_df
    if audit_df is None or audit_df.empty: return processed_df, audit_df
    for tgt, m in overrides["overrides"].items():
        vcol = f"{tgt}_Value"; scol = f"{tgt}_Status"
        if tgt not in processed_df.columns or vcol not in audit_df.columns or scol not in audit_df.columns: continue
        for ridx_str, meta in m.items():
            try: ridx = int(ridx_str)
            except: continue
            new_val = meta.get("new_value","")
            if new_val == "": continue
            if 0 <= ridx < len(processed_df):
                processed_df.at[ridx, tgt] = new_val
            mask = (audit_df["RowIndex"] == ridx)
            audit_df.loc[mask, vcol]  = new_val
            audit_df.loc[mask, scol]  = "OVERRIDE"
    return processed_df, audit_df
def reset_overrides_for_project(project, backup=True):
    ov_path = project_file(project, OVERRIDES_FILE)
    if backup and os.path.exists(ov_path):
        try:
            ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            shutil.copyfile(ov_path, ov_path + f".bak_{ts}")
        except Exception:
            pass
    save_overrides(project, {"overrides": {}})
    if st.session_state.get("processed_df") is not None and st.session_state.get("enrich_audit_df") is not None:
        p2, a2 = apply_overrides_to_processed(
            st.session_state["processed_df"].copy(),
            st.session_state["enrich_audit_df"].copy(),
            {"overrides": {}}
        )
        st.session_state["processed_df"] = p2
        st.session_state["enrich_audit_df"] = a2

# Export Excel
def export_excel(final_df, flagged_df, audit_df, meta, project):
    clean = final_df.copy()
    clean = clean[~clean.replace("", np.nan).isna().all(axis=1)].reset_index(drop=True)
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
        clean.to_excel(writer, "Final", index=False)
        if not flagged_df.empty: flagged_df.to_excel(writer, "Flagged", index=False)
        if audit_df is not None and not audit_df.empty: audit_df.to_excel(writer, "Enrichment_Audit", index=False)
        meta_df = pd.DataFrame([(k,v) for k,v in meta.items()], columns=["Key","Value"])
        meta_df.to_excel(writer, "Metadata", index=False)
        if audit_df is not None and not audit_df.empty:
            wb = writer.book; ws = writer.sheets["Enrichment_Audit"]
            yellow = wb.add_format({"bg_color":"#FFF4C6"})
            blue   = wb.add_format({"bg_color":"#DFEFFF"})
            grey   = wb.add_format({"bg_color":"#ECEFF1"})
            status_cols = [c for c in audit_df.columns if c.endswith("_Status")]
            rows=len(audit_df)
            for col in status_cols:
                cidx = audit_df.columns.get_loc(col)
                ws.conditional_format(1,cidx,rows,cidx,{"type":"text","criteria":"containing","value":"MULTI","format":yellow})
                ws.conditional_format(1,cidx,rows,cidx,{"type":"text","criteria":"containing","value":"UNCLASSIFIED","format":blue})
                ws.conditional_format(1,cidx,rows,cidx,{"type":"text","criteria":"containing","value":"OVERRIDE","format":grey})
    bio.seek(0)
    with open(project_file(project, LAST_PROCESSED), "wb") as f:
        f.write(bio.getbuffer())
    return bio

# Progress
def progress_component():
    bar = st.empty(); pct = st.empty()
    def update(p, label=""):
        p = min(max(p,0),100)
        bar.markdown(f"<div style='background:#e9edf1;height:16px;border-radius:10px;overflow:hidden;width:100%;'><div style='height:100%;background:linear-gradient(90deg,#1f5fa0,#3293d8);width:{p}%;transition:width .35s;'></div></div>", unsafe_allow_html=True)
        pct.markdown(f"<div style='font-size:12px;margin-top:4px;color:#647687;'>Progress: {p:.0f}% {label}</div>", unsafe_allow_html=True)
    return update

# Logo helpers
def save_logo(uploaded):
    if not uploaded: return
    ext = os.path.splitext(uploaded.name)[1].lower()
    if ext not in [".png",".jpg",".jpeg"]:
        st.error("Logo must be PNG or JPG"); return
    for f in os.listdir(GLOBAL_ASSETS_DIR):
        if f.startswith(GLOBAL_LOGO_BASENAME):
            try: os.remove(os.path.join(GLOBAL_ASSETS_DIR, f))
            except: pass
    path = os.path.join(GLOBAL_ASSETS_DIR, GLOBAL_LOGO_BASENAME+ext)
    with open(path,"wb") as f: f.write(uploaded.getbuffer())
    st.session_state["logo_path"] = path
    st.toast("Logo uploaded.")
def current_logo():
    p = st.session_state.get("logo_path")
    if p and os.path.exists(p): return p
    for f in os.listdir(GLOBAL_ASSETS_DIR):
        if f.startswith(GLOBAL_LOGO_BASENAME) and f.lower().endswith((".png",".jpg",".jpeg")):
            st.session_state["logo_path"] = os.path.join(GLOBAL_ASSETS_DIR, f)
            return st.session_state["logo_path"]
    return None

# OpenAI client
def get_openai_client():
    try:
        from openai import OpenAI
    except Exception:
        return None, "OpenAI SDK not installed. Run: pip install openai>=1.0.0"
    api_key = os.environ.get("OPENAI_API_KEY") or (st.secrets.get("OPENAI_API_KEY") if hasattr(st, "secrets") else None)
    if not api_key: return None, "Missing OPENAI_API_KEY. Add it to environment or Streamlit secrets."
    try:
        client = OpenAI(api_key=api_key); return client, None
    except Exception as e:
        return None, f"Failed to init OpenAI client: {e}"

def build_row_context(raw_row, target_sources):
    if target_sources:
        parts = [str(raw_row.get(c, "")) for c in target_sources if c in raw_row.index]
    else:
        parts = [str(raw_row[c]) for c in raw_row.index]
    return " ".join([p for p in parts if p and p.strip()])[:1024]

def context_hash(target: str, ctx: str, matched: dict) -> str:
    base = json.dumps({"t": target, "c": ctx, "m": matched or {}}, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(base.encode("utf-8")).hexdigest()

# =========================================================
# AI Persistent Cache (SQLite) + Embeddings helpers
# =========================================================
def init_ai_db():
    try:
        conn = sqlite3.connect(AI_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT NOT NULL,
            target TEXT NOT NULL,
            model TEXT NOT NULL,
            ctx_hash TEXT NOT NULL,
            ctx TEXT NOT NULL,
            embedding TEXT NOT NULL,
            suggested_value TEXT NOT NULL,
            confidence REAL NOT NULL,
            rationale TEXT,
            new_keywords TEXT,
            suggested_weight REAL,
            created_at TEXT NOT NULL,
            UNIQUE(project, target, model, ctx_hash)
        )
        """)
        conn.commit()
    finally:
        try: conn.close()
        except: pass

def ai_db_upsert_suggestion(project, target, model, ctx_hash, ctx, embedding, rec):
    try:
        conn = sqlite3.connect(AI_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        INSERT OR REPLACE INTO suggestions
        (project, target, model, ctx_hash, ctx, embedding, suggested_value, confidence, rationale, new_keywords, suggested_weight, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            str(project), str(target), str(model), str(ctx_hash), str(ctx),
            json.dumps(embedding or []),
            str(rec.get("suggested_value","")),
            float(rec.get("confidence", 0.0) or 0.0),
            str(rec.get("rationale","") or ""),
            json.dumps(rec.get("new_keywords",[]) or []),
            float(rec.get("suggested_weight", 3.0) or 3.0),
            datetime.datetime.utcnow().isoformat()
        ))
        conn.commit()
    except Exception:
        pass
    finally:
        try: conn.close()
        except: pass

def ai_db_get_exact(project, target, model, ctx_hash):
    try:
        conn = sqlite3.connect(AI_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT suggested_value, confidence, rationale, new_keywords, suggested_weight
            FROM suggestions
            WHERE project=? AND target=? AND model=? AND ctx_hash=?
            LIMIT 1
        """, (str(project), str(target), str(model), str(ctx_hash)))
        row = cur.fetchone()
        if not row:
            return None
        sv, conf, rat, kws_json, w = row
        return {
            "suggested_value": sv or "",
            "confidence": float(conf or 0.0),
            "rationale": rat or "",
            "new_keywords": json.loads(kws_json or "[]"),
            "suggested_weight": float(w or 3.0)
        }
    except Exception:
        return None
    finally:
        try: conn.close()
        except: pass

def ai_db_get_nearest_for_target(project, target, model, limit=300):
    try:
        conn = sqlite3.connect(AI_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT ctx_hash, ctx, embedding, suggested_value, confidence, rationale, new_keywords, suggested_weight
            FROM suggestions
            WHERE project=? AND target=? AND model=?
            ORDER BY id DESC
            LIMIT ?
        """, (str(project), str(target), str(model), int(limit)))
        rows = cur.fetchall()
        out = []
        for r in rows:
            ch, ctx, emb_json, sv, conf, rat, kws_json, w = r
            try:
                emb = json.loads(emb_json or "[]")
            except:
                emb = []
            out.append({
                "ctx_hash": ch,
                "ctx": ctx,
                "embedding": emb,
                "rec": {
                    "suggested_value": sv or "",
                    "confidence": float(conf or 0.0),
                    "rationale": rat or "",
                    "new_keywords": json.loads(kws_json or "[]"),
                    "suggested_weight": float(w or 3.0),
                }
            })
        return out
    except Exception:
        return []
    finally:
        try: conn.close()
        except: pass

def cosine_similarity(v1, v2):
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = 0.0; n1 = 0.0; n2 = 0.0
    for a, b in zip(v1, v2):
        dot += (a * b); n1 += (a*a); n2 += (b*b)
    if n1 == 0.0 or n2 == 0.0:
        return 0.0
    return dot / (math.sqrt(n1) * math.sqrt(n2))

def get_embedding(client, text: str) -> list:
    if client is None or not text:
        return []
    try:
        resp = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
        vec = resp.data[0].embedding
        return list(vec) if vec else []
    except Exception:
        return []

# Initialize persistent AI cache (SQLite)
try:
    init_ai_db()
except Exception:
    pass

# =========================================================
# SIMPLE LOGIN (no external dependency)
# Username: admin@leareraid.com
# Password: Studyusa@1234
# You can override via Streamlit secrets: AUTH_USERNAME / AUTH_PASSWORD
# =========================================================
def get_valid_credentials():
    user = "admin@learneraid.com"
    pwd  = "Studyusa@1234"
    try:
        if hasattr(st, "secrets"):
            user = st.secrets.get("AUTH_USERNAME", user)
            pwd  = st.secrets.get("AUTH_PASSWORD", pwd)
    except Exception:
        pass
    return str(user), str(pwd)

def check_credentials(input_user: str, input_pwd: str) -> bool:
    valid_user, valid_pwd = get_valid_credentials()
    return hmac.compare_digest(input_user.strip(), valid_user) and hmac.compare_digest(input_pwd, valid_pwd)

def render_login():
    st.title("Sign in")
    with st.form("login_form", clear_on_submit=False):
        u = st.text_input("Email", value="", autocomplete="username")
        p = st.text_input("Password", value="", type="password", autocomplete="current-password")
        remember = st.checkbox("Remember me", value=False)
        submitted = st.form_submit_button("Sign in")
    if submitted:
        if check_credentials(u, p):
            st.session_state["authentication_status"] = True
            st.session_state["username"] = u
            st.session_state["name"] = u.split("@")[0].title()
            if remember:
                st.session_state["remember_me"] = True
            st.success("Signed in.")
            st.rerun()
        else:
            st.error("Invalid credentials.")
    st.stop()

# Gate the app
if st.session_state.get("authentication_status") is not True:
    render_login()

# Sidebar: Logout
with st.sidebar:
    if st.button("Logout"):
        for k in ["authentication_status","username","name","remember_me"]:
            st.session_state.pop(k, None)
        st.success("Signed out.")
        st.rerun()
    if st.session_state.get("username"):
        st.caption(f"Signed in as: {st.session_state.get('username')}")

# =========================================================
# TUTORIAL / NAV (ONLY AFTER AUTH)
# =========================================================
def render_tutorial():
    st.markdown("1) Welcome / Tutorial\n2) Project Setup\n3) Upload Raw\n4) Map Fields\n5) Enrichment Setup\n6) Run Processing\n7) Overrides & Analytics\n8) Post-Processing\n9) Download & Review\n10) Other tools")

steps = [
    "0. Welcome / Tutorial",
    "1. Project Setup",
    "2. Upload Raw",
    "3. Map Fields",
    "4. Enrichment Setup",
    "5. Run Processing",
    "6. Overrides & Analytics",
    "7. Post-Processing",
    "8. Download & Review",
    "9. Other tools"
]
current_step = st.sidebar.radio("Flow", steps, index=0)

with st.sidebar.expander("Project Status", expanded=False):
    st.write("Active Project:", st.session_state["active_project"] or "None")
    proj = st.session_state["active_project"]
    if proj:
        template_exists = os.path.exists(project_file(proj, TEMPLATE_FILE))
        enrichment_exists= os.path.exists(project_file(proj, ENRICH_FILE))
        mapping_exists  = os.path.exists(project_file(proj, MAPPING_FILE))
        override_exists = os.path.exists(project_file(proj, OVERRIDES_FILE))
        st.write("Template:", "✅" if template_exists else "⏳")
        st.write("Mapping:", "✅" if mapping_exists else "⏳")
        st.write("Enrichment:", "✅" if enrichment_exists else "⏳")
        st.write("Overrides:", "✅" if override_exists else "─")
st.sidebar.caption(f"Version {APP_VERSION}")

# =========================================================
# STEP 0: Welcome (logo)
# =========================================================
if current_step == "0. Welcome / Tutorial":
    colL, colR = st.columns([1,3])
    with colL:
        logo = current_logo()
        if logo:
            st.markdown("<div class='logo-wrap'>", unsafe_allow_html=True)
            st.image(logo, use_container_width=True)
            if st.button("×", key="logo_close_btn", help="Remove logo", type="secondary"):
                try: os.remove(logo)
                except: pass
                st.session_state["logo_path"] = None
                st.toast("Logo removed.")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            up_logo = st.file_uploader("Upload Logo", type=["png","jpg","jpeg"])
            if up_logo: save_logo(up_logo)
    with colR:
        st.title("Learner Connect Data Optimising Tool")
        render_tutorial()
    st.info("Proceed to '1. Project Setup'.")

# =========================================================
# STEP 1: Project Setup
# =========================================================
elif current_step == "1. Project Setup":
    st.title("Project Setup & Template")
    projects = sorted([d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(project_dir(d))])
    col1, col2 = st.columns([2,1])
    with col1:
        sel = st.selectbox(
            "Select Project",
            [""]+projects,
            index=([""]+projects).index(st.session_state["active_project"]) if st.session_state["active_project"] in projects else 0
        )
        if sel and sel != st.session_state["active_project"]:
            st.session_state["active_project"] = sel
            st.session_state["raw_df"] = None
            st.session_state["processed_df"] = None
            st.session_state["enrich_audit_df"] = None
            st.session_state["flagged_df"] = None
            st.session_state["run_meta"] = None
            st.session_state["mapping"] = {}
            st.success(f"Switched to project: {sel}")
    with col2:
        newp = st.text_input("New Project Name")
        if st.button("Create Project"):
            if not newp.strip(): st.warning("Blank name.")
            elif newp in projects: st.warning("Project already exists.")
            else:
                ensure_project(newp.strip())
                st.session_state["active_project"] = newp.strip()
                st.session_state["mapping"] = {}
                st.success(f"Project '{newp}' created.")

    proj = st.session_state["active_project"]
    if not proj:
        st.info("Select or create a project.")
        st.stop()

    tpl_path = project_file(proj, TEMPLATE_FILE)
    st.subheader("Template")
    if os.path.exists(tpl_path):
        tdf = safe_read_excel(tpl_path)
        if tdf is not None and not tdf.empty:
            st.dataframe(tdf.head(50), use_container_width=True)
        c1,c2 = st.columns(2)
        with c1:
            if st.button("Replace Template"):
                st.session_state["replace_template"] = True
        with c2:
            if st.button("Delete Template"):
                os.remove(tpl_path)
                st.warning("Template deleted.")
    else:
        st.info("No template yet.")
    if st.session_state.get("replace_template") or not os.path.exists(tpl_path):
        up_t = st.file_uploader("Upload Template (.xlsx)", type=["xlsx"])
        if up_t:
            dfN = safe_read_excel(up_t)
            if dfN is not None and not dfN.empty:
                dfN.to_excel(tpl_path, index=False)
                st.session_state.pop("replace_template", None)
                st.success("Template saved.")

    st.subheader("Import Enrichment (Optional)")
    others = [p for p in projects if p != proj]
    if others:
        src = st.selectbox("Source Project", [""]+others)
        if src and st.button("Copy Enrichment"):
            cfg = load_enrichment(src)
            save_enrichment(proj, cfg)
            st.success("Enrichment copied.")

    st.subheader("Delete a Project")
    if st.button("Delete a Project", key="toggle_delete"):
        st.session_state["show_delete_dropdown"] = not st.session_state.get("show_delete_dropdown", False)
    if st.session_state.get("show_delete_dropdown"):
        del_proj = st.selectbox("Select a project to delete", projects, key="delete_proj_sel")
        if st.button("Confirm Delete", type="primary", key="confirm_delete_btn"):
            try:
                shutil.rmtree(project_dir(del_proj), ignore_errors=True)
                st.success(f"Project '{del_proj}' deleted.")
                if st.session_state.get("active_project") == del_proj:
                    st.session_state["active_project"] = None
                    st.session_state["raw_df"] = None
                    st.session_state["processed_df"] = None
                    st.session_state["enrich_audit_df"] = None
                    st.session_state["flagged_df"] = None
                    st.session_state["run_meta"] = None
                    st.session_state["mapping"] = {}
                st.session_state["show_delete_dropdown"] = False
                st.rerun()
            except Exception as e:
                st.error(f"Failed to delete project: {e}")

    st.info("Go to '2. Upload Raw'.")

# =========================================================
# STEP 2: Upload Raw
# =========================================================
elif current_step == "2. Upload Raw":
    st.title("Upload Raw Data")
    proj = st.session_state["active_project"]
    if not proj: st.stop()
    tpl_path = project_file(proj, TEMPLATE_FILE)
    if not os.path.exists(tpl_path):
        st.warning("Upload template first.")
        st.stop()

    with st.container():
        st.markdown("<div class='toolbar'>", unsafe_allow_html=True)
        if st.button("Reset all overrides (project)", key="btn_reset_overrides_project"):
            reset_overrides_for_project(proj, backup=True)
            st.success("All overrides reset for this project.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Upload new file")
    raw_up = st.file_uploader("Raw (.xlsx)", type=["xlsx"])
    if raw_up:
        rdf = safe_read_excel(raw_up)
        if rdf is not None and not rdf.empty:
            saved_path = save_uploaded_raw_copy(proj, raw_up)
            st.session_state["raw_df"] = rdf
            reset_overrides_for_project(proj, backup=True)
            st.success(f"Raw loaded: {len(rdf)} rows / {len(rdf.columns)} cols. Saved: {os.path.basename(saved_path)}. Overrides have been reset.")

    st.subheader("Or load from recent files")
    recents = list_recent_raw_uploads(proj, limit=5)
    if recents:
        options = [f"{i+1}. {r['name']}  —  {r['ts']}" for i, r in enumerate(recents)]
        choice = st.selectbox("Recent uploaded files (last 5)", options)
        if st.button("Load selected recent file", key="load_recent_raw"):
            idx = options.index(choice)
            path = recents[idx]["path"]
            rdf = safe_read_excel(path)
            if rdf is not None and not rdf.empty:
                st.session_state["raw_df"] = rdf
                st.success(f"Raw loaded from memory: {recents[idx]['name']} ({len(rdf)} rows / {len(rdf.columns)} cols)")
    else:
        st.info("No recent raw files yet. Upload a new one to start building memory.")

    if st.session_state["raw_df"] is not None:
        st.dataframe(st.session_state["raw_df"].head(50), use_container_width=True)
        st.info("Next: '3. Map Fields'")

# =========================================================
# STEP 3: Map Fields
# =========================================================
elif current_step == "3. Map Fields":
    st.title("Map Raw Columns → Template Fields")
    proj = st.session_state["active_project"]
    if not proj: st.stop()
    tpl_path = project_file(proj, TEMPLATE_FILE)
    if not os.path.exists(tpl_path): st.warning("Template missing."); st.stop()
    if st.session_state["raw_df"] is None: st.warning("Upload or load raw first."); st.stop()

    tpl_df = safe_read_excel(tpl_path)
    if tpl_df is None or tpl_df.empty: st.error("Template unreadable / empty."); st.stop()

    raw_df = st.session_state["raw_df"]
    raw_cols = list(map(str, list(raw_df.columns)))
    template_cols = list(map(str, list(tpl_df.columns)))

    map_path = project_file(proj, MAPPING_FILE)
    existing_mapping = load_yaml(map_path).get("overrides", {})

    st.caption("Headers-only suggestions. Choose the raw column for each template field. 'Reinforce 👍' teaches future suggestions.")
    st.markdown("<div class='mapping-grid-head'><div>Template Field</div><div>Mapped Raw Column</div><div>Reinforce</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='mapping-grid-body'>", unsafe_allow_html=True)

    def norm(h): return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', str(h).strip().lower())).strip()

    headers_hash = hashlib.sha1(("|".join(sorted([norm(c) for c in raw_cols]))).encode("utf-8")).hexdigest()
    sim_cache = st.session_state["map_sim_cache"].get(headers_hash, {})

    if not sim_cache:
        sim_cache = {}
        raw_norm = [(c, norm(c)) for c in raw_cols]
        for tcol in template_cols:
            tnorm = norm(tcol)
            scores=[]
            for rcol, rnorm in raw_norm:
                sc = fuzz.token_set_ratio(tnorm, rnorm)
                scores.append((rcol, sc))
            scores.sort(key=lambda x: x[1], reverse=True)
            sim_cache[tcol] = scores[:5]
        st.session_state["map_sim_cache"][headers_hash] = sim_cache

    THRESH = 82

    def safe_widget_key(name: str, prefix="map_sel"):
        safe = re.sub(r'[^A-Za-z0-9_]', '_', str(name))
        h = hashlib.sha1(str(name).encode("utf-8")).hexdigest()[:8]
        return f"{prefix}::{safe}::{h}"

    new_mapping = {}
    for tcol in template_cols:
        memory_choice = suggest_from_global(tcol, raw_cols)
        top5 = sim_cache.get(tcol, [])
        top1 = top5[0][0] if top5 else ""
        top1_score = top5[0][1] if top5 else 0
        preselect = existing_mapping.get(tcol, memory_choice if memory_choice in raw_cols else (top1 if top1_score >= THRESH else ""))

        c1, c2, c3 = st.columns([2,4,1])
        with c1:
            st.markdown(f"<div class='mapping-grid-row'><div style='grid-column:1/2;overflow-wrap:anywhere'>{tcol}</div></div>", unsafe_allow_html=True)
        with c2:
            options = [""] + raw_cols
            idx = options.index(preselect) if preselect in options else 0
            chosen = st.selectbox(
                f"{tcol}__sel",
                options,
                index=idx,
                label_visibility="collapsed",
                key=safe_widget_key(tcol)
            )
            new_mapping[tcol] = chosen
            if top5:
                chips = " ".join([f"<span class='badge'>{r} ({s})</span>" for r,s in top5])
                st.markdown(f"<div style='margin-top:4px'>{chips}</div>", unsafe_allow_html=True)
        with c3:
            if chosen:
                if st.button("👍", key=f"mem_{hashlib.md5(tcol.encode()).hexdigest()[:6]}", help="Reinforce mapping"):
                    update_global_memory(tcol, chosen)
                    st.toast(f"Reinforced: {tcol} → {chosen}")
            else:
                st.write("")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Save Mapping"):
        save_yaml(map_path, {"overrides": new_mapping, "saved_at": datetime.datetime.utcnow().isoformat()})
        st.session_state["mapping"] = new_mapping
        for t,r in new_mapping.items():
            if r: update_global_memory(t, r)
        st.success("Mapping saved.")
    if st.session_state.get("mapping"):
        st.info("Proceed to '4. Enrichment Setup'.")

# =========================================================
# STEP 4: Enrichment Setup
# =========================================================
elif current_step == "4. Enrichment Setup":
    st.title("Enrichment Setup")
    proj = st.session_state["active_project"]
    if not proj: st.stop()
    tpl_path = project_file(proj, TEMPLATE_FILE)
    if not os.path.exists(tpl_path): st.stop()
    if st.session_state["raw_df"] is None or not st.session_state.get("mapping"):
        st.warning("Upload raw + mapping first.")
        st.stop()

    enrichment_cfg = load_enrichment(proj)
    tpl_df = safe_read_excel(tpl_path)
    final_cols = list(tpl_df.columns)
    raw_cols  = list(st.session_state["raw_df"].columns)

    st.subheader("Targets")
    curr_targets = [t for t in enrichment_cfg["targets"].keys() if t in final_cols]
    targets = st.multiselect("Template fields to enrich", final_cols, default=curr_targets, key="enrich_targets")
    for t in list(enrichment_cfg["targets"].keys()):
        if t not in targets: enrichment_cfg["targets"].pop(t,None)
    for t in targets:
        enrichment_cfg["targets"].setdefault(t, {"sources": [], "rules": []})

    for tgt in targets:
        node = enrichment_cfg["targets"][tgt]
        with st.expander(f"Target: {tgt}", expanded=False):
            node["sources"] = st.multiselect(
                f"Raw sources for {tgt}",
                raw_cols,
                default=[c for c in node.get("sources",[]) if c in raw_cols],
                key=f"sources_{tgt}"
            )
            rules_df = pd.DataFrame(node.get("rules",[]))
            if rules_df.empty:
                rules_df = pd.DataFrame(columns=["output_value","keyword","weight"])
            for c in ["output_value","keyword","weight"]:
                if c not in rules_df.columns:
                    rules_df[c] = "" if c in ("output_value","keyword") else 5.0
            edited = st.data_editor(
                rules_df[["output_value","keyword","weight"]],
                num_rows="dynamic",
                key=f"rules_editor_{tgt}",
                use_container_width=True,
                column_config={
                    "output_value": st.column_config.TextColumn("Category (Output Value)", width="large"),
                    "keyword": st.column_config.TextColumn("Keyword", width="large"),
                    "weight": st.column_config.NumberColumn("Weight", min_value=1.0, max_value=5.0, step=0.5, width="small")
                }
            )
            if st.button(f"Save Rules ({tgt})", key=f"save_rules_{tgt}"):
                cleaned=[]
                for _, r in edited.iterrows():
                    ov = str(r.get("output_value","")).strip()
                    kw = str(r.get("keyword","")).strip()
                    if not ov or not kw: continue
                    cleaned.append({"output_value": ov, "keyword": kw, "weight": min(5.0, max(1.0, safe_float(r.get("weight",5.0), 5.0))), "regex": False, "fuzzy": False})
                node["rules"] = cleaned
                save_enrichment(proj, enrichment_cfg)
                st.success(f"Saved {len(cleaned)} rules.")

    if st.button("Save All Enrichment Config"):
        save_enrichment(proj, enrichment_cfg)
        st.success("Enrichment config saved. Go to '5. Run Processing'.")

# =========================================================
# STEP 5: Run Processing (deterministic enrichment)
# =========================================================
elif current_step == "5. Run Processing":
    st.title("Run Processing")
    proj = st.session_state["active_project"]
    if not proj: st.stop()
    tpl_path = project_file(proj, TEMPLATE_FILE)
    if not os.path.exists(tpl_path):
        st.warning("Template missing."); st.stop()
    if st.session_state["raw_df"] is None or not st.session_state.get("mapping"):
        st.warning("Upload raw + mapping first."); st.stop()

    tpl_df = safe_read_excel(tpl_path)
    final_cols = list(tpl_df.columns)
    raw_df = st.session_state["raw_df"]
    mapping = st.session_state.get("mapping",{})
    enrichment_cfg = load_enrichment(proj)

    def run_pipeline():
        prog = progress_component(); prog(0,"Start")
        out_df = pd.DataFrame(columns=final_cols)
        # Map columns
        for i,(tcol,rcol) in enumerate(mapping.items()):
            if tcol in out_df.columns and rcol and rcol in raw_df.columns:
                out_df[tcol] = raw_df[rcol]
            elif tcol in out_df.columns:
                out_df[tcol] = ""
            prog(5+(i+1)/max(1,len(mapping))*15,"Mapping")

        # Prepared rules once
        prepared = build_prepared_rules(enrichment_cfg)
        targets = list(prepared.keys())
        audit_rows=[]; aggregated_keywords=[]
        for ridx in range(len(raw_df)):
            raw_row = raw_df.iloc[ridx]
            entry = {"RowIndex": ridx}
            row_kw=[]
            for tgt in targets:
                if tgt not in out_df.columns: out_df[tgt]=""
                sources = enrichment_cfg["targets"][tgt].get("sources", [])
                if sources:
                    ctx = " ".join(str(raw_row.get(s,"")) for s in sources if s in raw_row.index)
                else:
                    ctx = " ".join(str(raw_row[c]) for c in raw_row.index)
                ctx_lc = ctx.lower()
                result = classify_context(ctx_lc, prepared.get(tgt, []))
                out_df.loc[ridx, tgt] = result["value"]
                entry[f"{tgt}_Value"]   = result["value"]
                entry[f"{tgt}_Status"]  = result["status"]
                entry[f"{tgt}_Scores"]  = json.dumps(result["totals"])
                entry[f"{tgt}_MatchedKeywords"] = json.dumps(result["matched"])
                entry[f"{tgt}__MatchedKeywords"] = result["audit_str"] or ""
                for _, kws in result["matched"].items():
                    row_kw.extend(kws)
            aggregated_keywords.append(", ".join(sorted(set(row_kw))) if row_kw else "")
            if ridx % 25 == 0:
                prog(25+(ridx/len(raw_df))*55,"Enrichment")
            audit_rows.append(entry)

        out_df["All_Enrichment_Matched_Keywords"] = aggregated_keywords
        audit_df = pd.DataFrame(audit_rows)

        overrides = load_overrides(proj)
        out_df, audit_df = apply_overrides_to_processed(out_df, audit_df, overrides)

        run_meta = {
            "version": APP_VERSION,
            "timestamp_utc": datetime.datetime.utcnow().isoformat(),
            "project": proj,
            "raw_rows": len(raw_df),
            "rows_out": len(out_df),
            "flagged_rows": 0,
            "enrichment_targets": targets
        }
        st.session_state["processed_df"]    = out_df
        st.session_state["enrich_audit_df"] = audit_df
        st.session_state["flagged_df"]      = pd.DataFrame()
        st.session_state["run_meta"]        = run_meta
        st.session_state["last_processing_targets"] = targets
        save_yaml(project_file(proj, RUN_META_FILE), run_meta)
        prog(100,"Done")
        return out_df, audit_df

    if st.button("Run Processing 🚀", key="run_processing_btn"):
        out_df, audit_df = run_pipeline()
        st.success("Processing complete. Continue to '6. Overrides & Analytics'.")
        prev = out_df.head(60).copy()
        for tgt in st.session_state["last_processing_targets"]:
            s = f"{tgt}_Status"
            if s in audit_df.columns: prev[s] = audit_df[s]
        st.dataframe(prev, use_container_width=True)

# =========================================================
# STEP 6: Overrides & Analytics (AI panel with vector reuse + SQLite)
# =========================================================
elif current_step == "6. Overrides & Analytics":
    st.title("Overrides & Analytics")
    proj = st.session_state["active_project"]
    if not proj: st.stop()
    if st.session_state.get("processed_df") is None or st.session_state.get("enrich_audit_df") is None:
        st.warning("Run processing first."); st.stop()

    processed_df = st.session_state["processed_df"].copy()
    audit_df     = st.session_state["enrich_audit_df"].copy()
    enrichment_cfg = load_enrichment(proj)
    overrides = load_overrides(proj)
    all_targets = st.session_state.get("last_processing_targets", list(enrichment_cfg.get("targets",{}).keys()))
    if not all_targets:
        st.info("No enrichment targets configured.")
        st.stop()

    # 1) Analytics (always visible)
    st.subheader("Analytics (current run)")
    def compute_analytics(audit):
        rows=[]
        for t in all_targets:
            s = f"{t}_Status"
            if s in audit.columns:
                vc = audit[s].value_counts().to_dict()
                rows.append({
                    "Target": t,
                    "OK": vc.get("OK",0),
                    "MULTI": vc.get("MULTI",0),
                    "UNCLASSIFIED": vc.get("UNCLASSIFIED",0),
                    "OVERRIDE": vc.get("OVERRIDE",0),
                    "TOTAL": sum(vc.values())
                })
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    ana_df = compute_analytics(audit_df)
    if not ana_df.empty:
        st.dataframe(ana_df, use_container_width=True)
    else:
        st.info("No analytics yet.")

    # Helpers reused
    def allowed_outputs_for_target(tgt_name):
        rules = enrichment_cfg.get("targets", {}).get(tgt_name, {}).get("rules", [])
        outs = sorted({str(r.get("output_value","")).strip() for r in rules if str(r.get("output_value","")).strip()})
        return outs
    def _ai_norm_list_to_str(v):
        if isinstance(v, list): return ", ".join([str(x) for x in v if str(x).strip()])
        if v in (None, np.nan): return ""
        return str(v)
    def _parsed_kw_for_row(tgt, idx):
        mkw_json_col = f"{tgt}_MatchedKeywords"
        try:
            d = json.loads(audit_df.loc[audit_df["RowIndex"]==idx, mkw_json_col].values[0])
            flat=[]
            for _, lst in d.items(): flat.extend(lst)
            return ", ".join(sorted(set([x for x in flat if str(x).strip()])))
        except: return ""
    def _get_candidate_rows(tgt, statuses):
        s_col = f"{tgt}_Status"
        if s_col not in audit_df.columns or "RowIndex" not in audit_df.columns: return []
        mask = audit_df[s_col].isin(statuses)
        return audit_df.loc[mask, "RowIndex"].tolist()
    def _compute_analytics_local(audit, targets_list):
        rows=[]
        for t in targets_list:
            s = f"{t}_Status"
            if s in audit.columns:
                vc = audit[s].value_counts().to_dict()
                rows.append({"Target": t, "OK": vc.get("OK",0), "MULTI": vc.get("MULTI",0), "UNCLASSIFIED": vc.get("UNCLASSIFIED",0), "OVERRIDE": vc.get("OVERRIDE",0), "TOTAL": sum(vc.values())})
        return pd.DataFrame(rows) if rows else pd.DataFrame()

    # 2) Full Processed Table (collapsible)
    with st.expander("Processed Table (current run)", expanded=False):
        st.dataframe(processed_df, use_container_width=True)

    # 3) AI Suggestions (vector reuse + SQLite + per-run tokens)
    with st.expander("🤖 AI Suggestions (beta) — for MULTI / UNCLASSIFIED", expanded=False):
        client, err = get_openai_client()

        # Ensure session defaults
        st.session_state.setdefault("ai_form_state", st.session_state.get("ai_form_state", {}))
        st.session_state.setdefault("ai_table_state", {"records": []})
        st.session_state.setdefault("ai_sel_rows", [])
        st.session_state.setdefault("ai_tokens_used", {"input": 0, "output": 0, "cached": 0})
        st.session_state.setdefault("ai_last_run_tokens", {"input": 0, "output": 0, "cached": 0, "total": 0})
        st.session_state.setdefault("ai_cache", st.session_state.get("ai_cache", {}))
        st.session_state.setdefault("ai_undo", [])
        st.session_state.setdefault("ai_redo", [])

        table_holder = st.container()
        ai_form = st.session_state["ai_form_state"]

        # Controls row 1
        c1, c2, c3, c4, c5 = st.columns([1, 1.2, 1.6, 1, 1])
        with c1:
            ai_form["target"] = st.selectbox(
                "Target",
                all_targets,
                index=all_targets.index(ai_form.get("target", all_targets[0])) if ai_form.get("target") in all_targets else 0,
                key="ai_panel_target",
            )
        with c2:
            ai_form["statuses"] = st.multiselect(
                "Statuses",
                ["UNCLASSIFIED", "MULTI"],
                default=ai_form.get("statuses", ["UNCLASSIFIED", "MULTI"]),
                key="ai_panel_statuses",
            )
        with c3:
            all_processed_cols = list(processed_df.columns)
            special_cols = ["MatchedKeywords (parsed)"]
            default_show = ai_form.get("fields_to_show") or [
                c for c in [ai_form.get("target", all_targets[0]), "MatchedKeywords (parsed)", "Course Name"]
                if (c == "MatchedKeywords (parsed)") or (c in all_processed_cols)
            ]
            ai_form["fields_to_show"] = st.multiselect(
                "Fields to show",
                options=special_cols + all_processed_cols,
                default=default_show,
                key="ai_panel_fields_to_show",
            )
        with c4:
            ai_form["model"] = st.selectbox(
                "Model",
                ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"],
                index=["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"].index(ai_form.get("model", "gpt-4o-mini")),
                key="ai_panel_model",
                disabled=(client is None or err is not None),
            )
        with c5:
            ai_form["temperature"] = st.slider(
                "Temp",
                0.0, 1.0, float(ai_form.get("temperature", 0.2)), 0.05,
                key="ai_panel_temperature",
                disabled=(client is None or err is not None),
            )

        # Controls row 2
        c6, c7, c8, c9, c10 = st.columns([1, 1, 1, 1, 1])
        with c6:
            ai_form["row_cap"] = int(st.number_input("AI Max rows", min_value=1, max_value=10000, value=int(ai_form.get("row_cap", 500)), step=10, key="ai_panel_row_cap"))
        with c7:
            ai_form["refresh_cache"] = st.checkbox("Refresh cache", value=bool(ai_form.get("refresh_cache", False)), key="ai_panel_refresh")
        with c8:
            st.checkbox("Select all Apply?", value=False, key="ai_panel_select_all_apply")
        with c9:
            st.checkbox("Select all Master?", value=False, key="ai_panel_select_all_master")
        with c10:
            gen = st.button("Generate suggestions", key="ai_panel_generate", disabled=(client is None or err is not None))

        # Vector Reuse controls
        vr1, vr2, vr3 = st.columns([1, 1, 1])
        with vr1:
            use_vec = st.checkbox("Use vector reuse (embeddings)", value=True, key="ai_use_vector_reuse")
        with vr2:
            sim_thresh = st.slider("Similarity threshold", 0.50, 0.95, float(SIMILARITY_DEFAULT), 0.01, key="ai_similarity_threshold")
        with vr3:
            vec_k = int(st.number_input("Neighbors to scan (K)", min_value=10, max_value=1000, value=200, step=10, key="ai_vec_topk"))

        # Show cumulative tokens
        toks = st.session_state["ai_tokens_used"]
        if (toks.get("input", 0) + toks.get("output", 0) + toks.get("cached", 0)) > 0:
            total_cum = toks.get("input", 0) + toks.get("output", 0)
            st.caption(f"Cumulative tokens: {toks.get('input', 0)} input / {toks.get('output', 0)} output = {total_cum} total (cache/reuse hits: {toks.get('cached', 0)})")

        # Show last run tokens
        last = st.session_state.get("ai_last_run_tokens", {"input": 0, "output": 0, "cached": 0, "total": 0})
        if (last.get("total", 0) + last.get("cached", 0)) > 0:
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric("Last run prompt tokens", last.get("input", 0))
            with m2: st.metric("Last run completion tokens", last.get("output", 0))
            with m3: st.metric("Last run total tokens", last.get("total", 0))
            with m4: st.metric("Last run cache/reuse hits", last.get("cached", 0))

        # Generate suggestions
        if gen and client is not None and not err:
            tgt = ai_form["target"]; model = ai_form["model"]; row_cap = int(ai_form["row_cap"])
            allowed = allowed_outputs_for_target(tgt)
            rows_idx_all = _get_candidate_rows(tgt, ai_form["statuses"])
            rows_idx = rows_idx_all[:row_cap]

            run_input = 0; run_output = 0; run_cached = 0
            suggestions = []

            # Preload neighbor pool for vector reuse once per run (per target)
            neighbor_pool = []
            if use_vec:
                neighbor_pool = ai_db_get_nearest_for_target(proj, tgt, model, limit=vec_k)

            for ridx in rows_idx:
                raw_row = st.session_state["raw_df"].iloc[ridx]
                sources = enrichment_cfg.get("targets", {}).get(tgt, {}).get("sources", [])
                ctx = build_row_context(raw_row, sources)
                chash = context_hash(tgt, ctx, {})
                key_mem = (proj, tgt, int(ridx), chash, model)

                # 1) In-memory cache hit?
                if (key_mem in st.session_state["ai_cache"]) and (not ai_form.get("refresh_cache", False)):
                    st.session_state["ai_tokens_used"]["cached"] += 1; run_cached += 1
                    cached = st.session_state["ai_cache"][key_mem]
                    sv = cached.get("suggested_value","")
                    if sv not in allowed: sv = ""
                    suggestions.append({
                        "RowIndex": ridx,
                        "suggested_value": sv,
                        "confidence": float(cached.get("confidence",0)),
                        "rationale": cached.get("rationale",""),
                        "new_keywords": cached.get("new_keywords",[]),
                        "suggested_weight": safe_float(cached.get("suggested_weight",3.0), 3.0)
                    })
                    continue

                # 2) Persistent exact match (SQLite) if not refreshing
                if not ai_form.get("refresh_cache", False):
                    db_exact = ai_db_get_exact(proj, tgt, model, chash)
                    if db_exact:
                        st.session_state["ai_tokens_used"]["cached"] += 1; run_cached += 1
                        sv = db_exact.get("suggested_value","")
                        if sv not in allowed: sv = ""
                        rec = {
                            "RowIndex": ridx,
                            "suggested_value": sv,
                            "confidence": float(db_exact.get("confidence",0)),
                            "rationale": db_exact.get("rationale",""),
                            "new_keywords": db_exact.get("new_keywords",[]) or [],
                            "suggested_weight": safe_float(db_exact.get("suggested_weight",3.0), 3.0)
                        }
                        suggestions.append(rec)
                        st.session_state["ai_cache"][key_mem] = {k:v for k,v in rec.items() if k!="RowIndex"}
                        continue

                # 3) Vector reuse
                reused = False
                curr_emb = []
                if use_vec and neighbor_pool:
                    curr_emb = get_embedding(client, ctx)
                    if curr_emb:
                        best = None; best_sim = -1.0
                        for nb in neighbor_pool:
                            sim = cosine_similarity(curr_emb, nb.get("embedding", []))
                            if sim > best_sim:
                                best_sim = sim; best = nb
                        if best and best_sim >= float(sim_thresh):
                            sv = best["rec"]["suggested_value"] or ""
                            if sv not in allowed: sv = ""
                            rec = {
                                "RowIndex": ridx,
                                "suggested_value": sv,
                                "confidence": float(best["rec"]["confidence"] or 0.0),
                                "rationale": f"Reused via vector similarity (cos={best_sim:.3f})",
                                "new_keywords": best["rec"]["new_keywords"] or [],
                                "suggested_weight": safe_float(best["rec"]["suggested_weight"], 3.0)
                            }
                            suggestions.append(rec)
                            st.session_state["ai_tokens_used"]["cached"] += 1; run_cached += 1
                            st.session_state["ai_cache"][key_mem] = {k:v for k,v in rec.items() if k!="RowIndex"}
                            ai_db_upsert_suggestion(proj, tgt, model, chash, ctx, curr_emb or [], rec)
                            reused = True
                if reused:
                    continue

                # 4) Live LLM fallback
                prompt = f"""
You are assisting with data enrichment for target: "{tgt}".
Choose the single best category ONLY from this allowed list:
{allowed}

Analyze this context (truncated to sources only):
{ctx}

Return strict JSON:
{{"suggested_value":"<one_of_allowed_or_empty>","confidence":0..1,"rationale":"...", "new_keywords":[], "suggested_weight":1..5}}
If unsure, set suggested_value="".
"""
                try:
                    resp = client.chat.completions.create(
                        model=model,
                        temperature=float(ai_form.get("temperature", 0.2)),
                        response_format={"type": "json_object"},
                        messages=[
                            {"role": "system", "content": "You are a precise, deterministic enrichment assistant. Never propose values outside the allowed list."},
                            {"role": "user", "content": prompt},
                        ],
                    )
                    # Token usage
                    try:
                        u = resp.usage
                        this_in = int(getattr(u, "prompt_tokens", 0) or 0)
                        this_out = int(getattr(u, "completion_tokens", 0) or 0)
                        st.session_state["ai_tokens_used"]["input"] += this_in
                        st.session_state["ai_tokens_used"]["output"] += this_out
                        run_input += this_in; run_output += this_out
                    except Exception:
                        pass

                    js = json.loads(resp.choices[0].message.content)
                    sv = js.get("suggested_value", "") or ""
                    if sv not in allowed:
                        sv = ""
                    rec = {
                        "RowIndex": ridx,
                        "suggested_value": sv,
                        "confidence": float(js.get("confidence", 0) or 0),
                        "rationale": js.get("rationale", ""),
                        "new_keywords": js.get("new_keywords", []) or [],
                        "suggested_weight": safe_float(js.get("suggested_weight", 3.0), 3.0),
                    }
                    suggestions.append(rec)
                    st.session_state["ai_cache"][key_mem] = {k:v for k,v in rec.items() if k!="RowIndex"}
                    if not curr_emb:
                        curr_emb = get_embedding(client, ctx)
                    ai_db_upsert_suggestion(proj, tgt, model, chash, ctx, curr_emb or [], rec)

                except Exception as e:
                    suggestions.append({
                        "RowIndex": ridx,
                        "suggested_value": "",
                        "confidence": 0.0,
                        "rationale": f"AI error: {e}",
                        "new_keywords": [],
                        "suggested_weight": 3.0
                    })

            # Store and show last run tokens
            st.session_state["ai_last_run_tokens"] = {
                "input": run_input,
                "output": run_output,
                "cached": run_cached,
                "total": run_input + run_output,
            }
            st.success(f"AI tokens (this run): prompt {run_input}, completion {run_output}, total {run_input + run_output}. Cache/reuse hits: {run_cached}")

            if suggestions:
                disp = pd.DataFrame(suggestions)
                disp["rationale"] = disp["rationale"].apply(lambda x: "" if x in (None, np.nan) else str(x))
                disp["New Keywords (parsed)"] = disp["new_keywords"].apply(_ai_norm_list_to_str)
                disp["Apply Override?"] = False
                disp["Add to Master?"] = False
                for col in ai_form["fields_to_show"]:
                    if col == "MatchedKeywords (parsed)":
                        disp[col] = disp["RowIndex"].apply(lambda ix: _parsed_kw_for_row(tgt, ix))
                    elif col in processed_df.columns:
                        disp[col] = disp["RowIndex"].apply(lambda ix: processed_df.at[ix, col] if ix in processed_df.index else "")
                try:
                    disp = disp.sort_values(by=["confidence","RowIndex"], ascending=[True, True], kind="mergesort")
                except: pass
                st.session_state["ai_table_state"]["records"] = disp.to_dict(orient="records")

        # Render table at the top
        with table_holder:
            recs = st.session_state["ai_table_state"].get("records", [])
            if recs:
                df_disp = pd.DataFrame(recs)
                if st.session_state.get("ai_panel_select_all_apply", False) and "Apply Override?" in df_disp.columns:
                    df_disp["Apply Override?"] = True
                if st.session_state.get("ai_panel_select_all_master", False) and "Add to Master?" in df_disp.columns:
                    df_disp["Add to Master?"] = True
                if "New Keywords (parsed)" not in df_disp.columns and "new_keywords" in df_disp.columns:
                    df_disp["New Keywords (parsed)"] = df_disp["new_keywords"].apply(_ai_norm_list_to_str)
                df_disp["rationale"] = df_disp["rationale"].apply(lambda x: "" if x in (None, np.nan) else str(x))

                editor = st.data_editor(
                    df_disp,
                    use_container_width=True,
                    hide_index=True,
                    height=560,
                    key="ai_panel_table",
                    column_config={
                        "RowIndex": st.column_config.NumberColumn("RowIndex", disabled=True, width="small"),
                        "suggested_value": st.column_config.TextColumn("Suggested Value", width="large"),
                        "confidence": st.column_config.NumberColumn("Confidence", min_value=0.0, max_value=1.0, step=0.01, width="small"),
                        "rationale": st.column_config.TextColumn("Rationale", width="large"),
                        "New Keywords (parsed)": st.column_config.TextColumn("New Keywords", width="large"),
                        "Apply Override?": st.column_config.CheckboxColumn("Apply Override?", width="small"),
                        "Add to Master?": st.column_config.CheckboxColumn("Add to Master?", width="small")
                    }
                )
                st.session_state["ai_table_state"]["records"] = editor.to_dict(orient="records")
                st.session_state["ai_sel_rows"] = [int(r["RowIndex"]) for _, r in editor.iterrows() if r.get("Apply Override?", False)]

        # Actions row
        a1, a2, a3, a4 = st.columns([1,1,1,1])
        with a1:
            apply_sel = st.button("Apply Selected", key="ai_panel_apply_sel")
        with a2:
            apply_all = st.button("Apply All", key="ai_panel_apply_all")
        with a3:
            undo_last = st.button("Undo last apply", key="ai_panel_undo")
        with a4:
            redo_last = st.button("Redo", key="ai_panel_redo")

        # Apply logic + preview
        def _apply_overrides(scope_records, tgt_):
            ov = load_overrides(proj); changes=[]
            for r in scope_records:
                ridx = int(r["RowIndex"])
                new_val = str(r.get("suggested_value","")).strip()
                if not new_val: continue
                old_val = processed_df.at[ridx, tgt_] if (ridx in processed_df.index and tgt_ in processed_df.columns) else ""
                if new_val != old_val:
                    ov["overrides"].setdefault(tgt_, {})
                    ov["overrides"][tgt_][str(ridx)] = {"new_value": new_val, "timestamp": datetime.datetime.utcnow().isoformat()}
                    changes.append({"row": ridx, "old": old_val, "new": new_val})
            save_overrides(proj, ov)
            p2, a2 = apply_overrides_to_processed(processed_df.copy(), audit_df.copy(), ov)
            st.session_state["processed_df"] = p2; st.session_state["enrich_audit_df"] = a2
            return changes
        def _gather_rules(scope_records, tgt_):
            props=[]
            for r in scope_records:
                if not r.get("Add to Master?", False): continue
                out = str(r.get("suggested_value","")).strip()
                w   = min(5.0, max(1.0, safe_float(r.get("suggested_weight",3.0), 3.0)))
                kws_parsed = r.get("New Keywords (parsed)","")
                cand = str(kws_parsed).split(",")[0].strip().lower() if kws_parsed else ""
                if out and cand:
                    kw = re.sub(r"\s+"," ", cand)
                    props.append({"Target": tgt_, "Output value": out, "Keyword": kw, "Weight": w})
            return props
        def _hygiene_merge_rules(node_rules, proposed):
            existing = {(re.sub(r"\s+"," ",str(x.get("output_value","")).strip().lower()),
                         re.sub(r"\s+"," ",str(x.get("keyword","")).strip().lower())): float(x.get("weight",3.0))
                        for x in (node_rules or []) if x.get("output_value") and x.get("keyword")}
            result=[]
            for pr in proposed:
                ov = re.sub(r"\s+"," ",str(pr["Output value"]).strip().lower())
                kw = re.sub(r"\s+"," ",str(pr["Keyword"]).strip().lower())
                w  = min(5.0, max(1.0, safe_float(pr.get("Weight",3.0), 3.0)))
                if (ov, kw) in existing:
                    existing[(ov,kw)] = min(existing[(ov,kw)], w); continue
                merged=False
                for (eov, ekw), ew in list(existing.items()):
                    if eov == ov and levenshtein(kw, ekw) < 2:
                        existing[(eov, ekw)] = min(ew, w); merged=True; break
                if not merged:
                    for rr in result:
                        if re.sub(r"\s+"," ",rr["output_value"].strip().lower()) == ov and levenshtein(kw, re.sub(r"\s+"," ",rr["keyword"].strip().lower())) < 2:
                            rr["weight"] = min(rr["weight"], w); merged=True; break
                if not merged:
                    result.append({"output_value": pr["Output value"], "keyword": kw, "weight": w, "regex": False, "fuzzy": False})
            return result

        before_ana = _compute_analytics_local(audit_df, all_targets)
        if 'apply_sel' not in locals(): apply_sel = False
        if 'apply_all' not in locals(): apply_all = False

        if apply_sel or apply_all:
            tgt = st.session_state["ai_form_state"]["target"]
            table = st.session_state["ai_table_state"]["records"]
            if not table:
                st.info("No suggestions to apply.")
            else:
                scope = [r for r in table if r.get("Apply Override?", False)] if apply_sel else list(table)
                changes = _apply_overrides(scope, tgt)
                st.toast(f"Applied {len(changes)} override(s).")

                props = _gather_rules(scope, tgt)
                rules_added=[]
                if props:
                    with st.expander("Review rules to add", expanded=True):
                        df_rules = pd.DataFrame(props); df_rules["Select?"]=True
                        red = st.data_editor(
                            df_rules, use_container_width=True, hide_index=True, key="ai_rules_review_editor",
                            column_config={
                                "Target": st.column_config.TextColumn("Target", width="small", disabled=True),
                                "Output value": st.column_config.TextColumn("Output value", width="large"),
                                "Keyword": st.column_config.TextColumn("Keyword", width="large"),
                                "Weight": st.column_config.NumberColumn("Weight", min_value=1.0, max_value=5.0, step=0.5, width="small"),
                                "Select?": st.column_config.CheckboxColumn("Select?", width="small")
                            }
                        )
                        sel_all_rules = st.checkbox("Select all rules", value=True, key="ai_rules_sel_all")
                        if sel_all_rules and "Select?" in red.columns:
                            red["Select?"] = True
                        if st.button("Approve Selected", key="ai_rules_write"):
                            cfg = load_enrichment(proj)
                            node = cfg["targets"].setdefault(tgt, {"sources": [], "rules": []})
                            to_merge = [{"Output value": r["Output value"], "Keyword": r["Keyword"], "Weight": r["Weight"]} for _, r in red.iterrows() if r.get("Select?", False)]
                            add_rules = _hygiene_merge_rules(node.get("rules", []), to_merge)
                            if add_rules:
                                node["rules"].extend(add_rules); save_enrichment(proj, cfg)
                                rules_added = add_rules; st.toast(f"Saved {len(add_rules)} rule(s).")
                            else:
                                st.info("No new rules to add after hygiene checks.")

                st.session_state["ai_undo"].append({"target": tgt, "changes": changes, "rules_added": rules_added})
                st.session_state["ai_redo"].clear()

                st.markdown("###### AI Enriched Preview (Top 200)")
                st.dataframe(st.session_state["processed_df"].head(200), use_container_width=True)
                after_ana = _compute_analytics_local(st.session_state["enrich_audit_df"], all_targets)
                cA, cB = st.columns(2)
                with cA:
                    st.markdown("###### Analytics (previous run)")
                    st.dataframe(before_ana, use_container_width=True)
                with cB:
                    st.markdown("###### Analytics (AI-suggested)")
                    st.dataframe(after_ana, use_container_width=True)

        # Undo/Redo
        def _do_undo():
            if not st.session_state["ai_undo"]:
                st.toast("Nothing to undo."); return
            batch = st.session_state["ai_undo"].pop()
            tb = batch["target"]
            ovd = load_overrides(proj)
            for ch in batch["changes"]:
                ridx = ch["row"]; old = ch["old"]
                if old == "":
                    try:
                        if str(ridx) in ovd["overrides"].get(tb, {}): del ovd["overrides"][tb][str(ridx)]
                    except: pass
                else:
                    ovd["overrides"].setdefault(tb, {})
                    ovd["overrides"][tb][str(ridx)] = {"new_value": old, "timestamp": datetime.datetime.utcnow().isoformat()}
            save_overrides(proj, ovd)
            if batch.get("rules_added"):
                cfg = load_enrichment(proj)
                node = cfg["targets"].setdefault(tb, {"sources": [], "rules": []})
                to_remove = {(re.sub(r"\s+"," ",r["output_value"].strip().lower()), re.sub(r"\s+"," ",r["keyword"].strip().lower())) for r in batch["rules_added"]}
                node["rules"] = [r for r in node.get("rules",[]) if (re.sub(r"\s+"," ",r.get("output_value","").strip().lower()), re.sub(r"\s+"," ",r.get("keyword","").strip().lower())) not in to_remove]
                save_enrichment(proj, cfg)
            p2, a2 = apply_overrides_to_processed(processed_df.copy(), audit_df.copy(), load_overrides(proj))
            st.session_state["processed_df"] = p2; st.session_state["enrich_audit_df"] = a2
            st.session_state["ai_redo"].append(batch)
            st.toast("Undo complete.")

        def _do_redo():
            if not st.session_state["ai_redo"]:
                st.toast("Nothing to redo."); return
            batch = st.session_state["ai_redo"].pop()
            tb = batch["target"]
            ovd = load_overrides(proj)
            for ch in batch["changes"]:
                ridx = ch["row"]; newv = ch["new"]
                ovd["overrides"].setdefault(tb, {})
                ovd["overrides"][tb][str(ridx)] = {"new_value": newv, "timestamp": datetime.datetime.utcnow().isoformat()}
            save_overrides(proj, ovd)
            if batch.get("rules_added"):
                cfg = load_enrichment(proj)
                node = cfg["targets"].setdefault(tb, {"sources": [], "rules": []})
                existing = {(re.sub(r"\s+"," ",r["output_value"].strip().lower()), re.sub(r"\s+"," ",r["keyword"].strip().lower())) for r in node.get("rules",[])}
                for r in batch["rules_added"]:
                    pair = (re.sub(r"\s+"," ",r["output_value"].strip().lower()), re.sub(r"\s+"," ",r["keyword"].strip().lower()))
                    if pair not in existing:
                        node["rules"].append({"output_value": r["output_value"], "keyword": r["keyword"], "weight": min(5.0, max(1.0, safe_float(r.get("weight",3.0), 3.0))), "regex": False, "fuzzy": False})
                save_enrichment(proj, cfg)
            p2, a2 = apply_overrides_to_processed(processed_df.copy(), audit_df.copy(), load_overrides(proj))
            st.session_state["processed_df"] = p2; st.session_state["enrich_audit_df"] = a2
            st.session_state["ai_undo"].append(batch)
            st.toast("Redo complete.")

        if 'undo_last' in locals() and undo_last: _do_undo()
        if 'redo_last' in locals() and redo_last: _do_redo()

        # Bottom toolbar: Export / Import
        st.markdown("---")
        st.markdown("<div class='toolbar'>", unsafe_allow_html=True)

        # Export .xlsx
        if st.button("Export .xlsx", key="ai_export_xlsx"):
            def _enrich_to_df(cfg):
                rows=[]
                for t, node in (cfg.get("targets", {}) or {}).items():
                    for r in (node.get("rules",[]) or []):
                        rows.append({"Target": t, "Output value": r.get("output_value",""), "Keyword": r.get("keyword",""), "Weight": safe_float(r.get("weight",3.0), 3.0)})
                return pd.DataFrame(rows)
            def _overrides_to_df(ov):
                rows=[]
                for t, mapping in (ov.get("overrides",{}) or {}).items():
                    for ridx, meta in (mapping or {}).items():
                        rows.append({"Target": t, "RowIndex": int(ridx), "NewValue": meta.get("new_value",""), "Timestamp": meta.get("timestamp","")})
                return pd.DataFrame(rows)
            dfE = _enrich_to_df(enrichment_cfg)
            dfO = _overrides_to_df(overrides)
            bio = io.BytesIO()
            with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
                (dfE if not dfE.empty else pd.DataFrame(columns=["Target","Output value","Keyword","Weight"])).to_excel(writer, sheet_name="Enrichment", index=False)
                (dfO if not dfO.empty else pd.DataFrame(columns=["Target","RowIndex","NewValue","Timestamp"])).to_excel(writer, sheet_name="Overrides", index=False)
            bio.seek(0)
            st.download_button("Download .xlsx", data=bio.getvalue(), file_name=f"{proj}_enrichment_overrides.xlsx", key="ai_export_xlsx_dl")

        # Export .json
        if st.button("Export .json", key="ai_export_json"):
            payload = {"enrichment": enrichment_cfg, "overrides": overrides}
            st.download_button("Download .json", data=json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"), file_name=f"{proj}_enrichment_overrides.json", key="ai_export_json_dl")

        # Import with popovers if available
        has_pop = hasattr(st, "popover")
        if has_pop:
            with st.popover("Import .xlsx"):
                upx = st.file_uploader("Choose .xlsx", type=["xlsx"], key="ai_import_xlsx")
                if upx is not None:
                    try:
                        wb = pd.read_excel(upx, sheet_name=None)
                        if "Enrichment" in wb:
                            dfE = wb["Enrichment"].fillna("")
                            cfg = load_enrichment(proj)
                            for _, r in dfE.iterrows():
                                tgt = str(r.get("Target","")).strip()
                                ov  = str(r.get("Output value","")).strip()
                                kw  = re.sub(r"\s+"," ", str(r.get("Keyword","")).strip().lower())
                                w   = min(5.0, max(1.0, safe_float(r.get("Weight",3.0), 3.0)))
                                if not tgt or not ov or not kw: continue
                                node = cfg["targets"].setdefault(tgt, {"sources": [], "rules": []})
                                pair_found = False
                                for rr in node["rules"]:
                                    if rr.get("output_value","").strip().lower() == ov.lower():
                                        if rr.get("keyword","").strip().lower() == kw or levenshtein(kw, rr.get("keyword","").strip().lower()) < 2:
                                            rr["keyword"] = kw; rr["weight"] = w; pair_found = True; break
                                if not pair_found:
                                    node["rules"].append({"output_value": ov, "keyword": kw, "weight": w, "regex": False, "fuzzy": False})
                            save_enrichment(proj, cfg); enrichment_cfg = cfg
                        if "Overrides" in wb:
                            dfO = wb["Overrides"].fillna("")
                            ovd = load_overrides(proj)
                            for _, r in dfO.iterrows():
                                tgt = str(r.get("Target","")).strip()
                                if tgt == "": continue
                                ridx = r.get("RowIndex", None)
                                if pd.isna(ridx): continue
                                ridx = int(ridx)
                                newv = str(r.get("NewValue",""))
                                ts   = str(r.get("Timestamp","")) or datetime.datetime.utcnow().isoformat()
                                ovd["overrides"].setdefault(tgt, {})
                                old = ovd["overrides"][tgt].get(str(ridx))
                                if not old or (old and ts > old.get("timestamp","")):
                                    ovd["overrides"][tgt][str(ridx)] = {"new_value": newv, "timestamp": ts}
                            save_overrides(proj, ovd); overrides = ovd
                        st.success("Import merged.")
                    except Exception as e:
                        st.error(f"Import failed: {e}")
            with st.popover("Import .json"):
                upj = st.file_uploader("Choose .json", type=["json"], key="ai_import_json")
                if upj is not None:
                    try:
                        data = json.load(upj)
                        if isinstance(data, dict):
                            if "enrichment" in data and isinstance(data["enrichment"], dict):
                                cfg = load_enrichment(proj)
                                dfE = []
                                for t, node in data["enrichment"].get("targets", {}).items():
                                    for r in (node.get("rules",[]) or []):
                                        dfE.append({"Target": t, "Output value": r.get("output_value",""), "Keyword": r.get("keyword",""), "Weight": r.get("weight",3.0)})
                                dfE = pd.DataFrame(dfE).fillna("")
                                for _, r in dfE.iterrows():
                                    tgt = str(r.get("Target","")).strip()
                                    ovv = str(r.get("Output value","")).strip()
                                    kw  = re.sub(r"\s+"," ", str(r.get("Keyword","")).strip().lower())
                                    w   = min(5.0, max(1.0, safe_float(r.get("Weight",3.0), 3.0)))
                                    if not tgt or not ovv or not kw: continue
                                    node = cfg["targets"].setdefault(tgt, {"sources": [], "rules": []})
                                    pair_found=False
                                    for rr in node["rules"]:
                                        if rr.get("output_value","").strip().lower() == ovv.lower():
                                            if rr.get("keyword","").strip().lower() == kw or levenshtein(kw, rr.get("keyword","").strip().lower()) < 2:
                                                rr["keyword"] = kw; rr["weight"] = w; pair_found=True; break
                                    if not pair_found:
                                        node["rules"].append({"output_value": ovv, "keyword": kw, "weight": w, "regex": False, "fuzzy": False})
                                save_enrichment(proj, cfg); enrichment_cfg = cfg
                            if "overrides" in data and isinstance(data["overrides"], dict):
                                ovd = load_overrides(proj)
                                for tgt, mapping in (data["overrides"] or {}).items():
                                    ovd["overrides"].setdefault(tgt, {})
                                    for ridx, meta in (mapping or {}).items():
                                        ts = str(meta.get("timestamp","")) or datetime.datetime.utcnow().isoformat()
                                        old = ovd["overrides"][tgt].get(str(ridx))
                                        if not old or (old and ts > old.get("timestamp","")):
                                            ovd["overrides"][tgt][str(ridx)] = {"new_value": meta.get("new_value",""), "timestamp": ts}
                                save_overrides(proj, ovd); overrides = ovd
                        st.success("Import merged.")
                    except Exception as e:
                        st.error(f"Import failed: {e}")
        else:
            if st.button("Import .xlsx", key="ai_import_xlsx_btn"):
                st.session_state["show_imp_xlsx"] = not st.session_state.get("show_imp_xlsx", False)
            if st.button("Import .json", key="ai_import_json_btn"):
                st.session_state["show_imp_json"] = not st.session_state.get("show_imp_json", False)
            if st.session_state.get("show_imp_xlsx", False):
                upx2 = st.file_uploader("Choose .xlsx", type=["xlsx"], key="ai_import_xlsx_fallback")
                if upx2 is not None:
                    try:
                        wb = pd.read_excel(upx2, sheet_name=None)
                        if "Enrichment" in wb:
                            dfE = wb["Enrichment"].fillna("")
                            cfg = load_enrichment(proj)
                            for _, r in dfE.iterrows():
                                tgt = str(r.get("Target","")).strip()
                                ov  = str(r.get("Output value","")).strip()
                                kw  = re.sub(r"\s+"," ", str(r.get("Keyword","")).strip().lower())
                                w   = min(5.0, max(1.0, safe_float(r.get("Weight",3.0), 3.0)))
                                if not tgt or not ov or not kw: continue
                                node = cfg["targets"].setdefault(tgt, {"sources": [], "rules": []})
                                pair_found = False
                                for rr in node["rules"]:
                                    if rr.get("output_value","").strip().lower() == ov.lower():
                                        if rr.get("keyword","").strip().lower() == kw or levenshtein(kw, rr.get("keyword","").strip().lower()) < 2:
                                            rr["keyword"] = kw; rr["weight"] = w; pair_found = True; break
                                if not pair_found:
                                    node["rules"].append({"output_value": ov, "keyword": kw, "weight": w, "regex": False, "fuzzy": False})
                            save_enrichment(proj, cfg); enrichment_cfg = cfg
                        if "Overrides" in wb:
                            dfO = wb["Overrides"].fillna("")
                            ovd = load_overrides(proj)
                            for _, r in dfO.iterrows():
                                tgt = str(r.get("Target","")).strip()
                                if tgt == "": continue
                                ridx = r.get("RowIndex", None)
                                if pd.isna(ridx): continue
                                ridx = int(ridx)
                                newv = str(r.get("NewValue",""))
                                ts   = str(r.get("Timestamp","")) or datetime.datetime.utcnow().isoformat()
                                ovd["overrides"].setdefault(tgt, {})
                                old = ovd["overrides"][tgt].get(str(ridx))
                                if not old or (old and ts > old.get("timestamp","")):
                                    ovd["overrides"][tgt][str(ridx)] = {"new_value": newv, "timestamp": ts}
                            save_overrides(proj, ovd); overrides = ovd
                        st.success("Import merged.")
                    except Exception as e:
                        st.error(f"Import failed: {e}")
            if st.session_state.get("show_imp_json", False):
                upj2 = st.file_uploader("Choose .json", type=["json"], key="ai_import_json_fallback")
                if upj2 is not None:
                    try:
                        data = json.load(upj2)
                        if isinstance(data, dict):
                            if "enrichment" in data and isinstance(data["enrichment"], dict):
                                cfg = load_enrichment(proj)
                                dfE = []
                                for t, node in data["enrichment"].get("targets", {}).items():
                                    for r in (node.get("rules",[]) or []):
                                        dfE.append({"Target": t, "Output value": r.get("output_value",""), "Keyword": r.get("keyword",""), "Weight": r.get("weight",3.0)})
                                dfE = pd.DataFrame(dfE).fillna("")
                                for _, r in dfE.iterrows():
                                    tgt = str(r.get("Target","")).strip()
                                    ovv = str(r.get("Output value","")).strip()
                                    kw  = re.sub(r"\s+"," ", str(r.get("Keyword","")).strip().lower())
                                    w   = min(5.0, max(1.0, safe_float(r.get("Weight",3.0), 3.0)))
                                    if not tgt or not ovv or not kw: continue
                                    node = cfg["targets"].setdefault(tgt, {"sources": [], "rules": []})
                                    pair_found=False
                                    for rr in node["rules"]:
                                        if rr.get("output_value","").strip().lower() == ovv.lower():
                                            if rr.get("keyword","").strip().lower() == kw or levenshtein(kw, rr.get("keyword","").strip().lower()) < 2:
                                                rr["keyword"] = kw; rr["weight"] = w; pair_found=True; break
                                    if not pair_found:
                                        node["rules"].append({"output_value": ovv, "keyword": kw, "weight": w, "regex": False, "fuzzy": False})
                                save_enrichment(proj, cfg); enrichment_cfg = cfg
                            if "overrides" in data and isinstance(data["overrides"], dict):
                                ovd = load_overrides(proj)
                                for tgt, mapping in (data["overrides"] or {}).items():
                                    ovd["overrides"].setdefault(tgt, {})
                                    for ridx, meta in (mapping or {}).items():
                                        ts = str(meta.get("timestamp","")) or datetime.datetime.utcnow().isoformat()
                                        old = ovd["overrides"][tgt].get(str(ridx))
                                        if not old or (old and ts > old.get("timestamp","")):
                                            ovd["overrides"][tgt][str(ridx)] = {"new_value": meta.get("new_value",""), "timestamp": ts}
                                save_overrides(proj, ovd); overrides = ovd
                        st.success("Import merged.")
                    except Exception as e:
                        st.error(f"Import failed: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    # 3b) AI Rule Generator (from your data)
    with st.expander("🧠 AI Rule Generator (from your data)", expanded=False):
        client_rg, err_rg = get_openai_client()
        if client_rg is None or err_rg:
            st.info("OpenAI client not available. Add your OPENAI_API_KEY to use Rule Generator.")
        else:
            tgt_rg = st.selectbox("Target to learn rules for", all_targets, key="rg_target")
            n_per_value = int(st.number_input("Max sample rows per output_value", 5, 200, 20, 5, key="rg_n_per_value"))
            k_rules = int(st.number_input("Rules to propose per output_value", 1, 20, 5, 1, key="rg_k_rules"))
            default_weight = float(st.slider("Default weight for new rules", 1.0, 5.0, 3.0, 0.5, key="rg_weight"))
            go_rg = st.button("Generate candidate rules", key="rg_generate")

            if go_rg:
                if tgt_rg not in processed_df.columns:
                    st.warning("Target not in processed data. Run processing first.")
                else:
                    # Collect samples grouped by output_value
                    df_ok = processed_df.copy()
                    df_ok = df_ok[df_ok[tgt_rg].astype(str).str.strip() != ""]
                    samples = {}
                    sources = enrichment_cfg.get("targets", {}).get(tgt_rg, {}).get("sources", [])
                    for ov, g in df_ok.groupby(df_ok[tgt_rg].astype(str).str.strip()):
                        take = g.head(n_per_value)
                        contexts = []
                        for _, row in take.iterrows():
                            ctx = " ".join([str(row.get(c, "")) for c in sources]) if sources else " ".join([str(row[c]) for c in row.index])
                            if ctx.strip():
                                contexts.append(ctx[:512])
                        if contexts:
                            samples[ov] = contexts

                    if not samples:
                        st.info("No data with non-empty values for this target.")
                    else:
                        # Build prompt safely (avoid braces in f-strings)
                        prompt_blocks = []
                        for ov, ctxs in samples.items():
                            block = 'Output Value: "{}"\nExamples:\n- '.format(ov) + "\n- ".join(ctxs[:n_per_value])
                            prompt_blocks.append(block)

                        prompt_text = (
                            f'You will propose keywords for enrichment rules for target "{tgt_rg}" from example rows grouped by output_value.\n\n'
                            f'For EACH output_value below, return up to {k_rules} precise, lowercase keywords or short phrases that strongly indicate that output_value in future rows.\n'
                            'Return strict JSON object with a top-level key "rules" whose value is a list of objects like: '
                            '[{"output_value":"...", "keyword":"...", "weight":3}]\n'
                            f'- use weight {default_weight} unless otherwise obvious from examples; value between 1 and 5.\n'
                            '- keyword must be lowercase; no punctuation except spaces.\n'
                            '- avoid duplicates; avoid overly generic words.\n\n'
                            'Groups:\n'
                            + "\n\n".join(prompt_blocks)
                        )

                        try:
                            resp = client_rg.chat.completions.create(
                                model=st.session_state["ai_form_state"].get("model", "gpt-4o-mini"),
                                temperature=0.1,
                                response_format={"type": "json_object"},
                                messages=[
                                    {"role": "system", "content": "You generate compact enrichment rules based on user data. Output strict JSON."},
                                    {"role": "user", "content": prompt_text},
                                ],
                            )
                            content = resp.choices[0].message.content

                            # Show token usage (optional)
                            try:
                                u = resp.usage
                                st.caption(f"RuleGen tokens: prompt {getattr(u, 'prompt_tokens', 0)} / completion {getattr(u, 'completion_tokens', 0)}")
                            except Exception:
                                pass

                            # Parse JSON (supports either {"rules":[...]} or a raw list [...])
                            rules_json = []
                            try:
                                data = json.loads(content)
                                if isinstance(data, dict) and isinstance(data.get("rules"), list):
                                    rules_json = data["rules"]
                                elif isinstance(data, list):
                                    rules_json = data
                            except Exception as e:
                                st.error(f"Could not parse AI response as JSON: {e}")
                                rules_json = []

                            if not isinstance(rules_json, list) or not rules_json:
                                st.info("No rules returned.")
                            else:
                                # Normalize and show for approval
                                cand_df = pd.DataFrame(rules_json).fillna("")
                                if "weight" not in cand_df.columns:
                                    cand_df["weight"] = default_weight
                                cand_df["Select?"] = True
                                st.markdown("Review and approve rules:")
                                ed = st.data_editor(
                                    cand_df[["output_value", "keyword", "weight", "Select?"]],
                                    use_container_width=True,
                                    hide_index=True,
                                    key="rg_editor",
                                    column_config={
                                        "output_value": st.column_config.TextColumn("Output value", width="large"),
                                        "keyword": st.column_config.TextColumn("Keyword (lowercase)", width="large"),
                                        "weight": st.column_config.NumberColumn("Weight", min_value=1.0, max_value=5.0, step=0.5, width="small"),
                                        "Select?": st.column_config.CheckboxColumn("Select?", width="small"),
                                    },
                                )
                                if st.button("Save selected rules to Enrichment", key="rg_save_rules"):
                                    cfg = load_enrichment(proj)
                                    node = cfg["targets"].setdefault(tgt_rg, {"sources": [], "rules": []})
                                    existing = {(r.get("output_value", "").strip().lower(), r.get("keyword", "").strip().lower()) for r in node.get("rules", [])}
                                    added = 0
                                    for _, r in ed.iterrows():
                                        if not r.get("Select?", False):
                                            continue
                                        ovv = str(r.get("output_value", "")).strip()
                                        kw = str(r.get("keyword", "")).strip().lower()
                                        w = min(5.0, max(1.0, safe_float(r.get("weight", default_weight), default_weight)))
                                        if not ovv or not kw:
                                            continue
                                        pair = (ovv.strip().lower(), kw)
                                        if pair in existing:
                                            continue
                                        node["rules"].append(
                                            {
                                                "output_value": ovv,
                                                "keyword": kw,
                                                "weight": w,
                                                "regex": False,
                                                "fuzzy": False,
                                            }
                                        )
                                        existing.add(pair)
                                        added += 1
                                    save_enrichment(proj, cfg)
                                    st.success(f"Saved {added} rule(s).")
                        except Exception as e:
                            st.error(f"AI Rule Generator failed: {e}")
    # 4) Inline Overrides
    with st.expander("Inline Overrides", expanded=False):
        st.session_state["ov_wrap_text"] = st.checkbox("Wrap text in table", value=st.session_state.get("ov_wrap_text", True), key="ov_wrap_toggle")
        tgt2 = st.selectbox("Step 1: Select Target Field", all_targets, index=all_targets.index(st.session_state.get("ov_selected_target", all_targets[0])) if st.session_state.get("ov_selected_target") in all_targets else 0, key="ov_target_select")
        st.session_state["ov_selected_target"] = tgt2
        vcol = f"{tgt2}_Value"; scol = f"{tgt2}_Status"; mkw_json_col = f"{tgt2}_MatchedKeywords"

        st.markdown("Step 2: Select fields to show (order preserved)")
        all_processed_cols2 = list(processed_df.columns)
        special_cols2 = ["MatchedKeywords (parsed)"]
        default_show2 = st.session_state.get("ov_selected_fields") or [c for c in ["University Name","Course Name", tgt2, "MatchedKeywords (parsed)"] if (c=="MatchedKeywords (parsed)") or (c in all_processed_cols2)]
        current_selected2 = st.multiselect("Fields to show", options=special_cols2 + all_processed_cols2, default=default_show2, key="ov_fields_to_show")
        st.session_state["ov_selected_fields"] = current_selected2

        status_choices = ["UNCLASSIFIED","MULTI","OK","OVERRIDE"]
        selected_statuses = st.multiselect("Filter by Status", status_choices, default=["UNCLASSIFIED","MULTI","OVERRIDE"], key="ov_status_filter")

        mask_rows = audit_df[scol].isin(selected_statuses) if scol in audit_df.columns else pd.Series([], dtype=bool)
        base_cols = [c for c in ["RowIndex", vcol, scol] if c in audit_df.columns]
        base_rows = audit_df.loc[mask_rows, base_cols] if base_cols else pd.DataFrame(columns=["RowIndex"])
        if "RowIndex" not in base_rows.columns:
            base_rows["RowIndex"] = []

        if mkw_json_col in audit_df.columns:
            def parse_kw(js):
                try:
                    d = json.loads(js); flat=[]
                    for _, lst in d.items(): flat.extend(lst)
                    return ", ".join(sorted(set([x for x in flat if str(x).strip()])))
                except: return ""
            base_rows["MatchedKeywords (parsed)"] = audit_df.loc[mask_rows, mkw_json_col].apply(parse_kw)
        else:
            base_rows["MatchedKeywords (parsed)"] = ""

        disp = pd.DataFrame({"RowIndex": base_rows["RowIndex"]})
        for col in current_selected2:
            if col == "MatchedKeywords (parsed)":
                disp[col] = base_rows["MatchedKeywords (parsed)"].values
            else:
                if col in processed_df.columns:
                    disp[col] = disp["RowIndex"].apply(lambda ix: processed_df.at[ix, col] if ix in processed_df.index else "")
                else:
                    disp[col] = ""
        if tgt2 not in disp.columns and tgt2 in processed_df.columns:
            disp[tgt2] = disp["RowIndex"].apply(lambda ix: processed_df.at[ix, tgt2] if ix in processed_df.index else "")
        disp["OverrideValue"] = disp.get(tgt2, "")
        disp["NewKeyword/Pattern"] = ""
        disp["Weight(1-5)"] = 3.0
        disp["Save?"] = False

        edited = st.data_editor(
            disp,
            num_rows="fixed",
            use_container_width=True,
            key="override_guided_table",
            hide_index=True,
            height=580,
            column_config={
                "RowIndex": st.column_config.NumberColumn("Row", disabled=True, width="small"),
                "OverrideValue": st.column_config.TextColumn("OverrideValue", width="large"),
                "NewKeyword/Pattern": st.column_config.TextColumn("Keyword/Pattern", width="large"),
                "Weight(1-5)": st.column_config.NumberColumn("Weight(1-5)", min_value=1.0, max_value=5.0, step=0.5, width="small"),
                "MatchedKeywords (parsed)": st.column_config.TextColumn("MatchedKeywords (parsed)", width="large"),
                "Save?": st.column_config.CheckboxColumn("Save this row?", width="small")
            }
        )
        st.markdown("<div class='inline-note'>Tip: Use 'Quick Save All Edited' to persist changed OverrideValue without ticking each row.</div>", unsafe_allow_html=True)

        colA, colB = st.columns([1,1])
        with colA:
            if st.button("Apply Selected Row Saves", key="apply_selected_row_saves"):
                changes = 0
                rules_added = 0
                cfg = load_enrichment(proj)
                node = cfg["targets"].setdefault(tgt2, {"sources": [], "rules": []})
                existing_pairs = {(r["output_value"], r["keyword"]) for r in node["rules"]}
                for _, r in edited.iterrows():
                    if not r.get("Save?", False): continue
                    ridx = int(r["RowIndex"])
                    new_val = str(r.get("OverrideValue","")).strip()
                    kw     = str(r.get("NewKeyword/Pattern","")).strip()
                    w      = safe_float(r.get("Weight(1-5)", 3.0), 3.0)
                    if new_val != "":
                        overrides["overrides"].setdefault(tgt2, {})
                        overrides["overrides"][tgt2][str(ridx)] = {"new_value": new_val, "timestamp": datetime.datetime.utcnow().isoformat()}
                        changes += 1
                    if new_val and kw:
                        pair = (new_val, kw.lower())
                        if pair not in existing_pairs:
                            node["rules"].append({
                                "output_value": new_val,
                                "keyword": kw.lower(),
                                "weight": min(5.0, max(1.0, w)),
                                "regex": False,
                                "fuzzy": False
                            })
                            existing_pairs.add(pair)
                            rules_added += 1
                save_overrides(proj, overrides)
                save_enrichment(proj, cfg)
                processed_df2, audit_df2 = apply_overrides_to_processed(processed_df.copy(), audit_df.copy(), overrides)
                st.session_state["processed_df"] = processed_df2
                st.session_state["enrich_audit_df"] = audit_df2
                st.success(f"Saved {changes} override(s). Reinforced {rules_added} rule(s).")
        with colB:
            if st.button("Quick Save All Edited OverrideValues", key="quick_save_all"):
                changes = 0
                overrides_local = load_overrides(proj)
                for _, r in edited.iterrows():
                    ridx = int(r["RowIndex"])
                    new_val = str(r.get("OverrideValue","")).strip()
                    base_val = processed_df.at[ridx, tgt2] if (ridx in processed_df.index and tgt2 in processed_df.columns) else ""
                    if new_val and new_val != base_val:
                        overrides_local["overrides"].setdefault(tgt2, {})
                        overrides_local["overrides"][tgt2][str(ridx)] = {"new_value": new_val, "timestamp": datetime.datetime.utcnow().isoformat()}
                        changes += 1
                save_overrides(proj, overrides_local)
                processed_df2, audit_df2 = apply_overrides_to_processed(processed_df.copy(), audit_df.copy(), overrides_local)
                st.session_state["processed_df"] = processed_df2
                st.session_state["enrich_audit_df"] = audit_df2
                st.success(f"Quick-saved {changes} override(s).")

    # 5) Add Rule to Master
    with st.expander("Add Rule to Master (Output + Keyword + Weight)", expanded=False):
        tgt3 = st.selectbox("Target", all_targets, index=all_targets.index(st.session_state.get("ov_selected_target", all_targets[0])) if st.session_state.get("ov_selected_target") in all_targets else 0, key="add_rule_target")
        node_for_add = enrichment_cfg["targets"].get(tgt3, {"sources": [], "rules": []})
        existing_outputs = sorted(set([r["output_value"] for r in node_for_add.get("rules",[]) if r.get("output_value")]))

        out_mode = st.radio("Output value entry", ["Select existing","Type new"], horizontal=True, key="add_rule_mode")
        if out_mode == "Select existing":
            out_val = st.selectbox("Output Value", existing_outputs + ["(new...)"], key="add_rule_out_sel")
            if out_val == "(new...)":
                out_val = st.text_input("New Output Value", key="add_rule_out_new")
        else:
            out_val = st.text_input("New Output Value", key="add_rule_out_force")
        st.text_input("Keyword / Pattern", key="add_rule_kw")
        w = st.number_input("Weight (1-5)", min_value=1.0, max_value=5.0, value=3.0, step=0.5, key="add_rule_weight")
        if st.button("Save Rule to Enrichment", key="add_rule_save"):
            kw = st.session_state.get("add_rule_kw","").strip()
            if not out_val or not kw:
                st.warning("Provide Output and Keyword.")
            else:
                cfg = load_enrichment(proj)
                node = cfg["targets"].setdefault(tgt3, {"sources": [], "rules": []})
                pair_set = {(r["output_value"], r["keyword"]) for r in node["rules"]}
                if (out_val, kw.lower()) not in pair_set:
                    node["rules"].append({
                        "output_value": out_val,
                        "keyword": kw.lower(),
                        "weight": min(5.0, max(1.0, w)),
                        "regex": False,
                        "fuzzy": False
                    })
                    save_enrichment(proj, cfg)
                    st.success("Rule added to enrichment master.")

    # 6) Re-run Enrichment with comparison
    st.markdown("---")
    st.subheader("Re-run Enrichment (Respects saved overrides) with Comparison")
    before_ana = compute_analytics(audit_df)
    if st.button("Re-run now", key="rerun_now"):
        raw_df = st.session_state["raw_df"]; mapping = st.session_state.get("mapping",{})
        enrichment_cfg_live = load_enrichment(proj)
        tpl_df = safe_read_excel(project_file(proj, TEMPLATE_FILE))
        final_cols = list(tpl_df.columns) if tpl_df is not None else list(processed_df.columns)
        prog = progress_component(); prog(0,"Start")
        out_df = pd.DataFrame(columns=final_cols)
        for i,(tcol,rcol) in enumerate(mapping.items()):
            if tcol in out_df.columns and rcol and rcol in raw_df.columns: out_df[tcol]=raw_df[rcol]
            elif tcol in out_df.columns: out_df[tcol]=""
            prog(5+(i+1)/max(1,len(mapping))*15,"Mapping")
        prepared = build_prepared_rules(enrichment_cfg_live)
        targets = list(prepared.keys())
        audit_rows=[]; aggregated_keywords=[]
        for ridx in range(len(raw_df)):
            raw_row=raw_df.iloc[ridx]
            entry={"RowIndex": ridx}; row_kw=[]
            for t in targets:
                if t not in out_df.columns: out_df[t]=""
                sources = enrichment_cfg_live["targets"][t].get("sources", [])
                if sources:
                    ctx = " ".join(str(raw_row.get(s,"")) for s in sources if s in raw_row.index)
                else:
                    ctx = " ".join(str(raw_row[c]) for c in raw_row.index)
                result = classify_context(ctx.lower(), prepared.get(t, []))
                out_df.loc[ridx, t] = result["value"]
                entry[f"{t}_Value"]=result["value"]; entry[f"{t}_Status"]=result["status"]
                entry[f"{t}_Scores"]=json.dumps(result["totals"]); entry[f"{t}_MatchedKeywords"]=json.dumps(result["matched"])
                entry[f"{t}__MatchedKeywords"]=result["audit_str"] or ""
                for _, kws in result["matched"].items(): row_kw.extend(kws)
            aggregated_keywords.append(", ".join(sorted(set(row_kw))) if row_kw else "")
            if ridx % 25 == 0: prog(25+(ridx/len(raw_df))*55,"Enrichment")
            audit_rows.append(entry)
        out_df["All_Enrichment_Matched_Keywords"] = aggregated_keywords
        new_audit = pd.DataFrame(audit_rows)
        overrides_live = load_overrides(proj)
        out_df, new_audit = apply_overrides_to_processed(out_df, new_audit, overrides_live)
        st.session_state["processed_df"] = out_df; st.session_state["enrich_audit_df"] = new_audit
        prog(100,"Done")
        after_ana = compute_analytics(new_audit)
        try:
            b = before_ana.set_index("Target"); a = after_ana.set_index("Target")
            targets_union = sorted(set(b.index) | set(a.index))
            rows=[]
            for t in targets_union:
                b_row = b.loc[t] if t in b.index else pd.Series({"OK":0,"MULTI":0,"UNCLASSIFIED":0,"OVERRIDE":0,"TOTAL":0})
                a_row = a.loc[t] if t in a.index else pd.Series({"OK":0,"MULTI":0,"UNCLASSIFIED":0,"OVERRIDE":0,"TOTAL":0})
                rows.append({"Target": t,
                             "OK (Δ)": int(a_row.get("OK",0)-b_row.get("OK",0)),
                             "MULTI (Δ)": int(a_row.get("MULTI",0)-b_row.get("MULTI",0)),
                             "UNCLASSIFIED (Δ)": int(a_row.get("UNCLASSIFIED",0)-b_row.get("UNCLASSIFIED",0)),
                             "OVERRIDE (Δ)": int(a_row.get("OVERRIDE",0)-b_row.get("OVERRIDE",0)),
                             "TOTAL (new)": int(a_row.get("TOTAL",0))})
            comp_df = pd.DataFrame(rows)
        except Exception:
            comp_df = pd.DataFrame()
        st.session_state["last_comp"] = comp_df if not comp_df.empty else None
        st.success("Re-run complete.")

# =========================================================
# STEP 7: Post-Processing
# =========================================================
elif current_step == "7. Post-Processing":
    st.title("Post-Processing")
    proj = st.session_state["active_project"]
    if not proj: st.stop()
    if st.session_state.get("processed_df") is None:
        st.warning("Run processing first."); st.stop()
    df = st.session_state["processed_df"].copy()
    st.subheader("Preview")
    st.dataframe(df.head(400), use_container_width=True)

    tabs = st.tabs(["Split","Regex Replace","Strip","Bulk Populate by Target Values"])
    with tabs[0]:
        col = st.selectbox("Column", [""]+list(df.columns), key="pp_split_col")
        delim = st.text_input("Delimiter", value=",", key="pp_split_delim")
        max_parts = st.number_input("Max parts (0=auto)", min_value=0, value=0, key="pp_split_maxparts")
        prefix = st.text_input("Prefix", value="Split_", key="pp_split_prefix")
        keep = st.checkbox("Keep Original", value=True, key="pp_split_keep")
        if st.button("Apply Split", key="pp_split_apply"):
            if col:
                parts = df[col].astype(str).str.split(delim)
                max_len = max(len(p) if isinstance(p,list) else 1 for p in parts)
                if max_parts>0: max_len = min(max_len, max_parts)
                for i in range(max_len):
                    df[f"{prefix}{i+1}"] = parts.apply(lambda lst: lst[i].strip() if isinstance(lst,list) and i < len(lst) else "")
                if not keep: df.drop(columns=[col], inplace=True)
                st.session_state["processed_df"] = df
                st.success("Split applied.")
    with tabs[1]:
        rcols = st.multiselect("Columns", list(df.columns), key="pp_regex_columns")
        patt  = st.text_input("Pattern", value=r"[$,]", key="pp_regex_pattern")
        repl  = st.text_input("Replacement", value="", key="pp_regex_repl")
        ignore= st.checkbox("Ignore Case", value=True, key="pp_regex_ic")
        if st.button("Apply Regex Replace", key="pp_regex_apply"):
            flags = re.IGNORECASE if ignore else 0
            for c in rcols:
                df[c] = df[c].astype(str).apply(lambda x: re.sub(patt, repl, x, flags=flags))
            st.session_state["processed_df"] = df
            st.success("Regex replace applied.")
    with tabs[2]:
        scols = st.multiselect("Columns", list(df.columns), key="pp_strip_columns")
        chars = st.text_input("Characters to strip", value="$€£ ", key="pp_strip_chars")
        if st.button("Apply Strip", key="pp_strip_apply"):
            for c in scols:
                df[c] = df[c].astype(str).str.strip(chars)
            st.session_state["processed_df"] = df
            st.success("Strip applied.")
    with tabs[3]:
        st.caption("Define rules: target column & values, optional filter, then column to populate and a value to write.")
        groups = st.session_state["bulk_groups"]

        def build_filter_mask(series: pd.Series, op: str, val: str) -> pd.Series:
            s = series.astype(str)
            v = str(val)
            if op == "Contains":
                return s.str.contains(re.escape(v), case=False, na=False)
            if op == "Does not Contain":
                return ~s.str.contains(re.escape(v), case=False, na=False)
            if op == "Equals":
                return s.str.strip().str.casefold() == v.strip().casefold()
            if op == "Does not Equal":
                return s.str.strip().str.casefold() != v.strip().casefold()
            if op == "Begins with":
                return s.str.strip().str.lower().str.startswith(v.strip().lower(), na=False)
            return pd.Series([True]*len(s), index=s.index)

        # Rule entries
        for idx, grp in enumerate(groups):
            st.markdown(f"Rule {idx+1}")

            cols = st.columns([2, 3, 2, 2, 2])

            # 1) Target column
            with cols[0]:
                tcol = st.selectbox(
                    f"Target column #{idx+1}",
                    [""] + list(df.columns),
                    index=([""] + list(df.columns)).index(grp["target_col"]) if grp["target_col"] in df.columns else 0,
                    key=f"bulk_tcol_{idx}"
                )
                grp["target_col"] = tcol

            # 2) Values to match
            with cols[1]:
                options = sorted(df[tcol].dropna().astype(str).str.strip().unique().tolist()) if tcol else []
                tvals = st.multiselect(
                    f"Match values #{idx+1}",
                    options,
                    default=[v for v in grp["target_vals"] if v in options],
                    key=f"bulk_tvals_{idx}"
                )
                grp["target_vals"] = tvals

            # 3) Column to populate
            with cols[2]:
                pop_options = ["(new column...)"] + list(df.columns)
                pop_sel = st.selectbox(
                    f"Populate column #{idx+1}",
                    pop_options,
                    index=pop_options.index(grp["populate_col"]) if grp["populate_col"] in pop_options else 0,
                    key=f"bulk_pcol_{idx}"
                )
                grp["populate_col"] = pop_sel

                if pop_sel == "(new column...)":
                    new_name = st.text_input(
                        f"New column name #{idx+1}",
                        value=grp["new_populate_col"],
                        key=f"bulk_newp_{idx}"
                    )
                    grp["new_populate_col"] = new_name

            # 4) Value to write
            with cols[3]:
                val = st.text_input(
                    f"Value to write #{idx+1}",
                    value=grp["value"],
                    key=f"bulk_val_{idx}"
                )
                grp["value"] = val

            # 5) Remove rule
            with cols[4]:
                if st.button("Remove", key=f"bulk_remove_{idx}"):
                    groups.pop(idx)
                    st.rerun()

            # Optional filter row
            fcols = st.columns([2, 2, 3])
            with fcols[0]:
                fcol = st.selectbox(
                    f"Filter column (optional) #{idx+1}",
                    [""] + list(df.columns),
                    index=([""] + list(df.columns)).index(grp["filter_col"]) if grp["filter_col"] in df.columns else 0,
                    key=f"bulk_fcol_{idx}"
                )
                grp["filter_col"] = fcol
            with fcols[1]:
                fop = st.selectbox(
                    f"Filter operator #{idx+1}",
                    ["", "Contains", "Equals", "Does not Equal", "Begins with", "Does not Contain"],
                    index=["", "Contains", "Equals", "Does not Equal", "Begins with", "Does not Contain"].index(grp["filter_op"]) if grp["filter_op"] in ["", "Contains", "Equals", "Does not Equal", "Begins with", "Does not Contain"] else 0,
                    key=f"bulk_fop_{idx}"
                )
                grp["filter_op"] = fop
            with fcols[2]:
                fval = st.text_input(
                    f"Filter value #{idx+1}",
                    value=grp["filter_val"],
                    key=f"bulk_fval_{idx}"
                )
                grp["filter_val"] = fval

            st.write("---")

        c1, c2 = st.columns([1,2])
        with c1:
            if st.button("Add more fields", key="bulk_add_more"):
                groups.append({
                    "target_col":"", "target_vals":[], "populate_col":"", "new_populate_col":"",
                    "value":"", "filter_col":"", "filter_op":"", "filter_val":""
                })
        with c2:
            if st.button("Populate Now", key="bulk_populate_now"):
                changes = 0
                for grp in groups:
                    tcol = grp.get("target_col") or ""
                    tvals = grp.get("target_vals") or []
                    pcol_sel = grp.get("populate_col") or ""
                    new_p = grp.get("new_populate_col") or ""
                    val = grp.get("value","")
                    fcol = grp.get("filter_col") or ""
                    fop  = grp.get("filter_op") or ""
                    fval = grp.get("filter_val") or ""
                    if not tcol or not tvals: continue
                    if pcol_sel == "(new column...)":
                        if not new_p.strip(): continue
                        pcol = new_p.strip()
                        if pcol not in df.columns: df[pcol] = ""
                    else:
                        pcol = pcol_sel
                    mask_target = df[tcol].astype(str).str.strip().isin([str(v).strip() for v in tvals])
                    if fcol and fop and fval != "":
                        mask_filter = build_filter_mask(df[fcol], fop, fval)
                        mask_final = mask_target & mask_filter
                    else:
                        mask_final = mask_target
                    df.loc[mask_final, pcol] = val
                    changes += int(mask_final.sum())
                st.session_state["processed_df"] = df
                st.success(f"Populated {changes} cell(s).")

    st.subheader("Updated Preview (Top 300)")
    st.dataframe(st.session_state["processed_df"].head(300), use_container_width=True)
    st.info("Proceed to '8. Download & Review'.")

# =========================================================
# STEP 8: Download & Review
# =========================================================
elif current_step == "8. Download & Review":
    st.title("Download & Review")
    proj = st.session_state["active_project"]
    if not proj: st.stop()
    if st.session_state.get("processed_df") is None:
        st.warning("No processed data."); st.stop()
    processed_df = st.session_state["processed_df"].copy()
    audit_df     = st.session_state.get("enrich_audit_df", pd.DataFrame()).copy()
    flagged_df   = st.session_state.get("flagged_df", pd.DataFrame()).copy()
    run_meta     = st.session_state.get("run_meta", {})
    overrides    = load_overrides(proj)
    processed_df, audit_df = apply_overrides_to_processed(processed_df, audit_df, overrides)

    st.subheader("Final Data (Top 300)")
    preview = processed_df.head(300).copy()
    for tgt in st.session_state.get("last_processing_targets", []):
        scol = f"{tgt}_Status"
        if scol in audit_df.columns:
            try:
                idx_map = audit_df.set_index("RowIndex")[scol]
                preview[scol] = idx_map.reindex(preview.index).fillna("")
            except:
                pass
    st.dataframe(preview, use_container_width=True)

    excel_bytes = export_excel(processed_df, flagged_df, audit_df, run_meta, proj)
    st.download_button("⬇️ Download final.xlsx", data=excel_bytes, file_name=f"{proj}_final.xlsx")

    if not flagged_df.empty:
        st.subheader("Flagged Rows")
        st.dataframe(flagged_df.head(300), use_container_width=True)

    st.subheader("Enrichment Audit (Top 300)")
    st.dataframe(audit_df.head(300), use_container_width=True)

    st.subheader("Overrides")
    if overrides.get("overrides"): st.json(overrides["overrides"])
    else: st.write("None")

    st.subheader("Metadata")
    st.json(run_meta)

# =========================================================
# STEP 9: OTHER TOOLS
# =========================================================
elif current_step == "9. Other tools":
    st.title("Other tools")
    st.caption("Pick a tool below and click Launch to open it.")

    tools = [
        {"key":"merge", "icon":"🧩", "name":"Merge Excel/CSV", "desc":"Merge all Excel/CSV files in a folder into one Excel with unified headers + Source_File column."},
        {"key":"intake", "icon":"🗓️", "name":"Intake Split (Months → Intakes)", "desc":"Create an 'Intake Split' sheet from a chosen months column (Fall/Spring/Summer/Winter)."},
    ]

    cols = st.columns(3)
    for i, tool in enumerate(tools):
        with cols[i % 3]:
            st.markdown(f"<div class='section-box'><div class='tool-title'>{tool['icon']} {tool['name']}</div><div class='tool-desc'>{tool['desc']}</div></div>", unsafe_allow_html=True)
            if st.button(f"Launch {tool['name']}", key=f"launch_{tool['key']}"):
                st.session_state["other_tools_selected"] = tool["key"]
    st.markdown("---")

    def mac_folder_picker():
        script = '''
        set chosenFolder to POSIX path of (choose folder with prompt "Select folder with Excel/CSV files to merge")
        return chosenFolder
        '''
        try:
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            st.error(f"Folder picker failed: {e}")
            return ""
    def mac_file_picker():
        script = '''
        set chosenFile to POSIX path of (choose file with prompt "Select Excel file for intake split")
        return chosenFile
        '''
        try:
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            st.error(f"File picker failed: {e}")
            return ""

    sel = st.session_state.get("other_tools_selected","")

    if sel == "merge":
        st.subheader("🧩 Merge Excel/CSV Files (Mac folder picker or manual path)")
        pick_cols = st.columns([1,2])
        with pick_cols[0]:
            if platform.system() == "Darwin":
                if st.button("Pick Folder (Mac)", key="merge_pick_folder"):
                    path = mac_folder_picker()
                    if path:
                        st.session_state["merge_folder"] = path
            else:
                st.info("Mac-only picker not available on this OS.")
        with pick_cols[1]:
            st.text_input("Folder path", key="merge_folder_path_override", value=st.session_state.get("merge_folder",""))

        if st.button("Scan & Merge", key="merge_scan"):
            folder_path = st.session_state.get("merge_folder_path_override","").strip() or st.session_state.get("merge_folder","").strip()
            if not folder_path or not os.path.isdir(folder_path):
                st.warning("Please provide a valid folder path.")
            else:
                with st.spinner("Scanning files..."):
                    excel_files = glob.glob(os.path.join(folder_path, "*.xlsx"))
                    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
                    all_files = excel_files + csv_files
                if not all_files:
                    st.warning("No Excel or CSV files found in this folder.")
                else:
                    st.write(f"Found {len(all_files)} files.")
                    def read_headers(file):
                        if file.lower().endswith(".csv"):
                            return pd.read_csv(file, nrows=0).columns.map(str).str.strip().tolist()
                        else:
                            return pd.read_excel(file, nrows=0).columns.map(str).str.strip().tolist()
                    try:
                        base_headers = read_headers(all_files[0])
                    except Exception as e:
                        st.error(f"Failed reading headers from first file: {e}")
                        base_headers = []
                    extra_headers = []
                    for f in all_files[1:]:
                        try:
                            headers = read_headers(f)
                            for h in headers:
                                if h not in base_headers and h not in extra_headers:
                                    extra_headers.append(h)
                        except Exception as e:
                            st.warning(f"Error reading headers from {os.path.basename(f)}: {e}")
                    final_headers = base_headers + extra_headers
                    if "Source_File" not in final_headers:
                        final_headers.append("Source_File")

                    merged_data=[]
                    prog = st.progress(0)
                    for i, f in enumerate(all_files, start=1):
                        try:
                            if f.lower().endswith(".csv"):
                                dfm = pd.read_csv(f, dtype=str)
                            else:
                                dfm = pd.read_excel(f, dtype=str)
                            dfm = dfm.dropna(how='all')
                            dfm.columns = dfm.columns.map(str).str.strip()
                            for col in final_headers:
                                if col not in dfm.columns:
                                    dfm[col] = None
                            dfm = dfm[final_headers]
                            dfm["Source_File"] = os.path.basename(f)
                            merged_data.append(dfm)
                        except Exception as e:
                            st.warning(f"Error merging file {os.path.basename(f)}: {e}")
                        prog.progress(int(i/len(all_files)*100))
                    if not merged_data:
                        st.error("No data merged.")
                    else:
                        final_df = pd.concat(merged_data, ignore_index=True).reset_index(drop=True)
                        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        out_name = f"Merged_Master_File_{ts}.xlsx"
                        bio = io.BytesIO()
                        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
                            final_df.to_excel(writer, index=False, sheet_name="Merged")
                        bio.seek(0)
                        st.session_state["merge_output_bytes"] = bio.getvalue()
                        st.session_state["merge_output_name"] = out_name
                        try:
                            out_path = os.path.join(folder_path, out_name)
                            with open(out_path, "wb") as f:
                                f.write(st.session_state["merge_output_bytes"])
                            st.success(f"Merged file saved at: {out_path}")
                        except Exception as e:
                            st.info(f"Could not write to folder: {e}")

                        st.download_button(
                            "⬇️ Download merged Excel",
                            data=st.session_state["merge_output_bytes"],
                            file_name=st.session_state["merge_output_name"]
                        )
                        st.write("Preview (Top 100 rows)")
                        st.dataframe(final_df.head(100), use_container_width=True)

    elif sel == "intake":
        st.subheader("🗓️ Intake Split (Months → Intakes)")
        st.caption("Create 'Intake Split' sheet (Fall/Spring/Summer/Winter) from a selected months column.")

        MONTHS_MAP = {'jan':'January','feb':'February','mar':'March','apr':'April','may':'May','jun':'June','jul':'July','aug':'August','sep':'September','oct':'October','nov':'November','dec':'December'}
        ABBREV = {'January':'Jan','February':'Feb','March':'Mar','April':'Apr','May':'May','June':'Jun','July':'Jul','August':'Aug','September':'Sep','October':'Oct','November':'Nov','December':'Dec'}
        FALL = {'August','September','October'}
        SPRING = {'January','February','March'}
        SUMMER = {'April','May','June','July'}
        WINTER = {'November','December'}

        def normalize_months_cell(value):
            if pd.isna(value): return []
            s = str(value).lower()
            s = re.sub(r'\d{4}', '', s)
            s = re.sub(r'\d{1,2}:\d{2}:\d{2}', '', s)
            parts = re.split(r'[,/ ]+', s)
            out=[]
            for p in parts:
                p=p.strip()
                if p in MONTHS_MAP:
                    out.append(MONTHS_MAP[p])
            return out
        def classify_intakes(months):
            fall_m   = [ABBREV[m] for m in months if m in FALL]
            spring_m = [ABBREV[m] for m in months if m in SPRING]
            summer_m = [ABBREV[m] for m in months if m in SUMMER]
            winter_m = [ABBREV[m] for m in months if m in WINTER]
            return [
                ", ".join(fall_m) if fall_m else "",
                ", ".join(spring_m) if spring_m else "",
                ", ".join(summer_m) if summer_m else "",
                ", ".join(winter_m) if winter_m else "",
            ]
        def dataframe_to_worksheet(ws, df: pd.DataFrame):
            for j, col in enumerate(df.columns, start=1):
                ws.cell(row=1, column=j, value=col)
            for i, (_, row) in enumerate(df.iterrows(), start=2):
                for j, col in enumerate(df.columns, start=1):
                    ws.cell(row=i, column=j, value=str(row[col]) if pd.notna(row[col]) else "")

        pick_cols = st.columns([1,2])
        with pick_cols[0]:
            if platform.system() == "Darwin":
                if st.button("Pick Excel (Mac)", key="intake_pick_file"):
                    path = mac_file_picker()
                    if path:
                        st.session_state["intake_mac_path"] = path
            else:
                st.info("Mac-only picker not available on this OS.")
        with pick_cols[1]:
            uploaded_xlsx = st.file_uploader("Excel (.xlsx)", type=["xlsx"], key="intake_uploader")

        src_df = None; src_cols = []; using_mac_path = False
        if st.session_state.get("intake_mac_path"):
            p = st.session_state["intake_mac_path"]
            if os.path.isfile(p):
                try:
                    src_df = pd.read_excel(p)
                    src_cols = list(src_df.columns)
                    using_mac_path = True
                    st.success(f"Loaded: {os.path.basename(p)} ({len(src_df)} rows).")
                except Exception as e:
                    st.error(f"Failed to read Excel: {e}")
        elif uploaded_xlsx is not None:
            try:
                src_df = pd.read_excel(uploaded_xlsx)
                src_cols = list(src_df.columns)
                st.success(f"Uploaded file loaded: {uploaded_xlsx.name} ({len(src_df)} rows).")
            except Exception as e:
                st.error(f"Failed to read uploaded Excel: {e}")

        target_col = st.selectbox("Select the column containing intake months", src_cols, key="intake_target_col") if src_cols else ""

        run_cols = st.columns([1,3])
        with run_cols[0]:
            go = st.button("Run Intake Split", key="intake_run_btn", disabled=(not src_cols or not target_col))
        with run_cols[1]:
            if using_mac_path:
                st.caption("Mode: Mac file path — new sheet will be added to the selected workbook.")
            else:
                st.caption("Mode: Upload — a modified workbook (with new sheet) will be offered for download.")

        if go and src_df is not None and target_col:
            try:
                results = []
                for val in src_df[target_col]:
                    months = normalize_months_cell(val)
                    results.append(classify_intakes(months))
                intake_df = pd.DataFrame(results, columns=["Fall Intake", "Spring Intake", "Summer Intake", "Winter Intake"])

                if using_mac_path:
                    file_path = st.session_state["intake_mac_path"]
                    wb = load_workbook(file_path)
                    if 'Intake Split' in wb.sheetnames:
                        ws_old = wb['Intake Split']
                        wb.remove(ws_old)
                        wb.save(file_path)
                    ws = wb.create_sheet('Intake Split')
                    dataframe_to_worksheet(ws, intake_df)
                    wb.save(file_path)
                    st.success(f"Intake Split complete! New sheet added to: {file_path}")
                else:
                    up_bytes = uploaded_xlsx.getvalue()
                    wb = load_workbook(filename=io.BytesIO(up_bytes))
                    if 'Intake Split' in wb.sheetnames:
                        ws_old = wb['Intake Split']
                        wb.remove(ws_old)
                    ws = wb.create_sheet('Intake Split')
                    dataframe_to_worksheet(ws, intake_df)
                    out_bio = io.BytesIO()
                    wb.save(out_bio); out_bio.seek(0)
                    dl_name = f"{os.path.splitext(uploaded_xlsx.name)[0]}_with_Intake_Split.xlsx"
                    st.download_button("⬇️ Download workbook with Intake Split", data=out_bio.getvalue(), file_name=dl_name)
                    st.success("Intake Split sheet generated. Download the modified workbook above.")
                st.write("Preview (Top 20 rows):")
                st.dataframe(intake_df.head(20), use_container_width=True)
            except Exception as e:
                st.error(f"Failed to complete Intake Split: {e}")

    else:
        st.info("Select a tool above to launch.")

st.caption(f"© 2025 Learner Connect Data Optimising Tool — Version {APP_VERSION}")

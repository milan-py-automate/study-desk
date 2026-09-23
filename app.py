import os
import json
import datetime
from flask import Flask, jsonify, request

import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = os.environ.get("SHEET_ID")
SHEET_NAME = "Materials"
HEADERS = ["Subject", "Chapter", "Material Type", "Material Name", "Link", "Progress", "Added On"]
MATERIAL_TYPES = {"PDF", "Video", "Audio", "Slide"}

_ws_cache = None


def get_worksheet():
    """Google Sheet ka connection banata hai (service account ke through)."""
    global _ws_cache
    if _ws_cache is not None:
        return _ws_cache

    creds_raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not creds_raw:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON env var set nahi hai")
    if not SHEET_ID:
        raise RuntimeError("SHEET_ID env var set nahi hai")

    creds_dict = json.loads(creds_raw)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    sh = client.open_by_key(SHEET_ID)

    try:
        ws = sh.worksheet(SHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=SHEET_NAME, rows=1000, cols=len(HEADERS))
        ws.append_row(HEADERS)

    _ws_cache = ws
    return ws


def build_tree(ws):
    """Sheet ki saari rows padhkar Subject -> Chapter -> Materials tree banata hai."""
    values = ws.get_all_values()
    rows = values[1:] if values else []

    subjects = []
    subject_index = {}

    for i, row in enumerate(rows):
        row_num = i + 2  # +1 header, +1 1-indexed
        row = row + [""] * (7 - len(row))
        subj_name, chap_name, mtype, mname, mlink, progress, added = row[:7]

        subj_name = subj_name.strip()
        if not subj_name:
            continue

        if subj_name not in subject_index:
            subj = {"name": subj_name, "row": row_num, "chapters": []}
            subject_index[subj_name] = subj
            subjects.append(subj)
        subj = subject_index[subj_name]

        chap_name = chap_name.strip()
        if not chap_name:
            continue

        chap = next((c for c in subj["chapters"] if c["name"] == chap_name), None)
        if chap is None:
            chap = {"name": chap_name, "row": row_num, "materials": []}
            subj["chapters"].append(chap)

        if mtype in MATERIAL_TYPES and (mname.strip() or mlink.strip()):
            chap["materials"].append({
                "row": row_num,
                "type": mtype,
                "name": mname.strip() or mlink.strip(),
                "link": mlink.strip(),
                "progress": progress.strip(),
                "added_on": added.strip(),
            })

    return subjects


@app.route("/")
def home():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "index.html"), encoding="utf-8") as f:
        return f.read()


@app.route("/api/data")
def api_data():
    try:
        ws = get_worksheet()
        return jsonify({"subjects": build_tree(ws)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/subject", methods=["POST"])
def add_subject():
    data = request.get_json(force=True) or {}
    name = (data.get("subject") or "").strip()
    if not name:
        return jsonify({"error": "subject naam chahiye"}), 400
    ws = get_worksheet()
    ws.append_row([name, "", "", "", "", "", ""])
    return jsonify({"ok": True})


@app.route("/api/subject", methods=["DELETE"])
def delete_subject():
    data = request.get_json(force=True) or {}
    name = (data.get("subject") or "").strip()
    ws = get_worksheet()
    values = ws.get_all_values()
    rows_to_delete = [i + 2 for i, row in enumerate(values[1:]) if row and row[0].strip() == name]
    for r in sorted(rows_to_delete, reverse=True):
        ws.delete_rows(r)
    return jsonify({"ok": True})


@app.route("/api/chapter", methods=["POST"])
def add_chapter():
    data = request.get_json(force=True) or {}
    subject = (data.get("subject") or "").strip()
    chapter = (data.get("chapter") or "").strip()
    if not subject or not chapter:
        return jsonify({"error": "subject aur chapter dono chahiye"}), 400
    ws = get_worksheet()
    ws.append_row([subject, chapter, "", "", "", "", ""])
    return jsonify({"ok": True})


@app.route("/api/chapter", methods=["DELETE"])
def delete_chapter():
    data = request.get_json(force=True) or {}
    subject = (data.get("subject") or "").strip()
    chapter = (data.get("chapter") or "").strip()
    ws = get_worksheet()
    values = ws.get_all_values()
    rows_to_delete = [
        i + 2 for i, row in enumerate(values[1:])
        if len(row) > 1 and row[0].strip() == subject and row[1].strip() == chapter
    ]
    for r in sorted(rows_to_delete, reverse=True):
        ws.delete_rows(r)
    return jsonify({"ok": True})


@app.route("/api/material", methods=["POST"])
def add_material():
    data = request.get_json(force=True) or {}
    subject = (data.get("subject") or "").strip()
    chapter = (data.get("chapter") or "").strip()
    mtype = (data.get("type") or "").strip()
    name = (data.get("name") or "").strip()
    link = (data.get("link") or "").strip()
    if not (subject and chapter and mtype and link):
        return jsonify({"error": "subject, chapter, type, link — sab chahiye"}), 400
    if mtype not in MATERIAL_TYPES:
        return jsonify({"error": "type PDF/Video/Audio/Slide me se ek hona chahiye"}), 400
    ws = get_worksheet()
    added = datetime.date.today().isoformat()
    ws.append_row([subject, chapter, mtype, name or link, link, "", added])
    return jsonify({"ok": True})


@app.route("/api/row/<int:row_num>", methods=["DELETE"])
def delete_row(row_num):
    ws = get_worksheet()
    ws.delete_rows(row_num)
    return jsonify({"ok": True})


@app.route("/api/progress/<int:row_num>", methods=["PUT"])
def update_progress(row_num):
    data = request.get_json(force=True) or {}
    progress = (data.get("progress") or "").strip()
    ws = get_worksheet()
    ws.update_cell(row_num, 6, progress)  # column F = Progress
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)

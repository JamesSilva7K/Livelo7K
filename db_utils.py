import json
import os
import sqlite3
import traceback

def get_supreme_ids(db):
    try:
        r_admin = db.execute("SELECT value FROM sys_config WHERE key='supreme_admin_id'").fetchone()
        r_group = db.execute("SELECT value FROM sys_config WHERE key='supreme_group_id'").fetchone()
        adm = r_admin['value'] if r_admin else os.environ.get("SUPREME_ADMIN_ID", "")
        grp = r_group['value'] if r_group else os.environ.get("SUPREME_GROUP_ID", adm)
        return adm, grp
    except Exception as e:
        print("Erro get supreme ids:", e)
        return "", ""

import csv, os, datetime as dt
DATA_DIR=os.path.join(os.path.dirname(__file__),"..","data")
os.makedirs(DATA_DIR,exist_ok=True)
def _path(name): return os.path.join(DATA_DIR,name)
def read_csv(name):
    path=_path(name)
    if not os.path.exists(path): return []
    with open(path,encoding="utf-8") as f: return list(csv.DictReader(f))
def write_csv(name,rows,fieldnames):
    with open(_path(name),"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fieldnames);w.writeheader();w.writerows(rows)
def append_order(name,qty,vendor,owner):
    rows=read_csv("orders.csv");oid=str(len(rows)+1)
    rows.append({"id":oid,"name":name,"qty":qty,"vendor":vendor,"owner":owner,"status":"新規"})
    write_csv("orders.csv",rows,["id","name","qty","vendor","owner","status"])
def set_order_status(oid,to):
    rows=read_csv("orders.csv")
    for r in rows:
        if r["id"]==str(oid): r["status"]=to
    write_csv("orders.csv",rows,["id","name","qty","vendor","owner","status"])
def seed_if_empty():
    if not read_csv("orders.csv"):
        write_csv("orders.csv",[{"id":"1","name":"Switch","qty":"2","vendor":"楽天","owner":"buyer01","status":"新規"}],["id","name","qty","vendor","owner","status"])
    if not read_csv("alerts.csv"):
        write_csv("alerts.csv",[{"kind":"為替","title":"USD/JPY 150","time":dt.datetime.now().isoformat()}],["kind","title","time"])

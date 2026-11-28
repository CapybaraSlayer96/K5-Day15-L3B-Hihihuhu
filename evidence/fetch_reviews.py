"""Tải review App Store (RSS chính thức của Apple). Chạy: python -I -X utf8 fetch_reviews.py"""
import requests, csv, datetime
APPS = {"Wanderlog":1476732439,"Tripomatic":519058033,"Tripsy":1429967544,"Rhyme":6748781672,"TripIt":311035142}
PER_APP = 200
rows=[]
for name,i in APPS.items():
    got=[]
    for page in range(1,6):
        u=f"https://itunes.apple.com/us/rss/customerreviews/page={page}/id={i}/sortby=mostrecent/json"
        try: d=requests.get(u,timeout=30).json()
        except Exception as e: print(name,page,"ERR",e); break
        ent=d.get("feed",{}).get("entry",[])
        if isinstance(ent,dict): ent=[ent]
        ent=[e for e in ent if "im:rating" in e]
        if not ent: break
        got+=ent
        if len(got)>=PER_APP: break
    for e in got[:PER_APP]:
        rows.append({"app":name,"updated":e["updated"]["label"][:10],"stars":e["im:rating"]["label"],
                     "title":e["title"]["label"].replace("\n"," "),"text":e["content"]["label"].replace("\n"," ")})
    print(name,len(got[:PER_APP]))
with open("reviews_raw.csv","w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["app","updated","stars","title","text"]); w.writeheader(); w.writerows(rows)
print("tổng",len(rows),"tải ngày",datetime.date.today())

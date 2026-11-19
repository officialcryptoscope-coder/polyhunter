"""Write JSON and Markdown reports."""
import json,os
from datetime import datetime,timezone
def save_report(report,out_dir="reports",stem="polyhunter"):
    os.makedirs(out_dir,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    addr=(report.get("address") or "local-source").lower().replace("0x","")[:12]
    base="{}-{}-{}".format(stem,addr,stamp); jp=os.path.join(out_dir,base+".json"); mp=os.path.join(out_dir,base+".md")
    with open(jp,"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
    lines=["# PolyHunter Security Research Report","","- Generated: {}".format(report.get("generated_at")),
      "- Module: {}".format(report.get("module")),"- Network: {}".format(report.get("network")),
      "- Address: {}".format(report.get("address") or "Local source"),
      "- Contract: {}".format(report.get("contract_name","Unknown")),"",
      "> Automated heuristic output only. Validate findings manually.","","## Metadata",""]
    for k,v in report.get("metadata",{}).items(): lines.append("- {}: {}".format(k,v))
    lines.extend(["","## Findings",""])
    for x in report.get("findings",[]):
        lines.extend(["### {} — {} ({})".format(x.get("id"),x.get("category"),x.get("severity")),
          x.get("message",""),"- Status: {}".format(x.get("status","needs_manual_review")),
          "- Occurrences: {}".format(x.get("occurrences",0))])
        for e in x.get("evidence",[]): lines.append("  - {}:{} — {}".format(e.get("file"),e.get("line"),e.get("snippet")))
        lines.append("")
    lines.extend(["## Limitations",""]+["- "+x for x in report.get("limitations",[])])
    with open(mp,"w",encoding="utf-8") as f: f.write("\n".join(lines))
    return jp,mp

import json, os
from datetime import datetime, timezone
def save_report(report, out_dir="reports"):
    os.makedirs(out_dir,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    addr=(report.get("address") or "local-source").lower().replace("0x","")[:12]
    base=f"polyhunter-{addr}-{stamp}"
    jp,mp=os.path.join(out_dir,base+".json"),os.path.join(out_dir,base+".md")
    with open(jp,"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
    lines=["# PolyHunter Security Research Report","",f"- Generated UTC: {report.get('generated_at')}",
      f"- Network: {report.get('network','Polygon PoS')}",f"- Address: {report.get('address') or 'Local source'}",
      f"- Contract: {report.get('contract_name','Unknown')}",""," > Automated heuristic output only. Validate findings manually; this is not an audit.","","## Metadata",""]
    for k,v in report.get("metadata",{}).items(): lines.append(f"- {k}: {v}")
    lines += ["","## Findings",""]
    for x in report.get("findings",[]):
        lines += [f"### {x['id']} — {x['category']} ({x['severity']})",x["message"],
          f"- Confidence: {x.get('confidence','low')}",f"- Status: {x.get('status','needs_manual_review')}",
          f"- Matching lines: {x.get('occurrences',0)}"]
        for ev in x.get("evidence",[]): lines.append(f"  - {ev['file']}:{ev['line']} — {ev['snippet']}")
        lines.append("")
    lines += ["## Manual follow-up","1. Inspect each evidence location in context.","2. Trace callers, modifiers, inherited contracts, and state transitions.","3. Validate proxy implementation and initialization.","4. Use authorized tests, fuzzing, and fork tests before making a security claim."]
    with open(mp,"w",encoding="utf-8") as f: f.write("\n".join(lines))
    return jp,mp

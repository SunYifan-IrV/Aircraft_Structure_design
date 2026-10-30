from pathlib import Path
import json,re,time,argparse
import win32com.client as w
root=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser();parser.add_argument('--run-dir');args=parser.parse_args()
run=Path(args.run_dir).resolve() if args.run_dir else sorted((root/'02_CATIA/generated').glob('validation_*'))[-1]
rows=json.loads((run/'results.json').read_text(encoding='utf-8'))
source=Path(rows[-1]['active_file']);step=source.with_suffix('.stp')
c=w.GetActiveObject('CATIA.Application');old=c.DisplayFileAlerts;c.DisplayFileAlerts=False
report={}
try:
 d=c.Documents.Item(source.name);d.Close();d=c.Documents.Open(str(source));d.Part.Update()
 report['saved_catpart_reopen_update']='PASS'
 report['catpart_bytes']=source.stat().st_size;report['step_bytes']=step.stat().st_size
 text=step.read_text(encoding='ascii',errors='replace')
 report['step_manifold_solid_brep_count']=len(re.findall(r'=\s*MANIFOLD_SOLID_BREP\s*\(',text))
 print(report,flush=True)
 c.Documents.Open(str(step))
 code = 'Function CheckStep()\nOn Error Resume Next\nDim d,p\nSet d=CATIA.ActiveDocument\nIf TypeName(d)<>"PartDocument" Or d.Name="' + source.name + '" Then\nCheckStep="PENDING"\nExit Function\nEnd If\nSet p=d.Part\np.Update\nIf Err.Number<>0 Then\nCheckStep="ERROR " & Err.Description\nElse\nCheckStep=d.Name & "|" & CStr(p.Bodies.Count)\nEnd If\nEnd Function'
 for attempt in range(60):
  check=str(c.SystemService.Evaluate(code,1,'CheckStep',[]))
  if check!='PENDING':break
  time.sleep(1)
 if '|' not in check:raise RuntimeError('STEP import did not finish: '+check)
 imported=c.ActiveDocument
 imported_name,count=check.rsplit('|',1)
 report['step_import_document']=imported_name
 report['step_import_bodies']=int(count)
 report['step_import_update']='PASS'
 print('IMPORTED',report,flush=True)
 if report['step_import_bodies'] != report['step_manifold_solid_brep_count']:raise RuntimeError('Imported solid count does not match STEP')
 report['step_import']='PASS'
 print(report,flush=True)
 imported.Close()
 for i in range(c.Documents.Count,0,-1):
  testdoc=c.Documents.Item(i)
  if testdoc.FullName.startswith(str(run)) or (testdoc.Name.startswith(source.stem+'_') and testdoc.FullName==testdoc.Name):testdoc.Close()
 d.Activate()
 (run/'export_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
finally:c.DisplayFileAlerts=old

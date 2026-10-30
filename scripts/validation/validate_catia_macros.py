"""Run the actual CATScript sources through CATIA's VBScript engine.
Only Notify's message box is replaced with text capture; modeling is unchanged.
Run in the desktop user's session so GetActiveObject reaches the visible CATIA.
"""
from pathlib import Path
import argparse,json,sys,datetime,shutil
import win32com.client as w
parser=argparse.ArgumentParser();parser.add_argument('--start',type=int,default=1);parser.add_argument('--end',type=int,default=6);parser.add_argument('--run-dir')
a=parser.parse_args()
root=Path(__file__).resolve().parents[3]
scripts=root/'02_CATIA'/'scripts'
run=Path(a.run_dir).resolve() if a.run_dir else root/'02_CATIA'/'generated'/('validation_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
run.mkdir(parents=True,exist_ok=True)
print('RUN_DIR',run,flush=True)
c=w.GetActiveObject('CATIA.Application');old_alerts=c.DisplayFileAlerts;c.DisplayFileAlerts=False
rows=json.loads((run/'results.json').read_text(encoding='utf-8'))[:a.start-1] if (run/'results.json').exists() and a.start>1 else []
try:
 if a.start>1:
  resume=run/('resume_'+datetime.datetime.now().strftime('%H%M%S')+'.CATPart')
  shutil.copy2(run/f'stage{a.start-1:02d}.CATPart',resume)
  c.Documents.Open(str(resume))
 for n in range(a.start,a.end+1):
  source=next(scripts.glob(f'{n:02d}_*.CATScript'))
  code=source.read_text(encoding='utf-8-sig').replace('    MsgBox message','    ValidationMessages = ValidationMessages & message & vbCrLf')
  if n==6:
   for marker in ['    For Each name In expected', '    For Each name In Array', '    Set gs =', '    part.Update', '    For Each b In part.Bodies', '    Dim selection', '    selection.VisProperties', '    Dim fs,', '    stem =', '    catFile =', '    doc.SaveAs', '    doc.ExportData', '    Notify']:
    code=code.replace(marker, '    ValidationStage = '+json.dumps(marker.strip())+'\n'+marker)
  code='Dim ValidationMessages, ValidationStage\n'+code+'''\nFunction ValidateEntry()
On Error Resume Next
CATMain
If Err.Number <> 0 Then
ValidateEntry = "ERROR | " & CStr(Err.Number) & " | " & Err.Source & " | " & Err.Description & " | stage: " & ValidationStage
Else
ValidateEntry = "SUCCESS | " & ValidationMessages
End If
End Function
'''
  print('START',source.name,flush=True)
  result=c.SystemService.Evaluate(code,1,'ValidateEntry',[])
  print('RESULT',result,flush=True)
  if not str(result).startswith('SUCCESS'):raise RuntimeError(result)
  d=c.ActiveDocument;p=d.Part;p.Update()
  bodies=[]
  for i in range(1,p.Bodies.Count+1):
   b=p.Bodies.Item(i)
   for j in range(1,b.Shapes.Count+1):
    feature=b.Shapes.Item(j)
    if not p.IsUpToDate(feature):raise RuntimeError('Not updated: '+feature.Name)
   bodies.append({'name':b.Name,'shapes':b.Shapes.Count,'sketches':b.Sketches.Count})
  row={'step':n,'source':source.name,'result':result,'bodies':bodies,'active_file':d.FullName}
  rows.append(row)
  if n<6:d.SaveAs(str(run/f'stage{n:02d}.CATPart'))
  (run/'results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
  print('PASS',n,'bodies',len(bodies),'features',sum(b['shapes'] for b in bodies),flush=True)
 (run/'failure.txt').unlink(missing_ok=True)
 print('ALL REQUESTED STEPS PASSED',flush=True)
except Exception as e:
 print('FAILED',repr(e),flush=True)
 try:
  p=c.ActiveDocument.Part
  print('INWORK',p.InWorkObject.Name,flush=True)
  print('BODIES',[(p.Bodies.Item(i).Name,p.Bodies.Item(i).Shapes.Count,p.Bodies.Item(i).Sketches.Count) for i in range(1,p.Bodies.Count+1)],flush=True)
 except Exception:pass
 (run/'failure.txt').write_text(repr(e),encoding='utf-8')
 sys.exit(1)
finally:c.DisplayFileAlerts=old_alerts

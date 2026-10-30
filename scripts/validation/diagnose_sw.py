import win32com.client as w
from pathlib import Path
sw=w.GetActiveObject('SldWorks.Application')
print('SW',sw.RevisionNumber,flush=True)
try:
 d=sw.ActiveDoc
 print('ACTIVE',d.GetTitle if d else None,flush=True)
except Exception as e:print('ACTIVE ERROR',repr(e),flush=True)
p=str(Path('02_CATIA/generated/Aircraft_Structure_20261030_113158.stp').resolve())
obj=sw.GetImportFileData(p)
print('IMPORT OBJECT',obj,flush=True)
if obj:
 ti=obj._oleobj_.GetTypeInfo();ta=ti.GetTypeAttr()
 print('TYPE',ti.GetDocumentation(-1),flush=True)
 for i in range(ta.cFuncs):
  fd=ti.GetFuncDesc(i)
  print('METHOD',ti.GetNames(fd.memid),fd,flush=True)
print('APP METHODS',flush=True)
ti=sw._oleobj_.GetTypeInfo();ta=ti.GetTypeAttr()
for i in range(ta.cFuncs):
 fd=ti.GetFuncDesc(i);names=ti.GetNames(fd.memid)
 if any(t in names[0] for t in ['LoadFile4','GetImportFileData','OpenDoc6','UserPreferenceToggle']):print(names,fd,flush=True)


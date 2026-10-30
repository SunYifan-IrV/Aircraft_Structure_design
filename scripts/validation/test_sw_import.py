from pathlib import Path
import pythoncom,win32com.client as w,json,time,shutil
sw=w.GetActiveObject('SldWorks.Application')
folder=Path('02_CATIA/generated/SW_compat').resolve();folder.mkdir(exist_ok=True)
source=Path('02_CATIA/generated/Aircraft_Structure_20261030_113158.stp').resolve()
p=folder/'Aircraft_Structure_test.stp';shutil.copy2(source,p)
print('REVISION',sw.RevisionNumber,flush=True)
print('3DINTERCONNECT',sw.GetUserPreferenceToggle(691),flush=True)
data=sw.GetImportFileData(str(p));err=w.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_I4,0)
print('LOAD START',p,flush=True)
doc=sw.LoadFile4(str(p),'',data,err)
print('LOAD RESULT',doc,'error',err.value,flush=True)
if doc:
 print('TITLE',doc.GetTitle,'TYPE',doc.GetType,flush=True)
 try: print('BODIES',len(doc.GetBodies2(0,False) or []),flush=True)
 except Exception as e:print('BODYERR',repr(e),flush=True)

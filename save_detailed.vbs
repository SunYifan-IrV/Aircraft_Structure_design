On Error Resume Next
Set c=GetObject(, "CATIA.Application")
Set d=c.Documents.Item("Part4.CATPart")
If Err.Number<>0 Then WScript.Echo "Document missing: " & Err.Description: WScript.Quit 1
Err.Clear
d.SaveAs "D:\Document\University\Personal_aircraft\02_CATIA\PersonalAircraft_WingStructure_RevA.CATPart"
If Err.Number<>0 Then WScript.Echo "Save error: " & Err.Description: WScript.Quit 2
WScript.Echo "Saved document with " & d.Part.Bodies.Count & " bodies"

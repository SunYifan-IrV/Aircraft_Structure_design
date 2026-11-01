"""Inspect the STEP: volume bounding boxes, surface areas (mm^2), OML candidates."""
import gmsh, csv, os, sys

STEP = r"C:\Users\张文博\Desktop\Copy_of_PersonalAircraft_Structural_RevN.stp"
OUT = r"C:\Users\张文博\Documents\deepseek-harness\default-workspace\fea_aero\results"

gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 0)
gmsh.merge(STEP)
gmsh.model.occ.synchronize()

vols = gmsh.model.getEntities(3)
rows = []
for dim, tag in vols:
    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)
    area = gmsh.model.occ.getMass(2, tag) if False else 0.0
    # sum face areas
    faces = gmsh.model.getBoundary([(dim, tag)], oriented=False)
    a = 0.0
    for fd, ft in faces:
        a += gmsh.model.occ.getMass(2, ft)
    rows.append(dict(tag=tag, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                     zmin=zmin, zmax=zmax, dy=ymax - ymin, dx=xmax - xmin,
                     dz=zmax - zmin, area_mm2=a, nfaces=len(faces)))

rows.sort(key=lambda r: -r["area_mm2"])
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "volumes.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print("volumes:", len(rows))
for r in rows[:15]:
    print(f"tag={r['tag']:4d} area={r['area_mm2']:12.0f} x=[{r['xmin']:7.1f},{r['xmax']:7.1f}] "
          f"y=[{r['ymin']:7.1f},{r['ymax']:7.1f}] z=[{r['zmin']:6.1f},{r['zmax']:6.1f}]")
gmsh.finalize()

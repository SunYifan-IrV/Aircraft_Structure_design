"""Generate a surface mesh of the CATIA STEP (RevN) for CFD / visualisation.

Outputs:
  mesh/aircraft_surface.stl   (binary STL, mm)
  mesh/aircraft_surface.msh   (gmsh v2.2, mm)
"""
import gmsh, os, time, sys

STEP = r"C:\Users\张文博\Desktop\Copy_of_PersonalAircraft_Structural_RevN.stp"
ROOT = r"C:\Users\张文博\Documents\deepseek-harness\default-workspace\fea_aero"
MESH = os.path.join(ROOT, "mesh")
os.makedirs(MESH, exist_ok=True)

LMAX = float(sys.argv[1]) if len(sys.argv) > 1 else 25.0
LMIN = LMAX / 5.0

t0 = time.time()
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
gmsh.option.setNumber("General.NumThreads", 0)
gmsh.merge(STEP)
gmsh.model.occ.synchronize()
print(f"[{time.time()-t0:.1f}s] imported: {len(gmsh.model.getEntities(3))} volumes")

gmsh.option.setNumber("Mesh.CharacteristicLengthMax", LMAX)
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", LMIN)
gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 1)
gmsh.option.setNumber("Mesh.Algorithm", 1)
gmsh.option.setNumber("Mesh.Smoothing", 3)

print(f"[{time.time()-t0:.1f}s] meshing surfaces (h={LMAX} mm) ...")
gmsh.model.mesh.generate(2)
print(f"[{time.time()-t0:.1f}s] 2D mesh done")

nt = len(gmsh.model.mesh.getElements(2)[1][0]) if gmsh.model.mesh.getElements(2)[1] else 0
nn = len(gmsh.model.mesh.getNodes()[0])
print("nodes:", nn, " triangles(approx):", nt)

gmsh.write(os.path.join(MESH, "aircraft_surface.stl"))
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
gmsh.write(os.path.join(MESH, "aircraft_surface.msh"))
print(f"[{time.time()-t0:.1f}s] written")
gmsh.finalize()

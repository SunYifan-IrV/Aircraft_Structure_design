"""Mesh the complete RevP STEP and export binary STL + msh."""
import gmsh, os, time

STEP = r"C:\Users\张文博\Desktop\PersonalAircraft_Structural_RevP.stp"
ROOT = r"C:\Users\张文博\Documents\deepseek-harness\default-workspace\fea_aero"
MESH = os.path.join(ROOT, "mesh")
os.makedirs(MESH, exist_ok=True)

t0 = time.time()
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 0)
gmsh.merge(STEP)
gmsh.model.occ.synchronize()
print("volumes", len(gmsh.model.getEntities(3)), f"{time.time()-t0:.1f}s")

gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 18)
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 3.6)
gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
gmsh.option.setNumber("Mesh.Algorithm", 1)
gmsh.option.setNumber("Mesh.Smoothing", 3)
gmsh.model.mesh.generate(2)
nn = len(gmsh.model.mesh.getNodes()[0])
_types, _tags, _nodes = gmsh.model.mesh.getElements(2)
ntri = sum(len(t) for t in _tags)
print("nodes", nn, "tri", ntri, f"{time.time()-t0:.1f}s")

gmsh.option.setNumber("Mesh.Binary", 1)
gmsh.option.setNumber("Mesh.StlOneSolidPerSurface", 0)
gmsh.write(os.path.join(MESH, "revP_surface.stl"))
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
gmsh.write(os.path.join(MESH, "revP_surface.msh"))
print("written", f"{time.time()-t0:.1f}s")
gmsh.finalize()


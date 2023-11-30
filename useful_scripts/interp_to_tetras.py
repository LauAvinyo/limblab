from vedo import *
from vedo.pyplot import plot, histogram

# Load a mesh of a mouse limb at 12 days of development
tmsh = TetMesh(dataurl + "limb.vtu")

msh = tmsh.tomesh(fill=0) # convert to a Mesh object

# Pick 100 points where we measure the value of a gene expression
ids = np.random.randint(0, msh.npoints, 100)
pts = msh.vertices[ids]        # slice the numpy array
x = pts[:, 0]                  # x coordinates of the points
gene = np.sin((x+150)/500)**2  # we are making this up!

# Create a set of points with those values
points = Points(pts, r=10).cmap("Greens", gene)

# Interpolate the gene data onto the mesh, by averaging the 5 closest points
tmsh.interpolate_data_from(points, n=5).cmap("Greens").add_scalarbar()
tet_values = tmsh.pointdata["Scalars"]
print(tet_values)
# tmsh.write("limb.vtu")

# Create a graph of the gene expression as function of x-position
gene_plot = plot(x, gene, lw=0, title="Gene expression").clone2d(scale=0.5)
gene_histo = histogram(tet_values, bins=20, c="Greens", title="Gene expression")
gene_histo = gene_histo.clone2d("top-left", scale=0.5)

# Show the mesh, the points and the graphs
show(tmsh, points, gene_plot, gene_histo, axes=14, bg2='lb').close()

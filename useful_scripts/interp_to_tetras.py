from vedo import *
from vedo.pyplot import plot, histogram

# Load a mesh of a mouse limb at 12 days of development
tmsh = TetMesh(dataurl + "limb.vtu")

# Pick 100 points where we measure the value of a gene expression
ids = np.random.randint(0, tmsh.npoints, 100)
pts = tmsh.vertices[ids]  # slice the numpy array
x = pts[:, 0]  # x coordinates of the points
gene = np.sin((x + 150) / 500) ** 2  # we are making this up!

# Create a set of points with those values
points = Points(pts, r=12).cmap("Greens", gene)

# Interpolate the gene data onto the mesh, by averaging the 4 closest points
tmsh.interpolate_data_from(points, n=4)
tmsh.cmap("Greens").alpha(0.5).add_scalarbar3d("Gene expression")
tet_values = tmsh.pointdata["Scalars"]
print(tmsh)
print(tet_values)
# tmsh.write("limb.vtu")

# make a fancier scalarbar
tmsh.scalarbar = tmsh.scalarbar.clone2d("center-right", 0.15)

# Create a graph of the gene expression as function of x-position
gene_plot = plot(x, gene, lw=0, title="Gene expression")
gene_plot = gene_plot.clone2d("bottom-left", 0.5)

# Create a histogram of the gene expression
gene_histo = histogram(tet_values, bins=20, c="Greens", title="Gene expression")
gene_histo = gene_histo.clone2d("top-left", 0.5)

# Show the mesh, the points and the graphs
m = tmsh.tomesh().wireframe().color("k7", 0.01).lighting("off")  # for viz only
show(tmsh, m, points, gene_plot, gene_histo, axes=14, bg2="lb").close()

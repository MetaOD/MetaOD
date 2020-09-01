from imagecluster import calc as ic
from imagecluster import postproc as pp
import sys

# Create image database in memory. This helps to feed images to the NN model
# quickly.
ias = ic.image_arrays(sys.argv[1], size=(224,224))

model = ic.get_model()

fps = ic.fingerprints(ias, model)

# Optionally run a PCA on the fingerprints to compress the dimensions. Use a
# cumulative explained variance ratio of 0.95.
fps = ic.pca(fps, n_components=0.95)

# Run clustering on the fingerprints.  Select clusters with similarity index
# sim=0.5
clusters = ic.cluster(fps, sim=0.7)

# Create dirs with links to images. Dirs represent the clusters the images
# belong to.
pp.make_links(clusters, sys.argv[1] + '/clusters')

# Plot images arranged in clusters.
# pp.visualize(clusters, ias)

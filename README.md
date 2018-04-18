### slug_cluster

Scripts for running SLUG2 simulations and calculating time evolution of light-to-mass conversion factors of coeval populations of star clusters.

* Step 1: Clone slug2 from [bitbucket repository](https://bitbucket.org/krumholz/slug2/) and compile. Minimum requirements are BOOST C++ and GSL libraries. Set SLUG_DIR environment variable to the slug installation directory.

* Step 2: Set input parameters such as mass bins, number of trials, number of processors/threads, and generate param files. **gen_cluster_param.py**

* Step 3: Set input parameters accordingly and run simulations. **run_slug_cluster.sh**

* Step 4: Integrate output spectra and save median values of luminosity, ionizing photon output rate, mean energy of photons at different frequency bins. The "slugpy" should be in the python module search path. **slug_cluster.py**

* Step 4: Plot some results. **plt_evol.py**

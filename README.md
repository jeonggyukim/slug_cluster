Simple scripts for running SLUG2 simulations to obtain time evolution of light-to-mass conversion factors of coeval populations of star clusters.

* You first need to clone slug2 from [bitbucket repository](https://bitbucket.org/krumholz/slug2/) and compile. Minimum requirements are BOOST C++ and GSL libraries. Need to set SLUG_DIR environment variable.

* "gen_cluster_param.py": Set input parameters such as mass bins, number of trials, number of processors/threads, and generate param files.

* "run_slug_cluster.sh": Set input parameters accordingly and run simulations.

* "slug_cluster.py": Integrate output spectra and save median values of luminosity, ionizing photon output rate, mean energy of photons at different frequency bins. The "slugpy" should be in the python module search path.

* "plt_evol.py": Plot some results.

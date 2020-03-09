# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class KokkosKernels(CMakePackage,CudaPackage):
    """Kokkos Kernels provides math kernels, often BLAS or LAPACK
    for small matrices, that can be used in larger Kokkos parallel routines"""

    homepage = "https://github.com/kokkos/kokkos-kernels"
    git      = "https://github.com/kokkos/kokkos-kernels.git"

    version('3.0',     url='https://github.com/kokkos/kokkos-kernels/archive/3.0.00.tar.gz',
            sha256="e4b832aed3f8e785de24298f312af71217a26067aea2de51531e8c1e597ef0e6")
    version('develop', branch='develop')
    version('master',  branch='master')

    variant("diy", default=False, description="Add necessary flags for Spack DIY mode")

    depends_on("kokkos")
    depends_on("kokkos@develop", when="@develop")

    etis = {
      "double"                : (True,   "ETI doubles"),
      "float"                 : (False,  "ETI float"),
      "complex_double"        : (False,  "ETI complex double precision"),
      "complex_float"         : (False,  "ETI complex single precision"),
      "execspace_cuda"        : ('auto', ""),
      "memspace_cudauvmspace" : ('auto', ""),
      "memspace_cudaspace"    : ('auto', ""),
      "memspace_hostspace"    : (True,   ""),
      "execspace_openmp"      : ('auto', ""),
      "execspace_threads"     : ('auto', ""),
      "execspace_serial"      : ('auto', ""),
      "layoutleft"            : (True,   ""),
      "layoutright"           : (False,  ""),
      "ordinal_int"           : (True,   ""),
      "ordinal_int64_t"       : (False,  ""),
      "offset_int"            : (True,   ""),
      "offset_size_t"         : (True,   ""),
    }
    for eti in etis:
      deflt, descr = etis[eti]
      variant(eti, default=deflt, description=descr)

    tpls = {
      "blas"      : (False, "Link to system BLAS"),
      "mkl"       : (False, "Link to system MKL"),
      "cublas"    : (False, "Link to CUDA BLAS library"),
      "cusparse"  : (False, "Link to CUDA sparse library"),
    }
    for tpl in tpls:
      deflt, descr = tpls[tpl]
      variant(tpl, default=deflt, description=descr)

    def cmake_args(self):
      spec = self.spec
      options = []

      isDiy = "+diy" in spec
      if isDiy:
        options.append("-DSpack_WORKAROUND=On")

      options.append("-DKokkos_ROOT=%s" % spec["kokkos"].prefix)
      # Compiler weirdness due to nvcc_wrapper
      options.append("-DCMAKE_CXX_COMPILER=%s" % spec["kokkos"].kokkos_cxx)

      if self.run_tests:
        options.append("-DKokkosKernels_ENABLE_TESTS=ON")

      for tpl in self.tpls:
        onFlag = "+%s" % tpl
        offFlag = "~%s" % tpl
        if onFlag in self.spec:
          options.append("-DKokkosKernels_ENABLE_TPL_%s=ON" % tpl.upper())
        elif offFlag in self.spec:
          options.append("-DKokkosKernels_ENABLE_TPL_%s=OFF" % tpl.upper())
        
      for eti in self.etis:
        deflt, descr = self.etis[eti]
        if deflt == "auto":
          value = spec.variants[eti].value
          if str(value) == "True": #spack does these as strings, not reg booleans
            options.append("-DKokkosKernels_INST_%s=ON" % eti.upper())
          elif str(value) == "False":
            options.append("-DKokkosKernels_INST_%s=OFF" % eti.upper())
          else:
            pass #don't pass anything, let CMake decide
        else: #simple option
          onFlag = "+%s" % eti
          offFlag = "~%s" % eti
          if onFlag in self.spec:
            options.append("-DKokkosKernels_INST_%s=ON" % eti.upper())
          elif offFlag in self.spec:
            options.append("-DKokkosKernels_INST_%s=OFF" % eti.upper())

      return options


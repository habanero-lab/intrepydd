
#include <cblas.h>
#include <cmath>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

namespace pydd {

//#define N_OBS 10000
#define N_OBS 2
#define N_VAR 10


  namespace internal {
    void naive_dsyrk(const double *inputA, double *outputAA)
    {
      int i, j, k;
      double temp;

      for (j=0; j<N_VAR; j++) {
        for (k=j; k<N_VAR; k++) {
          temp = 0.0;
          for (i=0; i<N_OBS; i++) {
            temp += inputA[i*N_VAR+k] * inputA[i*N_VAR+j];
          }
          outputAA[j*N_VAR+k] = temp;
        }
      }
    }
    void wrapper_dsyrk(const double *A, double *AA, const CBLAS_ORDER Layout=CblasRowMajor, const CBLAS_UPLO uplo=CblasUpper, 
        const CBLAS_TRANSPOSE trans=CblasTrans, const int n=N_VAR, const int k=N_OBS , 
        const double alpha=1.0, const int lda=N_VAR, const double beta=0.0, const int ldc=N_VAR )
    {
      //Performs a symmetric rank-k update.
      //void cblas_dsyrk (const CBLAS_ORDER Layout, const CBLAS_UPLO uplo, const CBLAS_TRANSPOSE trans, const int n, const int k, const double alpha, const double *a, const int lda, const double beta, double *c, const int ldc);
      //C := alpha*A*A' + beta*C,


      if ( Layout == CblasRowMajor && uplo == CblasUpper 
          && trans==CblasTrans) {
        naive_dsyrk(A,AA);
      } else {
        //cblas_dsyrk (const CBLAS_ORDER layout, const CBLAS_UPLO Uplo, const CBLAS_TRANSPOSE Trans, const int N, const int K, const double alpha, const double *A, const int lda, const double beta, double *C, const int ldc)

        cblas_dsyrk(Layout, uplo, trans, n, k, alpha, A, lda, beta, AA, ldc);
      }

      //cblas_dsyrk(CblasRowMajor, CblasUpper, CblasTrans, N_VAR, N_OBS, 1.0,	A, N_VAR, 0., AA, N_VAR);
    }
  }
  template <typename T>
	py::array_t<double> dsyrk(py::array_t<T> &inputA,  const int n=N_VAR, const int k=N_OBS ,const CBLAS_ORDER Layout=CblasRowMajor, const CBLAS_UPLO uplo=CblasUpper, 
        const CBLAS_TRANSPOSE trans=CblasTrans,  
			const double alpha=1.0, const int lda=N_VAR, const double beta=0.0, const int ldc=N_VAR )
	{
    const double *A = inputA.data();
    py::array_t<double> outputAA;
    double *AA = outputAA.mutable_data();
    internal::wrapper_dsyrk(A, AA, Layout, uplo, trans, n, k,  alpha, lda, beta, ldc);
    return outputAA;
	}

}



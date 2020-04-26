#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=method-hidden,C0103,E265,E303,R0914,W0621,E305

"""Module describing the weighted non-linear optimization scheme used to
determine the wavelength sensitivity of the spectrometer using a  polynomial
as a model function"""

import os
import sys
import math
import logging
from datetime import datetime
import numpy as np

import scipy.optimize as opt
import matplotlib.pyplot as plt
from common import compute_series_para

from common import utils
# ------------------------------------------------------

# Set logging ------------------------------------------
fileh = logging.FileHandler('./run_parallel/logfile_para.txt', 'w+')
formatter = logging.Formatter('%(message)s')
fileh.setFormatter(formatter)

log = logging.getLogger()  # root logger
for hdlr in log.handlers[:]:  # remove all old handlers
    log.removeHandler(hdlr)
log.addHandler(fileh)      # set the new handler
# ------------------------------------------------------

# Logging starts here
logger = logging.getLogger(os.path.basename(__file__))
log.info(logger)
logging.getLogger().setLevel(logging.INFO)
log.warning(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
log.warning('\n',)
log.error("------------ Run log ------------\n")
# ------------------------------------------------------

# LOAD EXPERIMENTAL BAND AREA DATA

#  | band area | error |
# without header in the following files

# Change following paths
dataH2 = np.loadtxt("./run_parallel/BA_H2_1.txt")
dataHD = np.loadtxt("./run_parallel/BA_HD_1.txt")
dataD2 = np.loadtxt("./run_parallel/BA_D2_1.txt")
xaxis = np.loadtxt("./run_parallel/Ramanshift_axis_para.txt")
# ------------------------------------------------------
# PARALLEL POLARIZATION

# set indices for OJ,QJ and SJ for H2, HD and D2
# these are required for computing spectra for given T

OJ_H2 = 3
QJ_H2 = 4

OJ_HD = 3
QJ_HD = 3
SJ_HD = 2

OJ_D2 = 4
QJ_D2 = 6
SJ_D2 = 3
# ------------------------------------------------------
print('Dimension of input data')
print('\t', dataH2.shape)
print('\t', dataHD.shape)
print('\t', dataD2.shape)
# ------------------------------------------------------
# SET  INIT COEFS

param_linear = np.zeros((2))
param_linear[0] = 298
param_linear[1] = -1.045

# ----------------------------
param_quadratic = np.zeros((3))
param_quadratic[0] = 298
param_quadratic[1] = -0.931
param_quadratic[2] = -0.242

# ----------------------------
param_cubic = np.zeros((4))
param_cubic[0] = 298
param_cubic[1] = -0.9340
param_cubic[2] = -0.2140
param_cubic[3] = -0.00100

# ----------------------------

param_quartic = np.zeros((5))
param_quartic[0] = 298
param_quartic[1] = -0.9340
param_quartic[2] = -0.2140
param_quartic[3] = -0.00100
param_quartic[4] = -0.000001

# ----------------------------

param_quintuple = np.zeros((6))
param_quintuple[0] = 298
param_quintuple[1] = -0.9340
param_quintuple[2] = -0.2140
param_quintuple[3] = -0.00100
param_quintuple[4] = -0.000001
param_quintuple[5] = -0.000001


# initial run will be with above parameters
# ------------------------------------------------

# ------------------------------------------------------
#      RUN PARAMETERS (CHANGE THESE BEFORE RUNNING
#                   FINAL OPTIMIZATION
# ------------------------------------------------------

# AVAILABLE FUNCTIONS TO USER :

# run_all_fit()
#    Runs the fitting up to quartic polynomial
#    Returns : np array of residuals, with 4 elements


# plot_curves(residual_array="None")
#   Plotting the curves (from fit)
#   and plot the residuals over the number of unknown variables
#   np array of residuals to be passed for plot of residuals

# Example :
#    resd = run_all_fit()
#    plot_curves(resd)
#
#    resd = run_all_fit() ; plot_curves(resd) ;
#
# ------------------------------------------------------
def run_all_fit():
    '''
    Runs the fitting up to quartic polynomial
    Returns : np array of residuals, with 4 elements
    '''
    resd_1 = 0
    resd_2 = 0
    resd_3 = 0
    resd_4 = 0
    resd_5 = 0

    run_fit_linear(299, 1.04586)
    resd_1 = run_fit_linear(299, -1.04586)

    resd_2 = run_fit_quadratic(299, -0.285, 0.052)
    resd_2 = run_fit_quadratic(299, 0.835, -0.052)

    run_fit_cubic(299, -1.036, -0.2192, 0.0025)
    resd_3 = run_fit_cubic(299, -0.559, -0.215, +0.00215)

    resd_4 = run_fit_quartic(299, -0.5566, -0.158, 0.05, +0.0012)
    resd_5 = run_fit_quintuple(296, -0.5566, -0.158, 0.05, +0.0012, +0.0001)

    out = np.array([resd_1, resd_2, resd_3, resd_4, resd_5])
    return out

# *******************************************************************

# ------------------------------------------------------
# ------------------------------------------------------
#                COMMON SETTINGS
# ------------------------------------------------------

# Constants ------------------------------
# these are used for scaling the coefs


scale1 = 1e3
scale2 = 1e6
scale3 = 1e9
scale4 = 1e12
scale5 = 1e14
# ----------------------------------------
scenter = 3316.3  # center of the spectra
# used to scale the xaxis

# ------------------------------------------------
#                COMMON FUNCTIONS
# ------------------------------------------------


def gen_intensity_mat(arr, index):
    """To obtain the intensity matrix for the numerator or denominator\
        in the Intensity ratio matrix

        array  =  2D array of data where index column contains the intensity
                  data
        index  =  corresponding to the column which has intensity data

        returns => square matrix of intensity ratio : { I(v1)/I(v2) } """

    spec1D = arr[:, index]
    spec_mat = np.zeros((spec1D.shape[0], spec1D.shape[0]))

    for i in range(spec1D.shape[0]):
        spec_mat[:, i] = spec1D / spec1D[i]

    return spec_mat

# ------------------------------------------------


def clean_mat(square_array):
    """Set the upper triangular portion of square matrix to zero
        including the diagonal
        input = any square array     """
    np.fill_diagonal(square_array, 0)
    return np.tril(square_array, k=0)

# ------------------------------------------------


def gen_weight(expt_data):
    """To generate the weight matrix from the experimental data 2D array
        expt_data  =  2D array of expt data where
                      0 index column is the band area
                      and
                      1 index column is the error
    """
    error_mat = np.zeros((expt_data.shape[0], expt_data.shape[0]))

    for i in range(expt_data.shape[0]):
        for j in range(expt_data.shape[0]):
            error_mat[i, j] = (expt_data[i, 0] / expt_data[j, 0]) \
                * math.sqrt((expt_data[i, 1] / expt_data[i, 0])**2
                            + (expt_data[j, 1] / expt_data[j, 0])**2)
    # return factor * inverse_square(error_mat)
    return error_mat

# ------------------------------------------------


def inverse_square(array):
    """return the inverse square of array, for all elements"""
    return 1 / (array**2)

# ------------------------------------------------


def scale_elements(array, index_array, factor):
    """scale the elements of array using the index_array and factor"""

    array[index_array] = array[index_array] * factor
    return array

# ------------------------------------------------


def gen_s_linear(computed_data, param):
    """Generate the sensitivity matrix assuming the wavelength
    dependent sensitivity as a line. Elements are the ratio of
    sensitivity at two wavenumber/wavelength points"""

    mat = np.zeros((computed_data.shape[0], computed_data.shape[0]))

    for i in range(computed_data.shape[0]):
        for j in range(computed_data.shape[0]):
            v1 = computed_data[i, 1] - scenter
            v2 = computed_data[j, 1] - scenter

            # param[0] = temperature
            # param[1] = c1

            mat[i, j] = (1 + (param[1] / scale1) * v1) / \
                (1 + (param[1] / scale1) * v2)

    return mat

# ------------------------------------------------


def gen_s_quadratic(computed_data, param):
    """Generate the sensitivity matrix assuming the wavelength
    dependent sensitivity as a quadratic polynomial. Elements are
    the ratio of sensitivity at two wavenumber/wavelength points"""

    mat = np.zeros((computed_data.shape[0], computed_data.shape[0]))

    for i in range(computed_data.shape[0]):
        for j in range(computed_data.shape[0]):
            v1 = computed_data[i, 1] - scenter
            v2 = computed_data[j, 1] - scenter

            # param[0] = temperature
            # param[1] = c1
            # param[2] = c2

            mat[i, j] = (1 + (param[1] / scale1) * v1 + (param[2]
                                                         / scale2) * v1**2)\
                / (1 + (param[1] / scale1) * v2 + (param[2] / scale2) * v2**2)

    return mat

# ------------------------------------------------


def gen_s_cubic(computed_data, param):
    """Generate the sensitivity matrix assuming the wavelength
    dependent sensitivity as a cubic polynomial. Elements are
    the ratio of sensitivity at two wavenumber/wavelength points"""

    mat = np.zeros((computed_data.shape[0], computed_data.shape[0]))
    # print('norm')
    for i in range(computed_data.shape[0]):
        for j in range(computed_data.shape[0]):
            v1 = computed_data[i, 1] - scenter
            v2 = computed_data[j, 1] - scenter

            # param[0] = temperature
            # param[1] = c1
            # param[2] = c2
            # param[3] = c3

            mat[i, j] = (1 + (param[1] / scale1) * v1 + (param[2] / scale2)
                         * v1**2 + (param[3] / scale3) * v1**3) \
                / (1 + (param[1] / scale1) * v2 + (param[2] / scale2) * v2**2
                   + (param[3] / scale3) * v2**3)

    return mat

# ------------------------------------------------


def gen_s_quartic(computed_data, param):
    """Generate the sensitivity matrix assuming the wavelength
    dependent sensitivity as quartic polynomial. Elements are
    the ratio of sensitivity at two wavenumber/wavelength points"""

    mat = np.zeros((computed_data.shape[0], computed_data.shape[0]))

    for i in range(computed_data.shape[0]):
        for j in range(computed_data.shape[0]):
            v1 = computed_data[i, 1] - scenter
            v2 = computed_data[j, 1] - scenter

            # param[0] = temperature
            # param[1] = c1
            # param[2] = c2
            # param[3] = c3
            # param[4] = c4

            mat[i, j] = (1+(param[1]/scale1)*v1 + (param[2]/scale2)*v1**2 +\
                       (param[3]/scale3)*v1**3 + (param[4]/scale4)*v1**4)/ \
                (1+(param[1]/scale1)*v2 + (param[2]/scale2)*v2**2 \
                 + (param[3]/scale3)*v2**3 + (param[4]/scale4)*v2**4)

    return mat
# ------------------------------------------------


def gen_s_quintuple(computed_data, param):
    """Generate the sensitivity matrix assuming the wavelength
    dependent sensitivity as quartic polynomial. Elements are
    the ratio of sensitivity at two wavenumber/wavelength points"""

    mat = np.zeros((computed_data.shape[0], computed_data.shape[0]))

    for i in range(computed_data.shape[0]):
        for j in range(computed_data.shape[0]):
            v1 = computed_data[i, 1] - scenter
            v2 = computed_data[j, 1] - scenter

            # param[0] = temperature
            # param[1] = c1
            # param[2] = c2
            # param[3] = c3
            # param[4] = c4

            mat[i, j] = (1+(param[1]/scale1)*v1 + (param[2]/scale2)*v1**2 +\
                       (param[3]/scale3)*v1**3 + (param[4]/scale4)*v1**4 
                       +  (param[5]/scale5)*v1**5 )/ \
                (1+(param[1]/scale1)*v2 + (param[2]/scale2)*v2**2 \
                 + (param[3]/scale3)*v2**3 + (param[4]/scale4)*v2**4 
                 + (param[5]/scale5)*v2**5 )

    return mat

# ------------------------------------------------

# ------------------------------------------------    

def T_independent_index():
    '''
    Getting indices for the t-independent terms in the matrix
    for all three gases, index output are for the terms which do not
    change with temperature
    '''

    TK = 298  #  --------------------------------
    sosD2 = compute_series_para.sumofstate_D2(TK)
    sosHD = compute_series_para.sumofstate_HD(TK)
    sosH2 = compute_series_para.sumofstate_H2(TK)

    computed_D2 = compute_series_para.spectra_D2( TK, OJ_D2, QJ_D2, 
                                                 SJ_D2, sosD2)
    computed_HD = compute_series_para.spectra_HD( TK, OJ_HD, QJ_HD, 
                                                 SJ_HD, sosHD)
    computed_H2 = compute_series_para.spectra_H2_c(TK, OJ_H2,
                                                   QJ_H2, sosH2 )    

    calc_298_D2 = gen_intensity_mat(computed_D2, 2)
    calc_298_HD = gen_intensity_mat(computed_HD, 2)
    calc_298_H2 = gen_intensity_mat(computed_H2, 2)

    TK = 1000  #  -------------------------------
    sosD2 = compute_series_para.sumofstate_D2(TK)
    sosHD = compute_series_para.sumofstate_HD(TK)
    sosH2 = compute_series_para.sumofstate_H2(TK)

    computed_D2 = compute_series_para.spectra_D2( TK, OJ_D2, QJ_D2, 
                                                 SJ_D2, sosD2)
    computed_HD = compute_series_para.spectra_HD( TK, OJ_HD, QJ_HD, 
                                                 SJ_HD, sosHD)
    computed_H2 = compute_series_para.spectra_H2_c(TK, OJ_H2,
                                                   QJ_H2, sosH2 )      

    calc_600_D2 = gen_intensity_mat (computed_D2, 2)
    calc_600_HD = gen_intensity_mat (computed_HD, 2)
    calc_600_H2 = gen_intensity_mat(computed_H2, 2) 
    
    # -------------------------------------------

    diff_D2 = calc_298_D2 - calc_600_D2
    diff_HD = calc_298_HD - calc_600_HD
    diff_H2 = calc_298_H2 - calc_600_H2

    cr_D2 = clean_mat(diff_D2)
    cr_HD = clean_mat(diff_HD)
    cr_H2 = clean_mat(diff_H2)
    
    # terms which are t-independet are selected here
    index_D2 = np.nonzero(np.abs(cr_D2) < 1e-10) 
    index_HD = np.nonzero(np.abs(cr_HD) < 1e-10) 
    index_H2 = np.nonzero(np.abs(cr_H2) < 1e-10)     
    
    # index for t-independent terms
    return index_D2, index_HD , index_H2

# ------------------------------------------------       
# ------------------------------------------------
# *******************************************************************
#     RESIDUAL FUNCTIONS DEFINED BELOW
# *******************************************************************


def residual_linear(param):
    '''Function which computes the residual (as sum of squares) comparing the
    ratio of expt to theoretical intensity ratio to the sensitivity  profile
    modelled as  a line, ( 1+ c1*x )

    param : T, c1

    '''

    TK = param[0]

    sosD2 = compute_series_para.sumofstate_D2(TK)
    sosHD = compute_series_para.sumofstate_HD(TK)
    sosH2 = compute_series_para.sumofstate_H2(TK)

    computed_D2 = compute_series_para.spectra_D2(TK, OJ_D2, QJ_D2,
                                                 SJ_D2, sosD2)
    computed_HD = compute_series_para.spectra_HD(TK, OJ_HD, QJ_HD,
                                                 SJ_HD, sosHD)
    computed_H2 = compute_series_para.spectra_H2_c(TK, OJ_H2,
                                                   QJ_H2, sosH2)

    # ------ D2 ------
    trueR_D2 = gen_intensity_mat(computed_D2, 2)
    expt_D2 = gen_intensity_mat(dataD2, 0)
    I_D2 = np.divide(expt_D2, trueR_D2)
    I_D2 = clean_mat(I_D2)
    # ----------------

    # ------ HD ------
    trueR_HD = gen_intensity_mat(computed_HD, 2)
    expt_HD = gen_intensity_mat(dataHD, 0)
    I_HD = np.divide(expt_HD, trueR_HD)
    I_HD = clean_mat(I_HD)
    # ----------------

    # ------ H2 ------
    trueR_H2 = gen_intensity_mat(computed_H2, 2)
    expt_H2 = gen_intensity_mat(dataH2, 0)
    I_H2 = np.divide(expt_H2, trueR_H2)
    I_H2 = clean_mat(I_H2)
    # ----------------

    # generate the RHS : sensitivity factor
    sD2 = gen_s_linear(computed_D2, param)
    sHD = gen_s_linear(computed_HD, param)
    sH2 = gen_s_linear(computed_H2, param)

    # residual matrix
    eD2 = I_D2 - sD2
    eHD = I_HD - sHD
    eH2 = I_H2 - sH2

    eD2 = np.multiply(wMat_D2, eD2)
    eHD = np.multiply(wMat_HD, eHD)
    eH2 = np.multiply(wMat_H2, eH2)

    eD2 = clean_mat(eD2)
    eHD = clean_mat(eHD)
    eH2 = clean_mat(eH2)

    # E = np.sum(np.square(eD2)) + np.sum(np.square(eHD))\
    #    + np.sum(np.square(eH2))
    
    index = T_independent_index()
    factor = 5
    eD2[index[0]] = eD2[index[0]] * factor
    eHD[index[1]] = eHD[index[1]] * factor
    eH2[index[2]] = eH2[index[2]] * factor

    E = np.sum(np.abs(eD2)) + np.sum(np.abs(eHD)) +\
        np.sum(np.abs(eH2))

    return E

# *******************************************************************
# *******************************************************************


def residual_quadratic(param):
    '''Function which computes the residual (as sum of squares) comparing the
    ratio of expt to theoretical intensity ratio to the sensitivity  profile
    modelled as  a line, ( 1+ c1*x + c2*x**2 )

    param : T, c1, c2

    '''
    TK = param[0]

    sosD2 = compute_series_para.sumofstate_D2(TK)
    sosHD = compute_series_para.sumofstate_HD(TK)
    sosH2 = compute_series_para.sumofstate_H2(TK)

    computed_D2 = compute_series_para.spectra_D2(TK, OJ_D2, QJ_D2,
                                                 SJ_D2, sosD2)
    computed_HD = compute_series_para.spectra_HD(TK, OJ_HD, QJ_HD,
                                                 SJ_HD, sosHD)
    computed_H2 = compute_series_para.spectra_H2_c(TK, OJ_H2,
                                                   QJ_H2, sosH2)

    # ------ D2 ------
    trueR_D2 = gen_intensity_mat(computed_D2, 2)
    expt_D2 = gen_intensity_mat(dataD2, 0)
    I_D2 = np.divide(expt_D2, trueR_D2)
    I_D2 = clean_mat(I_D2)
    # ----------------

    # ------ HD ------
    trueR_HD = gen_intensity_mat(computed_HD, 2)
    expt_HD = gen_intensity_mat(dataHD, 0)
    I_HD = np.divide(expt_HD, trueR_HD)
    I_HD = clean_mat(I_HD)
    # ----------------

    # ------ H2 ------
    trueR_H2 = gen_intensity_mat(computed_H2, 2)
    expt_H2 = gen_intensity_mat(dataH2, 0)
    I_H2 = np.divide(expt_H2, trueR_H2)
    I_H2 = clean_mat(I_H2)
    # ----------------

    # generate the RHS : sensitivity factor
    sD2 = gen_s_quadratic(computed_D2, param)
    sHD = gen_s_quadratic(computed_HD, param)
    sH2 = gen_s_quadratic(computed_H2, param)

    # residual matrix
    eD2 = I_D2 - sD2
    eHD = I_HD - sHD
    eH2 = I_H2 - sH2

    eD2 = np.multiply(wMat_D2, eD2)
    eHD = np.multiply(wMat_HD, eHD)
    eH2 = np.multiply(wMat_H2, eH2)

    eD2 = clean_mat(eD2)
    eHD = clean_mat(eHD)
    eH2 = clean_mat(eH2)

    # E = np.sum(np.square(eD2)) + np.sum(np.square(eHD))\
    #    + np.sum(np.square(eH2))
    
    index = T_independent_index()
    factor = 5
    eD2[index[0]] = eD2[index[0]] * factor
    eHD[index[1]] = eHD[index[1]] * factor
    eH2[index[2]] = eH2[index[2]] * factor    

    E = np.sum(np.abs(eD2)) + np.sum(np.abs(eHD)) +\
        np.sum(np.abs(eH2))

    return E

# *******************************************************************
# *******************************************************************


def residual_cubic(param):
    '''Function which computes the residual (as sum of squares) comparing the
    ratio of expt to theoretical intensity ratio to the sensitivity  profile
    modelled as  a line, ( 1+ c1*x + c2*x**2 + c3*x**3 )

    param : T, c1, c2, c3

    '''
    TK = param[0]
    sosD2 = compute_series_para.sumofstate_D2(TK)
    sosHD = compute_series_para.sumofstate_HD(TK)
    sosH2 = compute_series_para.sumofstate_H2(TK)

    computed_D2 = compute_series_para.spectra_D2(TK, OJ_D2, QJ_D2,
                                                 SJ_D2, sosD2)
    computed_HD = compute_series_para.spectra_HD(TK, OJ_HD, QJ_HD,
                                                 SJ_HD, sosHD)
    computed_H2 = compute_series_para.spectra_H2_c(TK, OJ_H2,
                                                   QJ_H2, sosH2)
    # ------ D2 ------
    trueR_D2 = gen_intensity_mat(computed_D2, 2)
    expt_D2 = gen_intensity_mat(dataD2, 0)
    I_D2 = np.divide(expt_D2, trueR_D2)
    I_D2 = clean_mat(I_D2)
    # ----------------

    # ------ HD ------
    trueR_HD = gen_intensity_mat(computed_HD, 2)
    expt_HD = gen_intensity_mat(dataHD, 0)
    I_HD = np.divide(expt_HD, trueR_HD)
    I_HD = clean_mat(I_HD)
    # ----------------

    # ------ H2 ------
    trueR_H2 = gen_intensity_mat(computed_H2, 2)
    expt_H2 = gen_intensity_mat(dataH2, 0)
    I_H2 = np.divide(expt_H2, trueR_H2)
    I_H2 = clean_mat(I_H2)
    # ----------------

    # generate the RHS : sensitivity factor
    sD2 = gen_s_cubic(computed_D2, param)
    sHD = gen_s_cubic(computed_HD, param)
    sH2 = gen_s_cubic(computed_H2, param)

    # residual matrix
    eD2 = I_D2 - sD2
    eHD = I_HD - sHD
    eH2 = I_H2 - sH2

    eD2 = np.multiply(wMat_D2, eD2)
    eHD = np.multiply(wMat_HD, eHD)
    eH2 = np.multiply(wMat_H2, eH2)

    eD2 = clean_mat(eD2)
    eHD = clean_mat(eHD)
    eH2 = clean_mat(eH2)

    # E = np.sum(np.square(eD2)) + np.sum(np.square(eHD))\
    #    + np.sum(np.square(eH2))

    index = T_independent_index()
    factor = 5
    eD2[index[0]] = eD2[index[0]] * factor
    eHD[index[1]] = eHD[index[1]] * factor
    eH2[index[2]] = eH2[index[2]] * factor    

    E = np.sum(np.abs(eD2)) + np.sum(np.abs(eHD)) +\
        np.sum(np.abs(eH2))

    return E

# *******************************************************************
# *******************************************************************


def residual_quartic(param):
    '''Function which computes the residual (as sum of squares) comparing the
    ratio of expt to theoretical intensity ratio to the sensitivity  profile
    modelled as  a line, ( 1+ c1*x + c2*x**2 + c3*x**3 + c4*x**4 )

    param : T, c1, c2, c3, c4

    '''
    TK = param[0]

    sosD2 = compute_series_para.sumofstate_D2(TK)
    sosHD = compute_series_para.sumofstate_HD(TK)
    sosH2 = compute_series_para.sumofstate_H2(TK)

    computed_D2 = compute_series_para.spectra_D2(TK, OJ_D2, QJ_D2,
                                                 SJ_D2, sosD2)
    computed_HD = compute_series_para.spectra_HD(TK, OJ_HD, QJ_HD,
                                                 SJ_HD, sosHD)
    computed_H2 = compute_series_para.spectra_H2_c(TK, OJ_H2,
                                                   QJ_H2, sosH2)

    # ------ D2 ------
    trueR_D2 = gen_intensity_mat(computed_D2, 2)
    expt_D2 = gen_intensity_mat(dataD2, 0)
    I_D2 = np.divide(expt_D2, trueR_D2)
    I_D2 = clean_mat(I_D2)
    # ----------------

    # ------ HD ------
    trueR_HD = gen_intensity_mat(computed_HD, 2)
    expt_HD = gen_intensity_mat(dataHD, 0)
    I_HD = np.divide(expt_HD, trueR_HD)
    I_HD = clean_mat(I_HD)
    # ----------------

    # ------ H2 ------
    trueR_H2 = gen_intensity_mat(computed_H2, 2)
    expt_H2 = gen_intensity_mat(dataH2, 0)
    I_H2 = np.divide(expt_H2, trueR_H2)
    I_H2 = clean_mat(I_H2)
    # ----------------

    # generate the RHS : sensitivity factor
    sD2 = gen_s_quartic(computed_D2, param)
    sHD = gen_s_quartic(computed_HD, param)
    sH2 = gen_s_quartic(computed_H2, param)

    # residual matrix
    eD2 = I_D2 - sD2
    eHD = I_HD - sHD
    eH2 = I_H2 - sH2

    eD2 = np.multiply(wMat_D2, eD2)
    eHD = np.multiply(wMat_HD, eHD)
    eH2 = np.multiply(wMat_H2, eH2)

    eD2 = clean_mat(eD2)
    eHD = clean_mat(eHD)
    eH2 = clean_mat(eH2)

    # E = np.sum(np.square(eD2)) + np.sum(np.square(eHD))\
    #    + np.sum(np.square(eH2))

    index = T_independent_index()
    factor = 5
    eD2[index[0]] = eD2[index[0]] * factor
    eHD[index[1]] = eHD[index[1]] * factor
    eH2[index[2]] = eH2[index[2]] * factor    

    E = np.sum(np.abs(eD2)) + np.sum(np.abs(eHD)) +\
        np.sum(np.abs(eH2))

    return E

# *******************************************************************
# *******************************************************************


def residual_quintuple(param):
    '''Function which computes the residual (as sum of squares) comparing the
    ratio of expt to theoretical intensity ratio to the sensitivity  profile
    modelled as  a line, ( 1+ c1*x + c2*x**2 + c3*x**3 + c4*x**4 )

    param : T, c1, c2, c3, c4

    '''
    TK = param[0]

    sosD2 = compute_series_para.sumofstate_D2(TK)
    sosHD = compute_series_para.sumofstate_HD(TK)
    sosH2 = compute_series_para.sumofstate_H2(TK)

    computed_D2 = compute_series_para.spectra_D2(TK, OJ_D2, QJ_D2,
                                                 SJ_D2, sosD2)
    computed_HD = compute_series_para.spectra_HD(TK, OJ_HD, QJ_HD,
                                                 SJ_HD, sosHD)
    computed_H2 = compute_series_para.spectra_H2_c(TK, OJ_H2,
                                                   QJ_H2, sosH2)

    # ------ D2 ------
    trueR_D2 = gen_intensity_mat(computed_D2, 2)
    expt_D2 = gen_intensity_mat(dataD2, 0)
    I_D2 = np.divide(expt_D2, trueR_D2)
    I_D2 = clean_mat(I_D2)
    # ----------------

    # ------ HD ------
    trueR_HD = gen_intensity_mat(computed_HD, 2)
    expt_HD = gen_intensity_mat(dataHD, 0)
    I_HD = np.divide(expt_HD, trueR_HD)
    I_HD = clean_mat(I_HD)
    # ----------------

    # ------ H2 ------
    trueR_H2 = gen_intensity_mat(computed_H2, 2)
    expt_H2 = gen_intensity_mat(dataH2, 0)
    I_H2 = np.divide(expt_H2, trueR_H2)
    I_H2 = clean_mat(I_H2)
    # ----------------

    # generate the RHS : sensitivity factor
    sD2 = gen_s_quintuple(computed_D2, param)
    sHD = gen_s_quintuple(computed_HD, param)
    sH2 = gen_s_quintuple(computed_H2, param)

    # residual matrix
    eD2 = I_D2 - sD2
    eHD = I_HD - sHD
    eH2 = I_H2 - sH2

    eD2 = np.multiply(wMat_D2, eD2)
    eHD = np.multiply(wMat_HD, eHD)
    eH2 = np.multiply(wMat_H2, eH2)

    eD2 = clean_mat(eD2)
    eHD = clean_mat(eHD)
    eH2 = clean_mat(eH2)

    # E = np.sum(np.square(eD2)) + np.sum(np.square(eHD))\
    #    + np.sum(np.square(eH2))

    index = T_independent_index()
    factor = 5
    eD2[index[0]] = eD2[index[0]] * factor
    eHD[index[1]] = eHD[index[1]] * factor
    eH2[index[2]] = eH2[index[2]] * factor

    E = np.sum(np.abs(eD2)) + np.sum(np.abs(eHD)) +\
        np.sum(np.abs(eH2))

    return E

# *******************************************************************
# *******************************************************************
# Fit functions
# *******************************************************************
# *******************************************************************


def run_fit_linear(init_T, init_k1):
    '''Function performing the actual fit using the residual_linear function
    defined earlier '''

    # init_k1 : Intial guess

    param_init = np.array([init_T, init_k1])
    print("**********************************************************")
    #print("Testing the residual function with data")
    print("Initial coef :  T={0}, k1={1} output = {2}".format(init_T, init_k1, \
          (residual_linear(param_init))))


    print("\nOptimization run: Linear     \n")
    res = opt.minimize(residual_linear, param_init, method='Nelder-Mead', \
                              options={'xatol': 1e-9, 'fatol': 1e-9})

    print(res)
    optT = res.x[0]
    optk1 = res.x[1]
    print("\nOptimized result : T={0}, k1={1} \n".format(round(optT, 6),
                                                         round(optk1, 6)))

    correction_curve = 1+(optk1/scale1)*(xaxis-scenter)  # generate the correction curve

    np.savetxt("correction_linear.txt", correction_curve, fmt='%2.8f',\
               header='corrn_curve_linear', comments='')

    print("**********************************************************")

    # save log -----------
    log.info('\n *******  Optimization run : Linear  *******')
    log.info('\n\t Initial : T = %4.8f, c1 = %4.8f\n', init_T, init_k1)
    log.info('\n\t %s\n', res)
    log.info('\n Optimized result : T = %4.8f, c1 = %4.8f\n', optT, optk1)
    log.info(' *******************************************')
    return res.fun
    # --------------------

# *******************************************************************
# *******************************************************************

def run_fit_quadratic(init_T, init_k1, init_k2):
    '''Function performing the actual fit using the residual_quadratic function
    defined earlier '''

    # init_k1 : Intial guess

    param_init = np.array([init_T, init_k1 , init_k2])
    print("**********************************************************")
    #print("Testing the residual function with data")
    print("Initial coef :  T={0}, k1={1}, k2={2} output = {3}".format(init_T, init_k1, \
         init_k2, (residual_quadratic(param_init))))

    print("\nOptimization run: Quadratic     \n")
    res = opt.minimize(residual_quadratic, param_init, method='Nelder-Mead', \
                              options={'xatol': 1e-9, 'fatol': 1e-9, 'maxiter':1500})

    print(res)
    optT = res.x[0]
    optk1 = res.x[1]
    optk2 = res.x[2]
    print("\nOptimized result : T={0}, k1={1}, k2={2} \n".format(round(optT, 6)\
     ,  round(optk1, 6), round(optk2, 6)))

     # generate the correction curve
    correction_curve = 1 + (optk1 / scale1)*(xaxis - scenter)\
        + (optk2 / scale2) * (xaxis - scenter)**2

    np.savetxt("correction_quadratic.txt", correction_curve, fmt='%2.8f',\
               header='corrn_curve_quadratic', comments='')

    print("**********************************************************")

    # save log -----------
    log.info('\n *******  Optimization run : Quadratic  *******')
    log.info('\n\t Initial : c1 = %4.8f, c2 = %4.8f\n', init_k1, init_k2 )
    log.info('\n\t %s\n', res)
    log.info('\n Optimized result : c1 = %4.8f, c2 = %4.8f\n', optk1, optk2)
    log.info(' *******************************************')
    return res.fun
    # --------------------

# *******************************************************************
# *******************************************************************

def run_fit_cubic(init_T, init_k1, init_k2, init_k3):
    '''Function performing the actual fit using the residual_cubic function
    defined earlier '''

    # init_k1 : Intial guess

    param_init = np.array([init_T, init_k1 , init_k2 , init_k3])
    print("**********************************************************")
    #print("Testing the residual function with data")
    print("Initial coef :  T={0}, k1={1}, k2={2}, k3={3}, output = {4}".\
          format(init_T, init_k1, init_k2, init_k3, (residual_cubic(param_init))))


    print("\nOptimization run : Cubic     \n")
    res = opt.minimize(residual_cubic, param_init, method='Nelder-Mead', \
                              options={'xatol': 1e-9, 'fatol': 1e-9, 'maxiter':2500})

    print(res)
    optT = res.x[0]
    optk1 = res.x[1]
    optk2 = res.x[2]
    optk3 = res.x[3]
    print("\nOptimized result : T={0}, k1={1}, k2={2}, k3={3} \n".\
          format(round(optT, 6) ,  round(optk1, 6), round(optk2, 6),\
                 round(optk3, 6)))

    correction_curve = 1+(optk1/scale1)*(xaxis-scenter)  \
        + (optk2/scale2)*(xaxis-scenter)**2  \
        +(optk3/scale3)*(xaxis-scenter)**3 # generate the correction curve

    np.savetxt("correction_cubic.txt", correction_curve, fmt='%2.8f',\
               header='corrn_curve_cubic', comments='')

    print("**********************************************************")
    # save log -----------
    log.info('\n *******  Optimization run : Cubic  *******')
    log.info('\n\t Initial : c1 = %4.8f, c2 = %4.8f, c3 = %4.8f\n', init_k1,\
             init_k2, init_k3)
    log.info('\n\t %s\n', res)
    log.info('\n Optimized result : c1 = %4.8f, c2 = %4.8f, c3 = %4.8f\n',\
             optk1, optk2, optk3)
    log.info(' *******************************************')
    return res.fun
    # --------------------

# *******************************************************************
# *******************************************************************

def run_fit_quartic(init_T, init_k1, init_k2, init_k3, init_k4):
    '''Function performing the actual fit using the residual_quartic function
    defined earlier '''

    # init_k1 : Intial guess

    param_init = np.array([init_T, init_k1 , init_k2 , init_k3, init_k4])
    print("**********************************************************")
    #print("Testing the residual function with data")
    print("Initial coef :  T={0}, k1={1}, k2={2}, k3={3}, k4={4} output = {5}".\
          format(init_T, init_k1, init_k2, init_k3, init_k4,
                 (residual_quartic(param_init))))


    print("\nOptimization run : Quartic     \n")
    res = opt.minimize(residual_quartic, param_init, method='Nelder-Mead', \
                              options={'xatol': 1e-9, 'fatol': 1e-9, 'maxiter':1500})

    print(res)
    optT = res.x[0]
    optk1 = res.x[1]
    optk2 = res.x[2]
    optk3 = res.x[3]
    optk4 = res.x[4]
    print("\nOptimized result : T={0}, k1={1}, k2={2}, k3={3}, k4={4} \n".\
          format(round(optT, 6) ,  round(optk1, 6), round(optk2, 6),\
                 round(optk3, 6), round(optk4, 6)))

    # generate the correction curve
    correction_curve= 1+(optk1/scale1)*(xaxis-scenter)  \
        +(optk2/scale2)*(xaxis-scenter)**2  \
        +(optk3/scale3)*(xaxis-scenter)**3 \
            +(optk4/scale4)*(xaxis-scenter)**4

    np.savetxt("correction_quartic.txt", correction_curve, fmt='%2.8f',\
               header='corrn_curve_quartic', comments='')

    print("**********************************************************")
    # save log -----------
    log.info('\n *******  Optimization run : Quartic  *******')
    log.info('\n\t Initial : c1 = %4.8f, c2 = %4.8f, c3 = %4.8f, c4 = %4.8f\n', init_k1,\
             init_k2, init_k3, init_k4)
    log.info('\n\t %s\n', res )
    log.info('\n Optimized result : c1 = %4.8f, c2 = %4.8f, c3 = %4.8f, c4 = %4.8f\n',\
             optk1, optk2, optk3, optk4)
    log.info(' *******************************************')
    return res.fun
    # --------------------


# *******************************************************************
# *******************************************************************

def run_fit_quintuple(init_T, init_k1, init_k2, init_k3, init_k4, init_k5):
    '''Function performing the actual fit using the residual_quintuple function
    defined earlier '''

    # init_k1 : Intial guess

    param_init = np.array([init_T, init_k1 , init_k2 , init_k3, init_k4, init_k5])
    print("**********************************************************")
    #print("Testing the residual function with data")
    print("Initial coef :  T={0}, k1={1}, k2={2}, k3={3}, k4={4}, k5={5} output = {6}".\
          format(init_T, init_k1, init_k2, init_k3, init_k4, init_k5,
                 (residual_quintuple(param_init))))


    print("\nOptimization run : Quintuple  \n")
    res = opt.minimize(residual_quintuple, param_init, method='Nelder-Mead', \
                              options={'xatol': 1e-9, 'fatol': 1e-9, 'maxiter':1500})

    print(res)
    optT = res.x[0]
    optk1 = res.x[1]
    optk2 = res.x[2]
    optk3 = res.x[3]
    optk4 = res.x[4]
    optk5 = res.x[5]
    print("\nOptimized result : T={0}, k1={1}, k2={2}, k3={3}, k4={4}, k5={5} \n".\
          format(round(optT, 6) ,  round(optk1, 6), round(optk2, 6),\
                 round(optk3, 6), round(optk4, 6), round(optk5, 6)))

    # generate the correction curve
    correction_curve= 1+(optk1/scale1)*(xaxis-scenter)  \
        +(optk2/scale2)*(xaxis-scenter)**2  \
          +(optk3/scale3)*(xaxis-scenter)**3 \
            +(optk4/scale4)*(xaxis-scenter)**4 \
              +(optk5/scale5)*(xaxis-scenter)**5

    np.savetxt("correction_quintuple.txt", correction_curve, fmt='%2.8f',\
               header='corrn_curve_quintuple', comments='')

    print("**********************************************************")
    # save log -----------
    log.info('\n *******  Optimization run : Quintuple  *******')
    log.info('\n\t Initial : c1 = %4.8f, c2 = %4.8f, c3 = %4.8f, c4 = %4.8f, c5 = %4.8f\n', init_k1,\
             init_k2, init_k3, init_k4, init_k5)
    log.info('\n\t %s\n', res )
    log.info('\n Optimized result : c1 = %4.8f, c2 = %4.8f, c3 = %4.8f, c4 = %4.8f, c5 = %4.8f\n',\
             optk1, optk2, optk3, optk4, optk5)
    log.info(' *******************************************')
    return res.fun
    # --------------------


# *******************************************************************
# *******************************************************************
# *******************************************************************


def plot_curves(residual_array="None"):
    '''
    If array containing residuals is not provided
    then the plot of residuals vs number of variables
    will not be made

    '''
    # Load the saved correction curves for  plotting
    # outputs from last run will be loaded
    correction_line = np.loadtxt("./correction_linear.txt", skiprows=1)
    correction_quad = np.loadtxt("./correction_quadratic.txt", skiprows=1)
    correction_cubic = np.loadtxt("./correction_cubic.txt", skiprows=1)
    correction_quartic = np.loadtxt("./correction_quartic.txt", skiprows=1)
    correction_quintuple = np.loadtxt("./correction_quintuple.txt", skiprows=1)

    # ---------------------------------------------------------------------

    # Plotting the data

    txt = ("*Generated from 'wavelength_sensitivity.py' on the\
          \nGitHub Repository: IntensityCalbr ")

    # FIGURE 0 INITIALIZED

    plt.figure(0)
    ax0 = plt.axes()
    plt.title('Fitting result', fontsize=22)

    plt.plot(xaxis, correction_line, 'r', linewidth=3, label='line_fit')
    plt.plot(xaxis, correction_quad, 'g', linewidth=4.2, label='quad_fit')
    plt.plot(xaxis, correction_cubic, 'b--', linewidth=2.65, label='cubic_fit')
    plt.plot(xaxis, correction_quartic, 'k--', linewidth=2.65, label='quartic_fit')
    plt.plot(xaxis, correction_quintuple, 'r--', linewidth=2.25, label='5th order fit')

    plt.xlabel('Wavenumber / $cm^{-1}$', fontsize=20)
    plt.ylabel('Relative sensitivity', fontsize=20)
    plt.grid(True, which='both')  # ax.grid(True, which='both')

    # change following as needed
    ax0.tick_params(axis='both', labelsize=20)

    xmin = np.amin(xaxis - 10)
    xmax = np.amax(xaxis + 10)
    
    plt.xlim((xmax, xmin)) #  setting xaxis range
    ax0.set_ylim([0, 2.1]) #  change this if the ylimit is not enough

    ax0.minorticks_on()
    ax0.tick_params(which='minor', right='on')
    ax0.tick_params(axis='y', labelleft='on', labelright='on')
    plt.text(0.05, 0.0095, txt, fontsize=6, color="dimgrey",
             transform=plt.gcf().transFigure)
    plt.legend(loc='upper left', fontsize=16)
    
    # markers showing the bands positions whose data is used for fit 
    plt.plot(computed_D2[:,1], dummyD2, 'mo' )
    plt.plot(computed_HD[:,1], dummyHD, 'cv' )
    plt.plot(computed_H2[:,1], dummyH2, 'gD' )

    if type(residual_array) != str:
        if isinstance(residual_array, (list, np.ndarray)):
            # -----------------------------------------------------
            # FIGURE 1 INITIALIZED

            xv = np.arange(1, 6, 1)
            plt.figure(1)
            ax1 = plt.axes()
            plt.title('Residuals', fontsize=21)
            plt.plot(xv, residual_array, 'ro--')
            plt.xlabel('degree of polynomial', fontsize=20)
            plt.ylabel('Residual', fontsize=20)
            plt.grid(True)  # ax.grid(True, which='both')
            ax1.tick_params(axis='both', labelsize=20)
        else:
            print('\tWrong type of parameter : residual_array. \
                  Quitting plotting.')
    else:
        print('\tResidual array not provided. plot of residuals not made!')


# ***************************************************************

# ******************** CHECKS FOR INPUTS ************************
# ***************************************************************


wMat_D2 = 1
wMat_HD = 1
wMat_H2 = 1

# checks for input done here

# generate calculated data for the entered J values
TK = 299
sosD2 = compute_series_para.sumofstate_D2(TK)
sosHD = compute_series_para.sumofstate_HD(TK)    
sosH2 = compute_series_para.sumofstate_H2(TK)

computed_D2 = compute_series_para.spectra_D2(TK, OJ_D2, QJ_D2,
                                                 SJ_D2, sosD2)
computed_HD = compute_series_para.spectra_HD(TK, OJ_HD, QJ_HD,
                                                 SJ_HD, sosHD)
computed_H2 = compute_series_para.spectra_H2_c(TK, OJ_H2,
                                                   QJ_H2, sosH2)

# checks for dimension match done here
if(len(computed_D2) != dataD2.shape[0]):
    print('D2 : Dimension of input data does not match with the calculated\
           spectra. Check input expt data or the J-indices entered.')
    sys.exit("\tError: Quitting.")

if(len(computed_HD) != dataHD.shape[0]):
    print('H2 : Dimension of input data does not match with the calculated\
           spectra. Check input expt data or the J-indices entered.')
    sys.exit("\tError: Quitting.")

if(len(computed_H2) != dataH2.shape[0]):
    print('H2 : Dimension of input data does not match with the calculated\
           spectra. Check input expt data or the J-indices entered.')
    sys.exit("\tError: Quitting.")

# ------------------------------------------------
# TESTS

trueR_D2 = gen_intensity_mat(computed_D2, 2)
expt_D2 = gen_intensity_mat(dataD2, 0)

trueR_HD = gen_intensity_mat(computed_HD, 2)
expt_HD = gen_intensity_mat(dataHD, 0)

trueR_H2 = gen_intensity_mat(computed_H2, 2)
expt_H2 = gen_intensity_mat(dataH2, 0)

I_D2 = np.divide(expt_D2, trueR_D2)
I_HD = np.divide(expt_HD, trueR_HD)
I_H2 = np.divide(expt_H2, trueR_H2)

I_D2 = clean_mat(I_D2)
I_HD = clean_mat(I_HD)
I_H2 = clean_mat(I_H2)

# print(I_H2)

errH2_output = gen_weight(dataH2)
errHD_output = gen_weight(dataHD)
errD2_output = gen_weight(dataD2)

sD2 = gen_s_linear(computed_D2, param_linear)
sHD = gen_s_linear(computed_HD, param_linear)
sH2 = gen_s_linear(computed_H2, param_linear)

eD2 = (np.multiply(errD2_output, I_D2) - sD2)
eHD = (np.multiply(errHD_output, I_HD) - sHD)
eH2 = (np.multiply(errH2_output, I_H2) - sH2)

eD2 = clean_mat(eD2)

eHD = clean_mat(eHD)

eH2 = clean_mat(eH2)

resd_lin = residual_linear(param_linear)
resd_quad = residual_quadratic(param_quadratic)
resd_cubic = residual_cubic(param_cubic)
resd_quar = residual_quartic(param_quartic)
resd_quint = residual_quintuple(param_quintuple)

print('Value of residuals with default coefs are')
print('\t linear \t:', resd_lin)
print('\t quadratic \t:', resd_quad)
print('\t cubic  \t:', resd_cubic)
print('\t quartic \t:', resd_quar)
print('\t quintuple \t:', resd_quint)

# -----------------------------------------------------
#  Dummy value for plot (vs frequencies)
#   Shows which band were analyzed in the fitting
val=0.125
dummyD2 = np.full(len(computed_D2), val)
dummyHD = np.full(len(computed_HD), val)
dummyH2 = np.full(len(computed_H2), val)

# -----------------------------------------------------

index=T_independent_index()
eD2[index[0]]=eD2[index[0]]*1.25

eH2[index[2]]=eH2[index[2]]*10

# IntensityCalbr

Repository : [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4655294.svg)](https://doi.org/10.5281/zenodo.4655294)  |  Link to article: [10.1002/jrs.6221](https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/10.1002/jrs.6221)

----
This work has been published in the following article:<br><br>
**Accurate intensity calibration of multichannel spectrometers using Raman intensity ratios**<br>
Ankit Raj, Chihiro Kato, Henryk A. Witek and Hiro‐o Hamaguchi<br>
*Journal of Raman Spectroscopy*<br>
[10.1002/jrs.6221](https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/10.1002/jrs.6221)

----

Repository containing programs implementing the procedure for obtaining wavelength-dependent sensitivity for calibration of Raman spectrometers based on multi-channel detectors. The present scheme is a multi-step procedure based on following three steps:
- C<sub>0</sub> : Correction for non-linear sampling of photons in the wavenumber scale.
- C<sub>1</sub> : Correction for channel-to-channel variation in the sensitivity of the spectrometer.
- C<sub>2</sub> : Final correction derived from Raman spectroscopic intensities.

In order to determine the final correction (C<sub>2</sub>) the relative band intensities between all pairs of bands are analyzed simultaneously by a comparison with the analogous reference intensities. Least squares minimization is used to determine the coefficients of a polynomial used to model the wavelength-dependent sensitivity representing the C<sub>2</sub> correction.

---

## Why we are doing this?

In any Raman spectrometer, light scattered by the molecules travels to the detector while passing through/by some optical components (for example, lens, mirrors, grating, etc..) In this process, the scattered light intensity is modulated by the non-uniform reflectance/transmission of the optical components. Reflectance and transmission of the optics are wavenumber dependent.
The net modulation to the light intensity, defined as <i>M</i>(&nu;), over the studied spectral range can be expressed as product(s) of  the wavenumber dependent performance of the i<sup>th</sup> optical element as

<a href="https://www.codecogs.com/eqnedit.php?latex=\dpi{200}&space;\large&space;M(\nu)&space;=&space;\Pi&space;c_{i}w_{i}(\nu)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\dpi{200}&space;\large&space;M(\nu)&space;=&space;\Pi&space;c_{i}w_{i}(\nu)" title="\large M(\nu) = \Pi c_{i}w_{i}(\nu)" /></a>

Here, <i>c<sub>i</sub></i> is a coefficient and <i>w<sub>i</sub>(&nu;)</i> is the wavenumber dependent transmission or reflectance of the i<sup>th</sup> optical component.

In most cases, determining the individual performance of each optical element is a cumbersome task. Hence, we limit our focus to approximately determine the relative form of <i>M</i>(&nu;), from experimental data. By relative form, it is meant that <i>M</i>(&nu;) is normalized to unity within the studied spectral range. If <i>M</i>(&nu;) is known, then we can correct the observed intensities in the Raman spectrum by dividing those by <i>M</i>(&nu;). In general, this is the principle of all intensity calibration procedure in optical spectroscopy.

In our work, we assume <i>M</i>(&nu;) &cong; C<sub>1</sub>(&nu;) C<sub>2</sub>(&nu;) / C<sub>0</sub>(&nu;) [The wavenumber dependence in not explicitly stated when C<sub>0</sub>, C<sub>1</sub> and C<sub>2</sub> are discussed in the following text. ]  The three contributions, C<sub>0</sub>(&nu;) to C<sub>2</sub>(&nu;)  are determined in two steps in this analysis.

- In the first step, (C<sub>0</sub> / C<sub>1</sub>) correction are determined using the wavenumber axis and the spectrum of a broad band white light source. [(See example)](https://github.com/ankit7540/IntensityCalbr/blob/master/PythonModule/determine_C0_C1_correction/Examples/Example_for_C0_C1.ipynb)
- C<sub>2</sub> is determined from the observed Raman intensities, where the reference or true intensities are known or can be computed. This can be done using (i) pure-rotational Raman bands of molecular hydrogen and isotopologues, (ii) vibration-rotation Raman bands of the same gases and (iii) vibrational Raman bands of some liquids.

The multiplicative correction to the Raman spectrum is then : (C<sub>0</sub> / C<sub>1</sub>C<sub>2</sub>)

---

## Methodology
Observed intensities from selected bands are analyzed as pairs among all such bands, to form a matrix. A similar matrix of intensity ratios are compared to the true ratios, and the coefficients for the wavelength/wavenumber dependent sensitivity curve, modelled as a polynomial function, is obtained via non-linear minimization technique.

The general scheme is given as follows.

<p align="center">
<img  src="https://github.com/ankit7540/IntensityCalbr/blob/master/img/scheme.png" data-canonical-src="https://github.com/ankit7540/IntensityCalbr/blob/master/img/scheme.png" width="450" height="629" /> </p>

Explanation for the steps of the scheme are following :


-  The experimental data available as 2D array is used to generate the **R**<sub>obs.</sub> matrix. Using the errors in band areas, the weights are generated.
-  The reference data computed at the given temperature is used to generate the **R**<sub>true</sub> matrix.
-  Next, using the band positions and initial coefs of the polynomial, the  **S**  matrix is generated.
-  The dimensions of the four matrices are checked before moving to the next step.
-  Difference matrix, **D**<sub></sub>, (for each species) is generated using the **R**<sub>obs</sub>, **R**<sub>true</sub> and **S**  matrix.
-  The elements of the difference matrix are weighted using the corresponding elements of the weight matrix **W**.
-  The norm of the difference matrix is computed. This norm is minimized by varying the coefficients of the polynomial (re-computing the  **S**  matrix using updated values of the coefficients of the polynomial and the reference matrix **R**<sub>true</sub> using the updated value of the temperature ).
-  Use the optimized coefficients of the polynomial to generate the C<sub>2</sub> correction. Check temperature obtained from the Raman intensities for physical correctness.


## References
In the following works, the ratio of intensities from common rotational states are compared to the corresponding theoretical ratio to obtain the wavelength dependent sensitivity curve.

  - H. Okajima, H. Hamaguchi, J. Raman Spectrosc. 2015, 46, 1140. [(10.1002/jrs.4731)](https://doi.org/10.1002/jrs.4731)
  - H. Hamaguchi, I. Harada, T. Shimanouchi, Chem. Lett. 1974, 3, 1405. [(cl.1974.1405)](https://www.journal.csj.jp/doi/pdf/10.1246/cl.1974.1405)
  - A. Raj, C. Kato, H.A. Witek. H. Hamaguchi, J. Raman Spec 2020, 51, 2066. [(10.1002/jrs.5955)]( https://doi.org/10.1002/jrs.5955)

This principle of comparing intensities (pure rotational Raman and rotation-vibration Raman) is extended to all bands in present work, requiring parametrizing of temperature in the scheme. Set of intensity ratios are then conveniently framed as a matrix, as shown in the above figure. The reference matrix can be computed if equations and required parameters are available, or,  if known intensities are available then they can work as reference (for given conditions).


## Input data required

**Intensity calibration**

 + Determination of C<sub>0</sub> and C<sub>1</sub> requires the vector/array of relative wavenumbers (which is used as the x-axis) and the measured spectrum of a broadband white-light source (we assume here that this source is close to a black-body emitter, so tungsten lamps will work). [(See example)](https://github.com/ankit7540/IntensityCalbr/blob/master/PythonModule/determine_C0_C1_correction/Examples/Example_for_C0_C1.ipynb)

 + General scheme : experimental band area, reference data either available before hand or computable. (If computable then appropriate functions are required to be called). **The following table lists the examples for all the schemes available for determining the final correction (defined as C<sub>2</sub>).**


| Raman transition type                |                                                                                                                                                                                                                |                                                                                                                                                                                                                                 |                                                                                                                                                                                               |                                                                                                                                                                                                                                   |
|--------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Pure rotational Raman intensities    | [t-dependent](https://github.com/ankit7540/IntensityCalbr/blob/master/PythonModule/determine_C2/rotationalRaman_H2_HD_D2/t_dependent/Example/example.ipynb)                                                    | [t-independent](https://github.com/ankit7540/IntensityCalbr/blob/master/PythonModule/determine_C2/rotationalRaman_H2_HD_D2/t_independent/Example/example.ipynb)                                                                 |                                                                                                                                                                                               |                                                                                                                                                                                                                                   |
| Vibration-rotation Raman intensities | [t-dependent](https://github.com/ankit7540/IntensityCalbr/blob/master/PythonModule/determine_C2/vibration_rotation_H2_HD_D2/T_dependent_analysis/example/example_genC2_parallel_t_dependent.ipynb)             | [t-independent](https://github.com/ankit7540/IntensityCalbr/blob/master/PythonModule/determine_C2/vibration_rotation_H2_HD_D2/T_independent_analysis/example/example_VR_TF.ipynb)                                               | [common rotational state](https://github.com/ankit7540/IntensityCalbr/blob/master/PythonModule/determine_C2/vibration_rotation_H2_HD_D2/common_rotational_state/Examples/example_genC2.ipynb) | [validation : temperature-determination](https://github.com/ankit7540/IntensityCalbr/blob/master/PythonModule/determine_C2/vibration_rotation_H2_HD_D2/temperature_determination/example/example_temperature_determination.ipynb) |
| Vibrational Raman liquids            | [relative intensities](https://github.com/ankit7540/IntensityCalbr/blob/master/PythonModule/determine_C2/vibrationalRaman_liquids/Using_relative_intensities/example/example_genC2_from_vibration_Raman.ipynb) | [anti-Stokes/Stokes intensities](https://github.com/ankit7540/IntensityCalbr/blob/master/PythonModule/determine_C2/vibrationalRaman_liquids/antiStokes_Stokes_ratios/example/example_antiStokes_Stokes_Raman_intensities.ipynb) |                                |                                                                                                                                                               |                                                                                                                                                                                                                                   |



 In this software repository, modules for computing reference intensities using reference excitation wavelength-dependent (&lambda; = 532.2 nm) ro-vibrational matrix elements of polarizability for pure rotation and rotational-vibrational Raman transitions are included. (At present this is possible for H<sub>2</sub>, HD and D<sub>2</sub> since their polarizability invariants can be computed to high accuracy. For other excitation wavelengths and Raman transitions not included in this work, see our earlier work :   A. Raj, H. Hamaguchi, and H. A. Witek , J. Chem. Phys. 148, 104308 (2018) [10.1063/1.5011433]( https://doi.org/10.1063/1.5011433 )

 - List of data required for analysis of pure rotational/ rotation-vibration Raman bands : experimental band area, *x*-axis vector for the spectra (in cm<sup>-1</sup> or wavelength). Indices of J-states for pure rotation; O, S, Q-bands for rotational-vibration bands, temperature (K) as additional parameters. The reference data is computed on the fly.


See specific program's readme regarding the use of the above data.

## Usage

Clone the repository or download the zip file. As per your choice of the programming environment and refer to the specific README inside the folders and proceed.

## Comments

 - **On convergence of the minimization scheme in intensity calibration :** The convergence of the optimization has been tested with artificial and actual data giving expected results. However, in certain cases convergence in the minimization may not be achieved based on the specific data set and the error in the intensity.

 - **Accuracy of the calibration :** It is highly suggested to perform an independent validation of the intensity calibration. This validation can be using anti-Stokes to Stokes intensity for determining the sample's temperature (for checking the accuracy of wavelength sensitivity correction). New ideas regarding testing the validity of intensity calibration are welcome. Please give comments in the "Issues" section of this repository.


## Other references

**NumPy** : Charles R. Harris, K. Jarrod Millman, Stéfan J. van der Walt, Ralf Gommers, Pauli Virtanen, David Cournapeau, Eric Wieser, Julian Taylor, Sebastian Berg, Nathaniel J. Smith, Robert Kern, Matti Picus, Stephan Hoyer, Marten H. van Kerkwijk, Matthew Brett, Allan Haldane, Jaime Fernández del Río, Mark Wiebe, Pearu Peterson, Pierre Gérard-Marchant, Kevin Sheppard, Tyler Reddy, Warren Weckesser, Hameer Abbasi, Christoph Gohlke & Travis E. Oliphant. "Array programming with NumPy", *Nature*, 585, 357–362 (2020) [10.1038/s41586-020-2649-2](https://doi.org/10.1038/s41586-020-2649-2)

**Scipy** : Pauli Virtanen, Ralf Gommers, Travis E. Oliphant, Matt Haberland, Tyler Reddy, David Cournapeau, Evgeni Burovski, Pearu Peterson, Warren Weckesser, Jonathan Bright, Stéfan J. van der Walt, Matthew Brett, Joshua Wilson, K. Jarrod Millman, Nikolay Mayorov, Andrew R. J. Nelson, Eric Jones, Robert Kern, Eric Larson, CJ Carey, İlhan Polat, Yu Feng, Eric W. Moore, Jake VanderPlas, Denis Laxalde, Josef Perktold, Robert Cimrman, Ian Henriksen, E.A. Quintero, Charles R Harris, Anne M. Archibald, Antônio H. Ribeiro, Fabian Pedregosa, Paul van Mulbregt, and SciPy 1.0 Contributors. (2020) "SciPy 1.0: Fundamental Algorithms for Scientific Computing in Python". *Nature Methods*, 17(3), 261-272. [10.1038/s41592-019-0686-2](https://doi.org/10.1038/s41592-019-0686-2)

**Non-linear optimization in SciPy** :  Travis E. Oliphant. "Python for Scientific Computing, *Computing in Science & Engineering*, 9, 10-20 (2007), DOI:10.1109/MCSE.2007.58


**Matplotlib**  : J. D. Hunter, "Matplotlib: A 2D Graphics Environment", *Computing in Science & Engineering*, vol. 9, no. 3, pp. 90-95, 2007.


**Orthogonal Distance Regression as used in SciPy** : (***i***) P. T. Boggs, R. Byrd, R. Schnabel, SIAM J. Sci. Comput. 1987, 8, 1052. (***ii***) P. T. Boggs, J. R. Donaldson, R. h. Byrd, R. B. Schnabel, ACM Trans. Math. Softw. 1989, 15, 348. (***iii***) J. W. Zwolak, P. T. Boggs, L. T. Watson, ACM Trans. Math. Softw. 2007, 33, 27. (***iv***)  P. T. Boggs and J. E. Rogers, “Orthogonal Distance Regression,” in “Statistical analysis of measurement error models and applications: proceedings of the AMS-IMS-SIAM joint summer research conference held June 10-16, 1989,” Contemporary Mathematics, vol. 112, pg. 186, 1990.

## Support/Questions/Issues
Please use "Issues" section for asking questions and reporting issues.


----
This work has been published in the following article:<br><br>
**Accurate intensity calibration of multichannel spectrometers using Raman intensity ratios>**<br>
Ankit Raj, Chihiro Kato, Henryk A. Witek and Hiro‐o Hamaguchi<br>
*Journal of Raman Spectroscopy*<br>
[10.1002/jrs.6221](https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/10.1002/jrs.6221)

----

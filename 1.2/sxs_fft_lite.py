#!/usr/bin/env python

import numpy as np
import scipy as sp
import matplotlib.mlab
import scipy.fftpack as sf

def mlab_psd(acces,dt,num_per_interval=None,noverlap=0):

	if num_per_interval == None:
		num_per_interval = len(acces)
	else:
		pass

	psd_sq,freq = matplotlib.mlab.psd(
		acces,
		num_per_interval,
		1./dt,
		detrend=matplotlib.mlab.detrend_mean,
		window=matplotlib.mlab.window_hanning,
		noverlap=noverlap,
		sides='onesided',
		scale_by_freq=True
		)
	psd = np.sqrt(psd_sq)
	return(psd[:-1],freq[:-1])

def scipy_fft(acces,dt):

	bin = len(acces)
	hanning = sp.hanning(len(acces))

	freq = sf.fftfreq(bin,dt)[0:bin/2]
	df = freq[1]-freq[0]
	fft = sf.fft(acces*hanning,bin)[0:bin/2]

	real = fft.real
	imag = fft.imag
	psd = np.abs(fft)/np.sqrt(df/2.)/float(bin) * np.sqrt(8./3)
	# np.sqrt(8./3) is the correction factor to match random power level to that without Hanning window.
	psd[0] /= np.sqrt(2)

	return(freq,real,imag,psd)

def scipy_fft_psd(acces,dt):

	bin = len(acces)
	hanning = sp.hanning(len(acces))

	freq = sf.fftfreq(bin,dt)[0:bin/2]
	df = freq[1]-freq[0]
	fft = sf.fft(acces*hanning,bin)[0:bin/2]

	psd = np.abs(fft)/np.sqrt(df/2.)/float(bin) * np.sqrt(8./3)
	# np.sqrt(8./3) is the correction factor to match random power level to that without Hanning window.
	psd[0] /= np.sqrt(2)

	return(psd,freq)

def calc_frf(reals,imags,force_reals,force_imags):

	ffts = reals + 1j * imags
	force_ffts = force_reals + 1j * force_imags

	frfs = ffts / force_ffts
	frf_real = np.average([frf.real for frf in frfs],axis=0)
	frf_imag = np.average([frf.imag for frf in frfs],axis=0)
	frf_abso = np.average([np.abs(frf) for frf in frfs],axis=0)
	frf_phas = np.arctan2(frf_imag,frf_real)
	frf_phas[frf_phas < 0] += 2*np.pi

	cross_fft = np.average(ffts.conjugate()*force_ffts,axis=0)
	fft_abso = np.average(ffts*ffts.conjugate(),axis=0)
	force_fft_abso = np.average(force_ffts*force_ffts.conjugate(),axis=0)
	coh = ((np.abs(cross_fft)**2)/(fft_abso*force_fft_abso)).real

	return(frf_real,frf_imag,frf_abso,frf_phas,coh)

def calc_peakfrfs(psds,reals,imags,force_reals,force_imags,freqs,peak_indices):

	# frf calculation for sine sweep data

	peakamps = [] # amplitude values at peaks
	peakpsds = [] # psd values at peaks
	peakfreqs = []
	frf_reals = []
	frf_imags = []
	frf_absos = []
	frf_phass = []
	cohs = []

	for psd,real,imag,freal,fimag,index in zip(psds,reals,imags,force_reals,force_imags,peak_indices):

		peakfreqs.append(freqs[index])
		peakamp = np.sum(psd[index-1:index+1+1])*np.sqrt(freqs[1]-freqs[0])
		peakamps.append(peakamp)
		peakpsds.append(psd[index])

		fft = (real + 1j * imag)[index]
		force_fft = (freal + 1j * fimag)[index]
		frf = fft / force_fft
		frf_real = frf.real
		frf_imag = frf.imag
		frf_abso = np.abs(frf)
		frf_phas = np.arctan2(frf_imag,frf_real)
		if frf_phas < 0:
			frf_phas += 2*np.pi
		cross_fft = fft.conjugate()*force_fft
		fft_abso = fft*fft.conjugate()
		force_fft_abso = force_fft*force_fft.conjugate()
		coh = ((np.abs(cross_fft)**2)/(fft_abso*force_fft_abso)).real
		frf_reals.append(frf_real)
		frf_imags.append(frf_imag)
		frf_absos.append(frf_abso)
		frf_phass.append(frf_phas)
		cohs.append(coh)

	peakfreqs = np.array(peakfreqs)
	peakamps = np.array(peakamps)
	peakpsds = np.array(peakpsds)

	frf_reals = np.array(frf_reals)
	frf_imags = np.array(frf_imags)
	frf_absos = np.array(frf_absos)
	frf_phass = np.array(frf_phass)
	cohs = np.array(cohs)

	return(peakfreqs,peakamps,peakpsds,frf_reals,frf_imags,frf_absos,frf_phass,cohs)

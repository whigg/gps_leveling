import math as mp
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import scipy.interpolate as sp


class Computations(object):

	# def __init__(self, filename):
	# 	self.data = np.genfromtxt(filename, delimiter=',')

	def read_fl(self, filename):
		self.fl = np.genfromtxt(filename, delimiter=',')

	def read_H(self, filename):
		self.H = np.genfromtxt(filename, delimiter=',')

	def read_h(self, filename):
		self.h = np.genfromtxt(filename, delimiter=',')

	def read_N(self, filename):
		self.N = np.genfromtxt(filename, delimiter=',')

	def estimation(self, method):
		"""
		Function to compute the parameters of the corrections model with
		Least Squares Estimation
		"""

		# Create the measurements vector h - H - N
		measurements = np.zeros((len(self.H), 1))
		for i in range(0, len(self.H)):
			measurements[i, 0] = self.h[i, 0] - self.H[i, 0] - self.N[i, 0]
		self.initial = measurements[:]

		# Choose the right error for the geoid heights based on the model
		# N_error = [0.0757, 0.0824, 0.0729, 0.0846, 0.0437]

		# Get the variances - errors for each point
		measur_errors = np.zeros((len(self.H), 1))
		for i in range(0, len(self.H)):
			measur_errors[i, 0] = 1/(self.h[i, 1]**2 + self.H[i, 1]**2 + self.N[i, 1]**2)

		# Create the weights matrix with the variances of each point
		weights = np.eye((len(self.H)))
		weights = weights * measur_errors


		# Create the state matrix based on the user's preference about the model
		if method == 1:
			A = np.ones((len(self.H), 3))
			A[:, 1] = self.H[:, 0]
			A[:, 2] = self.N[:, 0]
		elif method == 2:
			A = np.ones((len(self.H), 2))
			A[:, 1] = self.N[:, 0]
		elif method == 3:
			A = np.ones((len(self.H), 2))
			A[:, 1] = self.H[:, 0]

		# Compute the apriori variance estimation
		Cx_pre = np.dot(np.transpose(A), weights)
		Cx = np.linalg.inv(np.dot(Cx_pre, A))


		# Compute the estimation for the parameters of the model
		x_pre = np.dot(Cx, Cx_pre)
		x = np.dot(x_pre, measurements)

		# Create a Pandas Dataframe to hold the results
		if method == 1:
			val_pass = np.zeros((3, 2))
			val_pass[:, 0] = x[:, 0]
			val_pass[0, 1] = mp.sqrt(Cx[0, 0])
			val_pass[1, 1] = mp.sqrt(Cx[1, 1])
			val_pass[2, 1] = mp.sqrt(Cx[2, 2])
		elif method == 2 or method == 3:
			val_pass = np.zeros((2, 2))
			val_pass[:, 0] = x[:, 0]
			val_pass[0, 1] = mp.sqrt(Cx[0, 0])
			val_pass[1, 1] = mp.sqrt(Cx[1, 1])
		columns = ['Results', 'σx']
		if method == 1:
			rows = ['m', 'σΔΗ', 'σΔΝ']
		elif method == 2:
			rows = ['m', 'σΔΝ']
		elif method == 3:
			rows = ['m', 'σΔΗ']
		val_pass = pd.DataFrame(val_pass, index=rows, columns=columns)

		# Compute measurements estimation
		self.measurements_estimation = (np.dot(A, x))

		# Compute the error of the estimation
		self.error_estimation = measurements - self.measurements_estimation

		return val_pass

	def create_map(self):

		x, y = self.fl[:, 0], self.fl[:, 1]
		z = self.measurements_estimation
		X = np.linspace(np.min(x), np.max(x))
		Y = np.linspace(np.min(y), np.max(y))
		X, Y = np.meshgrid(X, Y)
		Z = sp.griddata((x, y), z, (X, Y)).reshape(50, 50)

		plt.contourf(Y, X, Z)
		plt.colorbar()
		plt.xlabel("Lon")
		plt.ylabel("Lat")
		plt.title("Correction Surface (m)")
		plt.show()


if __name__ == "__main__":

	start = Computations()
	start.read_fl("fl.csv")
	start.read_H("H.csv")
	start.read_h("h.csv")
	start.read_N("N_egm.csv")
	results = start.estimation(1)
	print(results)
	start.create_map()



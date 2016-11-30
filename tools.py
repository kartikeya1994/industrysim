def weibull(eta, beta, age):
	from random import random
	import math
	b = age**beta
	a = (1/eta)**beta
	#return b-Math.log(1-Math.random())/a, (1/p)-t0;
	return (b-math.log(1.0-random())/a)**(1.0/beta)-age

def normal(mu, sigma):
	from random import normalvariate as n
	return n(mu, sigma)

def log(msg):
	print(msg)
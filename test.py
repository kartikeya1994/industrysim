from random import random
import operator
class Test:
	def __len__(self):
		return 2
	def __init__(self):
		self.a = random()
		self.b = random()
	def __str__(self):
		return str(self.a)+' '+str(self.b)

l = []
for i in range(5):
	l += [Test()]
l.sort(key=operator.attrgetter('b'))
for e in l:
	print(e)
# a = Test()
# print(len(a))
# print(isinstance(a,Tes2t))
# raise Exception('lol')
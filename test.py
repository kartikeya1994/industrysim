# from random import random
# import operator
# class Test:
# 	def __len__(self):
# 		return 2
# 	def __init__(self):
# 		self.a = random()
# 		self.b = random()
# 	def __str__(self):
# 		return str(self.a)+' '+str(self.b)

# l = []
# for i in range(5):
# 	l += [Test()]
# l.sort(key=operator.attrgetter('b'))
# for e in l:
# 	print(e)
# a = Test()
# print(len(a))
# print(isinstance(a,Tes2t))
# raise Exception('lol')
a = [1,2,3,4,5]
for i in range(len(a)):
	if i==2:
		a.insert(i, 10)
		a.insert(i+1, 20)
		for k in range(i+2, len(a)):
			print(a[k])
		break
	else:
		print(a[i])
print(a)

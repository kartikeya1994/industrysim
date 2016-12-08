import theano
import theano.tensor as T
import numpy as np 

w = T.dmatrix('w')#theano.shared(np.array(np.random.rand(4,6), dtype=theano.config.floatX))
k = T.set_subtensor(w[:, :3], T.square(w[:,:3]))
a = np.array([[1,2,3,4,5,6],[4,5,6,1,2,5]])
fun = theano.function(inputs=[w], outputs=k)
print(fun(a))


4#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "sparseMatrix.py"
 #                                    created: 11/10/03 {3:15:38 PM} 
 #                                last update: 8/31/04 {1:38:07 PM} 
 #  Author: Jonathan Guyer
 #  E-mail: guyer@nist.gov
 #  Author: Daniel Wheeler
 #  E-mail: daniel.wheeler@nist.gov
 #    mail: NIST
 #     www: http://ctcms.nist.gov
 #  
 # ========================================================================
 # This software was developed at the National Institute of Standards
 # and Technology by employees of the Federal Government in the course
 # of their official duties.  Pursuant to title 17 Section 105 of the
 # United States Code this software is not subject to copyright
 # protection and is in the public domain.  PFM is an experimental
 # system.  NIST assumes no responsibility whatsoever for its use by
 # other parties, and makes no guarantees, expressed or implied, about
 # its quality, reliability, or any other characteristic.  We would
 # appreciate acknowledgement if the software is used.
 # 
 # This software can be redistributed and/or modified freely
 # provided that any derivative works bear some notice that they are
 # derived from it, and any modified versions bear some notice that
 # they have been modified.
 # ========================================================================
 #  
 #  Description: 
 # 
 #  History
 # 
 #  modified   by  rev reason
 #  ---------- --- --- -----------
 #  2003-11-10 JEG 1.0 original
 # ###################################################################
 ##

__docformat__ = 'restructuredtext'

import Numeric

import spmatrix

class SparseMatrix:
    
    """
    SparseMatrix class wrapper for pysparse.
    SparseMatrix is always NxN
    Allowing basic python operations __add__, __sub__ etc.
    Facilitate matrix populating in an easy way
    An example subcalls will be the identity matrix or the empty matrix.
    """

    def __init__(self, size = None, bandwidth = 0, matrix = None):
        if matrix != None:
            self.matrix = matrix
        else:
            self.matrix = spmatrix.ll_mat(size, size, size * bandwidth)
                
    def getMatrix(self):
        return self.matrix
    
    def copy(self):
	return SparseMatrix(matrix = self.matrix.copy())
	
    def __getitem__(self, index):
        m = self.matrix[index]
        if type(m) is type(0) or type(m) is type(0.):
            return m
        else:
            return SparseMatrix(matrix = m)
	
    def __str__(self):
        s = ""
        cellWidth = 11
        shape = self.getShape()
        for j in range(shape[1]):
            for i in range(shape[0]):
                v = self[j,i]
                if v == 0:
                    s += "---".center(cellWidth)
                else:
                    exp = Numeric.log(abs(v))
                    if abs(exp) <= 4:
                        if exp < 0:
                            s += ("%9.6f" % v).ljust(cellWidth)
                        else:
                            s += ("%9.*f" % (6,v)).ljust(cellWidth)
                    else:
                        s += ("%9.2e" % v).ljust(cellWidth)
            s += "\n"
        return s[:-1]
	    
    def __repr__(self):
	return repr(Numeric.array(self))
## 	return self.matrix.__repr__()
	
    def __setitem__(self, index, value):
	self.matrix[index] = value
	
    def __add__(self, other):
        """
        Add two sparse matrices
        
            >>> L = SparseMatrix(size = 3)
            >>> L.put((3.,10.,Numeric.pi,2.5), (0,0,1,2), (2,1,1,0))
            >>> print L + SparseIdentityMatrix(3)
             1.000000  10.000000   3.000000  
                ---     4.141593      ---    
             2.500000      ---     1.000000  
        """
	L = self.matrix.copy()
	L.shift(1, other.getMatrix())
	return SparseMatrix(matrix = L)

    def __sub__(self, other):
	L = self.matrix.copy()
	L.shift(-1, other.getMatrix())
	return SparseMatrix(matrix = L)

    def __mul__(self, other):
        """
        Multiply a sparse matrix by another sparse matrix
        
            >>> L1 = SparseMatrix(size = 3)
            >>> L1.put((3.,10.,Numeric.pi,2.5), (0,0,1,2), (2,1,1,0))
            >>> L2 = SparseIdentityMatrix(size = 3)
            >>> L2.put((4.38,12357.2,1.1), (2,1,0), (1,0,2))
            
            >>> print L1 * L2
             1.24e+05  23.140000   3.000000  
             3.88e+04   3.141593      ---    
             2.500000      ---     2.750000  
             
        or a sparse matrix by a vector
        
            >>> print L1 * Numeric.array((1,2,3),'d') 
            [ 29.        ,  6.28318531,  2.5       ,]
            
        or a vector by a sparse matrix
        
            >>> print Numeric.array((1,2,3),'d') * L1
            [  7.5       , 16.28318531,  3.        ,]
        """

        if type(other) == type(self):
            return SparseMatrix(matrix = spmatrix.matrixmultiply(self.matrix, other.getMatrix()))
        elif type(1) == type(other) or type(1.) == type(other):
	    N = self.matrix.shape[0]
	    L = spmatrix.ll_mat(N, N)
	    L.put(other * Numeric.ones(N))
	    return SparseMatrix(matrix = spmatrix.matrixmultiply(self.matrix, L))
	elif type(Numeric.ones(1)) == type(other):
	    y = other.copy()
	    self.matrix.matvec(other, y)
	    return y
	else:
 	    raise TypeError
            
    def __rmul__(self, other):
	if type(Numeric.ones(1)) == type(other):
	    y = other.copy()
	    self.matrix.matvec_transp(other, y)
	    return y
	else:
	    return self * other
	
    def __neg__(self):
	"""
        Negate a sparse matrix
        
            >>> print -SparseIdentityMatrix(size = 3)
            -1.000000      ---        ---    
                ---    -1.000000      ---    
                ---        ---    -1.000000  
        """
	return self * -1
	
    def __pos__(self):
	return self
	
##     def __eq__(self,other):
## 	return self.matrix.__eq__(other.getMatrix())

    def getShape(self):
        return self.matrix.shape
	
    def transpose(self):
        return self.matrix.fuckEverythingUp()

    def put(self, vector, id1, id2):
	"""
        Put elements of `vector` at positions of the matrix corresponding to (`id1`, `id2`)
        
            >>> L = SparseMatrix(size = 3)
            >>> L.put((3.,10.,Numeric.pi,2.5), (0,0,1,2), (2,1,1,0))
            >>> print L
                ---    10.000000   3.000000  
                ---     3.141593      ---    
             2.500000      ---        ---    
	"""
	self.matrix.put(vector, id1, id2)

    def putDiagonal(self, vector):
        """
        Put elements of `vector` along diagonal of matrix
        
            >>> L = SparseMatrix(size = 3)
            >>> L.putDiagonal((3.,10.,Numeric.pi))
            >>> print L
             3.000000      ---        ---    
                ---    10.000000      ---    
                ---        ---     3.141593  
            >>> L.putDiagonal((10.,3.))
            >>> print L
            10.000000      ---        ---    
                ---     3.000000      ---    
                ---        ---     3.141593  
        """
	ids = Numeric.arange(len(vector))
	self.put(vector, ids, ids)

    def take(self, id1, id2):
	vector = Numeric.zeros(len(id1), 'd')
	self.matrix.take(vector, id1, id2)
        return vector

    def takeDiagonal(self):
	ids = Numeric.arange(self.getShape()[0])
	return self.take(ids, ids)

    def addAt(self, vector, id1, id2):
	"""
        Add elements of `vector` to the positions in the matrix corresponding to (`id1`,`id2`)
        
	    >>> L = SparseMatrix(size = 3)
	    >>> L.put((3.,10.,Numeric.pi,2.5), (0,0,1,2), (2,1,1,0))
	    >>> L.addAt((1.73,2.2,8.4,3.9,1.23), (1,2,0,0,1), (2,2,0,0,2))
            >>> print L
            12.300000  10.000000   3.000000  
                ---     3.141593   2.960000  
             2.500000      ---     2.200000  
	"""
	self.matrix.update_add_at(vector, id1, id2)

    def addAtDiagonal(self, vector):
	ids = Numeric.arange(len(vector))
	self.addAt(vector, ids, ids)

    def __array__(self):
	shape = self.getShape()
	indices = Numeric.indices(shape)
	numMatrix = self.take(indices[0].flat, indices[1].flat)
	
	return Numeric.reshape(numMatrix, shape)

class SparseIdentityMatrix(SparseMatrix):
    """
    Represents a sparse identity matrix.
    """
    def __init__(self, size):
	"""
        Create a sparse matrix with '1' in the diagonal
        
            >>> print SparseIdentityMatrix(size = 3)
             1.000000      ---        ---    
                ---     1.000000      ---    
                ---        ---     1.000000  
	"""
	SparseMatrix.__init__(self, size = size, bandwidth = 1)
	ids = Numeric.arange(size)
	self.put(Numeric.ones(size), ids, ids)
	
def _test(): 
    import doctest
    return doctest.testmod()
    
if __name__ == "__main__": 
    _test() 

from bitset import *

class DP:
	"""docstring for Division_Property"""
	def __init__(self, K, blocksize):
		self.K = K
		self.blocksize_cur = self.blocksize = blocksize

	def show(self):
		print("blocksize : %d"%self.blocksize)
		if self.blocksize != self.blocksize_cur: print("blocksize_cur : %d"%self.blocksize_cur)
		print("K : ", self.K)
	
	def size_reduce(self):
		cnt = 0
		for redundantk in list(self.K):
			for k in self.K:
				if (k != redundantk)&(k&redundantk == k):
					self.K.remove(redundantk)
					cnt += 1
					break
		return cnt

	def copy(self, copyidxs, defaultReduce = True):
		""" The new copied bit based on "copy rule" is appended to the end.
		Ex)
		"""
		if not copyidxs:
			return

		if copyidxs[0]>=self.blocksize_cur:
			raise IndexError("Current block size : %d but, copy index : ("%self.blocksize_cur, copyidxs, ") out of range")

		b, n = self.blocksize_cur, len(copyidxs)

		# Copy rule : 0 -> (0,0) // 1->(1,0), (0,1) 
		for k in list(self.K):
			if ithbit(k,copyidxs[0]): # 1->(1,0), "(0,1) (added)"
				self.K.add( setbit0(setbit1(k,b),copyidxs[0]) )

		self.blocksize_cur += 1

		if defaultReduce:
			self.size_reduce()
		self.copy(copyidxs[1:], defaultReduce = defaultReduce)
		return [(copyidxs[x], b+x) for x in range(n)]

	def xor(self, xorfrom, xorinto, defaultReduce = True):
		if not xorinto:
			return

		n = len(xorfrom)
		if n != len(xorinto):
			raise ValueError("Lengths of xorfrom must equal with lengths xorinto.")
		elif n != len(set(xorfrom)):
			raise ValueError("Xorfrom must not contain duplicates.")

		elif xorfrom[0] in xorinto[1:]:
			raise ValueError("xorinto index %d is xored after it is deleted."%xorfrom[0])

		self.K = set([ delbit( setbit(k, xorinto[0], ithbit(k,xorfrom[0])|ithbit(k,xorinto[0])), xorfrom[0] ) for k in self.K if not 1&(k>>xorfrom[0])&(k>>xorinto[0])])

		if defaultReduce:
			self.size_reduce()

		self.blocksize_cur -= 1
		newxorfrom = [x-1 if x>xorfrom[0] else x for x in xorfrom[1:]]
		newxorinto = [x-1 if x>xorfrom[0] else x for x in xorinto[1:]]
		self.xor(newxorfrom, newxorinto, defaultReduce = defaultReduce)

	def sbox(self, targetidxs, sbox, defaultReduce = True):
		if sbox.inbit != len(targetidxs):
			raise ValueError("Lengths of targetidxs must equal with inbit of Sbox.")

		DPtable = sbox.get_DPT()[0]

		newK = set()
		for k in self.K:
			tablerow = sum([ithbit(k,targetidxs[i])<<i for i in range(len(targetidxs))])
			propaks = DPtable[tablerow]
			addedk = k
			for propak in propaks:
				for i in range(len(targetidxs)):
					addedk = setbit(addedk, targetidxs[i], ithbit(propak, i))
				newK.add(addedk)
		self.K = newK
		if defaultReduce:
			self.size_reduce()

	def bitperm(self, i2permi, defaultReduce = False):
		"""docstring for perm(bit - permutation) : i-th bit ==perm==> perm[i]-th bit """
		if len(i2permi) > self.blocksize_cur:
			raise IndexError("Out of index when bit - permutation")

		elif len(i2permi) < self.blocksize_cur:
			pass

		else:
			permedk = lambda bp, k: sum([1<<bp[i] for i in range(len(bp)) if ithbit(k, i)])
			self.K = set([permedk(i2permi, k) for k in self.K])




class DPTS(DP):
	"""docstring for DPT(Division Property Three Subset)"""
	def __init__(self, K, L, blocksize):
		super(DPT, self).__init__(K, blocksize)
		self.L = L
		
	def show(self):
		super().show()
		print("L : ", self.L)
		
	def size_reduce(self):
		kcnt = super().size_reduce()
		lcnt = 0
		for redundantl in list(self.L):
			for k in self.K:
				if k&redundantl == k: # l>= k
					self.L.remove(l)
					lcnt += 1
					break
		return kcnt, lcnt

	def copy(self, copyidxs, defaultReduce = True):
		""" The new copied bit based on "copy rule" is appended to the end.
		Ex)
		"""
		if copyidxs[0]>=self.blocksize_cur:
			raise IndexError("Current block size : %d but, copy index : ("%self.blocksize_cur, copyidxs, ") out of range")

		if not copyidxs:
			return

		b, n = self.blocksize_cur, len(copyidxs)

		# Copy rule : 0 -> (0,0) // 1->(1,0), (0,1) 
		for k in list(self.K):
			if ithbit(k,copyidxs[0]): # 1->(1,0), "(0,1) (added)"
				self.K.add( setbit0(setbit1(k,b),copyidxs[0]) )

		# Copy rule : 0 -> (0,0) // 1->(1,0), (0,1), (1,1)
		for l in list(self.L):
			if ithbit(l,copyidxs[0]):
				self.L.add( setbit1(l, b) ) # 1->(1,0), (0,1), "(1,1)""
				self.L.add( setbit0( setbit1(l,b), copyidxs[0]) ) # 1->(1,0), "(0,1)", (1,1) 

		self.blocksize_cur += 1

		if defaultReduce:
			self.size_reduce()
		self.copy(copyidxs[1:], defaultReduce = defaultReduce)
		return [(copyidxs[x], b+x) for x in range(n)]

	def xor(self, xorfrom, xorinto, defaultReduce = True):
		n = len(xorfrom)
		if n != len(xorinto):
			raise ValueError("Lengths of xorfrom must equal with lengths xorinto.")
		elif n != len(set(xorfrom)):
			raise ValueError("Xorfrom must not contain duplicates.")
		elif xorfrom[0] in xorinto[1:]:
			raise ValueError("xorinto index %d is xored after it is deleted."%xorfrom[0])

		if not xorinto:
			return

		# b = a1 + a2 only if b <= 1
		self.K = set([ delbit( setbit(k, xorinto[0], ithbit(k,xorfrom[0])|ithbit(k,xorinto[0])), xorfrom[0] ) for k in self.K if not 1&(k>>xorfrom[0])&(k>>xorinto[0])])

		# L xor= a1 + a2 only if (a1 + a2) <= 1
		# i.e. if a1 + a2 already exists in L, then removed. else, added.
		newL = set()
		for l in self.L:
			if not 1&(l>>xorfrom[0])&(l>>xorinto[0]): # if not a1 == a2 == 1
				newL ^= set([delbit(setbit(l, xorinto[0], ithbit(l, xorfrom[0])|ithbit(l, xorinto[0]) ), xorfromidxs[0])])
		self.L = newL

		if defaultReduce:
			self.size_reduce()

		self.blocksize_cur -= 1
		newxorfrom = [x-1 if x>xorfrom[0] else x for x in xorfrom[1:]]
		newxorinto = [x-1 if x>xorfrom[0] else x for x in xorinto[1:]]
		self.xor(newxorfrom, newxorinto, defaultReduce = defaultReduce)

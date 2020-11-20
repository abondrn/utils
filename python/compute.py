import functools


# TODO: fixed random
# TODO: web workers

class SubprocessMixin(object):
	"""Mixin for running subprocesses and capturing their output"""

	def __init__(self, verbose=False, progress=None):
		self.verbose = verbose
		self.progress = progress

	def reader(self, stream, context):
		"""
		Read lines from a subprocess' output stream and either pass to a progress
		callable (if specified) or write progress information to sys.stderr.
		"""
		progress = self.progress
		verbose = self.verbose
		while True:
			s = stream.readline()
			if not s:
				break
			if progress is not None:
				progress(s, context)
			else:
				if not verbose:
					sys.stderr.write('.')
				else:
					sys.stderr.write(s.decode('utf-8'))
				sys.stderr.flush()
		stream.close()


	def run_command(self, cmd, **kwargs):
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
							 stderr=subprocess.PIPE, **kwargs)
		t1 = threading.Thread(target=self.reader, args=(p.stdout, 'stdout'))
		t1.start()
		t2 = threading.Thread(target=self.reader, args=(p.stderr, 'stderr'))
		t2.start()
		p.wait()
		t1.join()
		t2.join()
		if self.progress is not None:
			self.progress('done.', 'main')
		elif self.verbose:
			sys.stderr.write('done.\n')
		return p


# TODO: dependencies and output
class DataCache:
	
	def __init__(self, prefix, readonly=True, **initcache):
		self.prefix = prefix
		self.readonly = readonly
		self.cache = initcache
	
	def path(self, name):
		return self.prefix+name+'.csv'
	
	def keys(self):
		return os.listdir(prefix)
	
	def __delitem__(self, name):
		if name in self.cache:
			self.invalidate_memory(name)
		if name in self:
			self.invalidate_disk(name)
	
	def invalidate_memory(self, name):
		del self.cache[name]
		
	def invalidate_disk(self, name):
		assert not self.readonly
		os.remove(self.path(name))
		
	def __contains__(self, name):
		return os.path.exists(self.path(name))
	
	# load
	def __getitem__(self, name):
		if name not in self.cache:
			self.cache[name] = pd.read_csv(self.path(name), encoding='latin-1')
		return self.cache[name]
		
	def __setitem__(self, name, df):
		assert not self.readonly
		df.to_csv(self.path(name), index=False)

from tools import weibull, normal, log
from terminaltables import AsciiTable
class MaintenanceTask:
	def __init__(self, eta=None, beta=None, age=None, fixed_cost=None,
					RF=None, labor_req=None, ttr=None):
		self.eta = eta
		self.beta = beta
		self.age = age
		self.orig_age = age
		self.fixed_cost = fixed_cost
		self.RF = RF
		self.labor_req = labor_req
		self.ttr = ttr

		self.init_vars()
		self.init_totals()
		
	def init_next_epoch(self):
		#TODO: log variables of this epoch here
		self.total_mt_jobs_done['low'] += self.mt_jobs_done['low']
		self.total_mt_jobs_done['high'] += self.mt_jobs_done['high']
		self.total_mt_jobs_done['cm'] += self.mt_jobs_done['cm']
		# self.total_mt_hours['high'] += self.mt_jobs_hours['high']
		# self.total_mt_hours['low'] += self.mt_jobs_hours['low']
		# self.total_mt_hours['cm'] += self.mt_jobs_hours['cm']
		self.total_mt_cost['high'] += self.mt_cost['high']
		self.total_mt_cost['low'] += self.mt_cost['low']
		self.total_mt_cost['cm'] += self.mt_cost['cm']

		a,b,c = self.age, self.mt_cost, self.mt_jobs_done
		self.init_vars()
		return a,b,c

	def init_vars(self):
		self.mt_jobs_done = {}
		self.mt_jobs_done['low'] = 0
		self.mt_jobs_done['high'] = 0
		self.mt_jobs_done['cm'] = 0
		# self.mt_hours['high'] = 0
		# self.mt_hours['low'] = 0
		# self.mt_hours['cm'] = 0
		self.mt_cost = {}
		self.mt_cost['high'] = 0.0
		self.mt_cost['low'] = 0.0
		self.mt_cost['cm'] = 0.0

	def init_totals(self):
		self.age = self.orig_age
		self.total_mt_jobs_done = {}
		self.total_mt_jobs_done['low'] = 0
		self.total_mt_jobs_done['high'] = 0
		self.total_mt_jobs_done['cm'] = 0
		# self.total_mt_hours['high'] = 0
		# self.total_mt_hours['low'] = 0
		# self.total_mt_hours['cm'] = 0
		self.total_mt_cost = {}
		self.total_mt_cost['high'] = 0.0
		self.total_mt_cost['low'] = 0.0
		self.total_mt_cost['cm'] = 0.0
		self.pm_scheduled = False

	def get_totals(self):
		return self.age, self.mt_jobs_done, self.total_mt_cost

	def get_labor(self, job_subtype=None):
		return self.labor_req[self.get_type_string(job_subtype)]

	def get_type_string(self, job_subtype):
		s = None
		if job_subtype is None:
			s = 'cm'
		elif job_subtype == 'HIGH':
			s = 'high'
		elif job_subtype == 'LOW':
			s = 'low'
		else:
			raise Exception('Incorrect job subtype while getting maintenance costs')
		return s

	def mt_complete(self, job_subtype):
		s = self.get_type_string(job_subtype)
		self.mt_jobs_done[s] += 1
		self.mt_cost[s] += self.fixed_cost[s]
		self.age *= (1-self.RF[s])

	def get_cm(self, epoch_length):
		ttf = weibull(self.eta, self.beta, self.age)
		# check if ttf lies in current epoch
		if not self.pm_scheduled and ttf<epoch_length:
			# not pm_scheduled is hacky, but a good enough approximation for now instead of recalculating TTFs after every PM.
			# there will be breakdown in this epoch
			return Job('CM', normal(params=self.ttr['cm']), start_time=ttf)
		else:
			return None

	def get_pm(self, subtype):
		if subtype == 'LOW':
			return Job('PM', normal(params=self.ttr['low']), job_subtype='LOW')
		elif subtype == 'HIGH':
			return Job('PM', normal(params=self.ttr['high']), job_subtype='HIGH')
		else:
			raise Exception('Bad PM type encountered while fetchign PM job')

class Machine:
	def __init__(self, name=None, compatible_jobs=None, maintenance_task=None,
					epoch_length=None):
		self.name = name
		self.compatible_jobs = compatible_jobs
		self.maintenance_task = maintenance_task
		self.epoch_length = epoch_length
		self.job_queue = JobQueue()

		self.init_vars()
		self.init_totals()

	def __cmp__(self, other):
		return cmp(len(self.job_queue), len(other.job_queue))

	def set_status(self, status):
		self.status = status

	def init_next_epoch(self):
		# runs at the end of each epoch
		self.total_time_spent['waiting'] += self.time_spent['waiting']
		self.total_time_spent['idle'] += self.time_spent['idle']
		self.total_time_spent['down'] += self.time_spent['down']
		self.total_jobs_done += self.jobs_done
		self.total_delay_cost += self.delay_cost

		age, mt_cost, mt_jobs_done = self.maintenance_task.init_next_epoch()

		epoch_result = MachineResult(self.name, age, self.time_spent, mt_cost, self.delay_cost, self.jobs_done, self.pending_jobs, mt_jobs_done)
		self.init_vars()
		self.curr_epoch += 1
		return epoch_result

	def init_vars(self):
		self.time_spent = {}
		self.time_spent['waiting'] = 0
		self.time_spent['idle'] = 0
		self.time_spent['down'] = 0
		self.jobs_done = 0
		self.delay_cost = 0.0

		self.maintenance_task.init_vars()

	def init_totals(self):
		self.total_time_spent = {}
		self.total_time_spent['waiting'] = 0
		self.total_time_spent['idle'] = 0
		self.total_time_spent['down'] = 0
		self.total_jobs_done = 0
		self.total_delay_cost = 0.0

		self.curr_epoch = 0
		self.waiting = False
		self.status = 'IDLE'

		self.maintenance_task.init_totals()

	def get_totals(self):
		age, total_mt_jobs_done, total_mt_cost = self.maintenance_task.get_totals()
		machine_result = MachineResult(self.name, age, self.total_time_spent, total_mt_cost, self.total_delay_cost, self.total_jobs_done, self.pending_jobs, total_mt_jobs_done)
		return machine_result
	
	def add_job(self, j, after=0):
		if isinstance(j, Job):
			if j.job_type == 'JOB' and j.job_subtype not in self.compatible_jobs:
				raise Exception('Job type not compatible')
			self.job_queue.append(j)
		elif j=='HIGH' or j=='LOW':
			pm_job = self.maintenance_task.get_pm(j)
			self.maintenance_task.pm_scheduled = True
			self.job_queue.append(pm_job)
		else:
			raise Exception('Job type is incorrect')

	def labor_req_met(self, curr_labor):
		# check if labor req of front job is l.e.q curr_labor
		req = self.labor_req()
		for i in range(len(req)):
			if req[i] > curr_labor[i]:
				return False
		return True

	def labor_req(self):
		# returns labor req of front job
		return self.maintenance_task.get_labor(self.front_job_subtype())

	def evaluate_breakdowns(self):
		cm_job = self.maintenance_task.get_cm(self.epoch_length)
		if cm_job is not None:
			# add CM job to schedule
			self.job_queue.append(cm_job)
	def front_job_subtype(self):
		return self.job_queue.jobs[0].job_subtype
	def front_job_type(self):
		if self.job_queue.length == 0:
			return None
		return self.job_queue.jobs[0].job_type
	def front_start_time(self):
		return self.job_queue.jobs[0].start_time
	def front_proc_time(self):
		return self.job_queue.jobs[0].proc_time
	def decrement_front_job(self, curr_time, delay_penalty):
		if self.front_job_type()=='JOB':
			# machine ages only if performing job
			self.maintenance_task.age += 1
		elif self.front_job_type() == 'PM' or self.front_job_type()=='CM':
			self.time_spent['down'] +=1

		self.job_queue.jobs[0].proc_time -= 1
		self.job_queue.length -=1
		if not self.job_queue.jobs[0].started:
			self.job_queue.jobs[0].started = True
			self.set_status(self.front_job_type())

		#handle if job is complete in this time step
		labor_release = None
		if self.front_proc_time() == 0:
			if self.front_job_type()=='JOB':
				self.jobs_done += 1
				#evaluate delay cost
				if self.job_queue[0].due_after < curr_time:
					self.delay_cost += (curr_time-self.job_queue[0].due_after)*delay_penalty
			elif self.front_job_type()=='PM' or self.front_job_type() == 'CM':
				log(self.front_job_type()+' complete')
				self.maintenance_task.pm_scheduled = False
				labor_release = self.labor_req()
				self.maintenance_task.mt_complete(self.front_job_subtype())
			#delete the completed job
			self.job_queue.jobs.pop(0)
			if len(self.job_queue)==0:
				self.set_status('IDLE')
		return labor_release
	def adjust_start_times(self, wait_release):
		prev_end_time = wait_release
		for i in range(len(self.job_queue.jobs)):
			self.job_queue.jobs[i].start_time = prev_end_time
			prev_end_time += self.job_queue.jobs[i].proc_time
	def get_leftover_jobs(self):
		leftover = []
		total_due_after = 0.0
		self.pending_jobs = 0
		#store unfinished jobs as they must be rescheduled
		unfinished_maintenance_job = None
		first = True
		for j in self.job_queue.jobs:
			if first and (j.job_type == 'PM' or j.job_type =='CM'):
				log('Leftover job: '+j.job_type)
				j.start_time = 0
				unfinished_maintenance_job = j
			elif j.job_type == 'JOB':
				j.due_after -= self.epoch_length # since next epoch starts from zero
				leftover.append(j)
				total_due_after += j.due_after
				self.pending_jobs += 1
			first = False
		self.job_queue = JobQueue()
		if unfinished_maintenance_job is not None:
			self.job_queue.append(unfinished_maintenance_job)
		return leftover, self.pending_jobs, total_due_after
	def front_started(self):
		return self.job_queue.jobs[0].started


class Job:
	def __init__(self, job_type, proc_time, due_after=None, start_time=None, job_subtype=None):
		self.job_type = job_type
		self.proc_time = proc_time
		self.due_after = due_after
		self.job_subtype = job_subtype
		self.start_time = start_time
		self.started = False
	def __str__(self):
		s = None
		if self.job_type == 'JOB':
			s = self.job_subtype
		else:
			s = self.job_type
			if self.job_subtype is not None:
				s+= '('+self.job_subtype+')'
		s+=' '+str(self.proc_time)
		return s
	def get_proc_time(self):
		return self.proc_time

class JobQueue:
	def __init__(self):
		self.length = 0
		self.jobs = []
	def __len__(self):
		return self.length
	def __getitem__(self,i):
		return self.jobs[i]
	def __str__(self):
		s = str(self.length)+' | '
		for j in self.jobs:
			s+= str(j) +' | '
		return s
	def append(self, j, after=0):
		# after param is only for PM jobs
		if not isinstance(j, Job):
			raise Exception('Non-Job member was appended to Job schedule')

		elif j.job_type == 'JOB':
			if not self.jobs:
				j.start_time = 0
			else:
				j.start_time = self.jobs[-1].start_time + self.jobs[-1].proc_time
			self.length += j.proc_time
			self.jobs.append(j)

		elif j.job_type == 'PM':
			if not self.jobs:
				# if job queue is empty
				j.start_time = after
				self.length += j.proc_time
				self.jobs.append(j)
				return j.start_time + j.proc_time
			else:
				# job queue is not empty
				for i in range(len(self.jobs)):
					if self.jobs[i].start_time >= after:
						if i>0:
							j.start_time = self.jobs[i-1].start_time + self.jobs[i-1].proc_time
						else:
							# to insert at first position
							j.start_time = 0
						self.jobs.insert(i, j)
						self.length += j.proc_time

						prev_end_time = j.start_time + j.proc_time
						#update start times of all jobs after index i
						for k in range(i+1,len(self.jobs)):
							self.jobs[k].start_time = prev_end_time 
							prev_end_time += self.jobs[k].proc_time

						return j.start_time + j.proc_time # return end time of added PM job
				# reached here implies after> start time of all jobs
				# just insert job at end of queue
				j.start_time = self.jobs[-1].start_time + self.jobs[-1].proc_time
				self.length += j.proc_time
				self.jobs.append(j)
				return j.start_time+j.proc_time

		elif j.job_type == 'CM':
			if self.length==0 or self.jobs[0].job_type != 'CM':
				log(str(self.length)+' CM time: '+ str(j.start_time))
				if self.length == 0:
					# CM is first and only job
					self.jobs.append(j)
					self.length += j.proc_time
				else:
					recalc_start_times = False
					if j.start_time == 0:
						# Add CM job at the beginning
						self.jobs.insert(0,j)
						self.length += j.proc_time
						prev_end_time = self.jobs[0].start_time + self.jobs[0].proc_time
						for k in range(1,len(self.jobs)):
							self.jobs[k].start_time = prev_end_time
							prev_end_time = self.jobs[k].start_time + self.jobs[k].proc_time
					elif j.start_time >= self.length:
						# Add CM job at the end
						self.jobs.append(j)
						self.length += j.proc_time
					else:
						# find position to insert CM job at
						for i in range(len(self.jobs)):
							start = self.jobs[i].start_time
							end = self.jobs[i].start_time + self.jobs[i].proc_time
							if start == j.start_time:
								self.jobs.insert(i,j)
								prev_end_time = self.jobs[i].start_time + self.jobs[i].proc_time
								for k in range(i+1,len(self.jobs)):
									self.jobs[k].start_time = prev_end_time
									prev_end_time = self.jobs[k].start_time + self.jobs[k].proc_time
								break
							elif start < j.start_time and j.start_time < end:
								# split this job into two at j.start_time
								#job_type, proc_time, due_after=None, start_time=None, job_subtype=None
								split1 = Job('JOB', j.start_time-start, due_after=self.jobs[i].due_after, start_time=start, job_subtype=self.jobs[i].job_subtype)
								self.jobs[i].start_time = j.start_time+j.proc_time
								self.jobs[i].proc_time -= split1.proc_time
								self.jobs.insert(i,split1)
								self.jobs.insert(i+1, j)
								self.length += j.proc_time
								# i+2 is now the second split
								#recompute start times
								prev_end_time = self.jobs[i+2].start_time + self.jobs[i+2].proc_time
								for k in range(i+3,len(self.jobs)):
									self.jobs[k].start_time = prev_end_time
									prev_end_time = self.jobs[k].start_time + self.jobs[k].proc_time
								break

class Policy:
	def __init__(self, job_sched, pm_plan):
		self.job_sched = job_sched #SJF or EDD
		self.pm_plan = pm_plan
		# dict with key as machine name on which to perform PM on
		# and value HIGH', or 'LOW' indicating the type of PM

class MachineResult:
	def __init__(self, name, age, time_spent, mt_cost, delay_cost, jobs_done, jobs_pending, mt_jobs_done):
		self.name = name
		self.age = age
		# self.time_spent = dict(time_spent)
		# self.mt_cost = dict(mt_cost)
		# self.delay_cost = delay_cost
		# self.jobs_done = jobs_done
		# self.mt_jobs_done = dict(mt_jobs_done)
		self.time_spent = (time_spent)
		self.mt_cost = (mt_cost)
		self.delay_cost = delay_cost
		self.jobs_done = jobs_done
		self.jobs_pending = jobs_pending
		self.mt_jobs_done = (mt_jobs_done)
		self.objfun = mt_cost['low'] + mt_cost['high'] + mt_cost['cm'] + delay_cost
	def __add__(self, other):
		for key in self.time_spent.keys():
			self.time_spent[key] += other.time_spent[key]
		for key in self.mt_cost.keys():
			self.mt_cost[key] += other.mt_cost[key]
		self.delay_cost += other.delay_cost
		self.jobs_done += other.jobs_done
		self.objfun += other.objfun
		return self
	@staticmethod
	def get_table_headings():
		return ['Machine', 'Age', 'ObjFun', 'Time W|D|I', 'DelayCost',  'PMHigh', 'PMLow', 'CMCost', 'JobsDone', 'JobsPend']
	def get_table_row(self):
		s = [self.name, str(self.age)]
		s.append(str(self.objfun))
		s.append(str(self.time_spent['waiting'])+'|'+str(self.time_spent['down'])+'|'+str(self.time_spent['idle']))
		s.append(str(self.delay_cost))
		s.append(str(self.mt_cost['high'])+'('+str(self.mt_jobs_done['high'])+')')
		s.append(str(self.mt_cost['low'])+'('+str(self.mt_jobs_done['low'])+')')
		s.append(str(self.mt_cost['cm'])+'('+str(self.mt_jobs_done['cm'])+')')
		s.append(str(self.jobs_done))
		s.append(str(self.jobs_pending))
		return s

class EpochResult:
	def __init__(self, epoch_num=None, machine_results=None, labor_cost=None):
		self.epoch_num = epoch_num
		self.machine_results = machine_results
		self.labor_cost = labor_cost
		self.objfun = labor_cost
		if machine_results is not None:
			for m in machine_results:
				self.objfun += m.objfun

	def __str__(self):
		data = [MachineResult.get_table_headings()]
		for m in self.machine_results:
			data.append(m.get_table_row())
		return AsciiTable(data).table
		
	def __getitem__(self, i):
		return self.machine_results[i]

	def __add__(self, other):
		if self.machine_results is None:
			return other
		for i in range(len(self.machine_results)):
			self.machine_results[i] += other.machine_results[i]
		self.objfun += other.objfun
		self.labor_cost += other.labor_cost
		return self
	def get_objfun(self):
		return self.objfun





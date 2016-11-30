from tools import weibull, normal
class MaintenanceTask:
	def __init__(self, eta, beta, age, RF_low, RF_high, cost_low, cost_high, labor_low, labor_high, ttf_low, ttf_high, cost_cm, labor_cm, ttf_cm):
		self.eta = eta
		self.beta = beta
		self.age = age
		self.RF_low=RF_low
		self.RF_high = RF_high
		self.cost_low = cost_low
		self.cost_high = cost_high
		self.labor_high = labor_high
		self.labor_low labor_low
		self.ttf_high = ttf_high #(mu,sigma)
		self.ttf_low = ttf_low #(mu,sigma)
		self.cost_cm = cost_cm
		self.labor_cm = labor_cm
		self.ttf_cm = ttf_cm #(mu,sigma)

		self.init_totals()
		self.init_next_epoch()
		
	def init_next_epoch(self):
		#TODO: log variables of this epoch here

		self.total_low_done += self.low_done
		self.total_high_done += self.high_done
		self.total_cm_done += self.cm_done
		self.total_low_hours += self.low_hours
		self.total_high_hours += self.high_hours
		self.total_cm_hours += self.cm_hours
		self.total_low_cost += self.low_cost
		self.total_high_cost += self.high_cost
		self.total_cm_cost += self.cm_cost

		self.low_done = 0
		self.high_done = 0
		self.cm_done = 0
		self.low_hours = 0
		self.high_hours = 0 
		self.cm_hours = 0
		self.low_cost = 0.0
		self.high_cost = 0.0
		self.cm_cost = 0.0
		self.pm_scheduled = False

	def init_totals(self):
		self.total_low_done = 0
		self.total_high_done = 0
		self.total_cm_done = 0
		self.total_low_hours = 0
		self.total_high_hours = 0 
		self.total_cm_hours = 0
		self.total_low_cost = 0.0
		self.total_high_cost = 0.0
		self.total_cm_cost = 0.0

	def get_cm():
		ttf = weibull(self.eta, self.beta, self.age)
		# check if ttf lies in current epoch
		if not self.pm_scheduled and ttf<self.epoch_length:
			# not pm_scheduled is hacky, but a good enough approximation for now instead of recalculating TTFs after every PM.
			# there will be breakdown in this epoch
			return Job('CM', normal(ttf_cm[0],ttf_cm[1]), start_time=ttf)
		else:
			return None

	def get_pm(self, subtype):
		if subtype == 'LOW':
			return Job('PM', normal(ttf_low[0], ttf_low[1]), job_subtype='LOW')
		elif subtype == 'HIGH':
			return Job('PM', normal(ttf_high[0], ttf_high[1], job_subtype='HIGH'))
		else:
			raise Exception('Bad PM type encountered while fetchign PM job')

class Machine:
	def __init__(self, name, eta, beta, age, compatible_jobs, maintenance_task, epoch_length):
		self.name = name
		self.compatible_jobs = compatible_jobs
		self.maintenance_task = maintenance_task
		self.epoch_length = epoch_length

		self.init_totals()
		self.init_next_epoch()

	def init_next_epoch(self):
		# must be run at the end of each epoch
		#store unfinished jobs as they must be rescheduled
		self.old_job_queue = JobQueue()
		self.unfinished_maintenance_job = None
		first = True
		for j in self.job_queue.jobs:
			if first and (j.job_type == 'PM' or j.job_type =='CM'):
				self.unfinished_maintenance_job = j
			elif j.type == 'JOB':
				self.old_job_queue.append(j)
			first = False

		self.job_queue = JobQueue()
		if self.unfinished_maintenance_job is not None:
			self.job_queue.append(unfinished_maintenance_job)

		self.status = 'IDLE'

		#TODO: log variables of this epoch here

		self.total_waiting_time += self.waiting_time
		self.total_down_time += self.down_time
		self.total_idle_time += self.idle_time
		self.total_jobs_done += self.jobs_done
		self.total_delay_cost += self.delay_cost
		self.total_proc_cost += self.proc_cost

		self.waiting_time = 0
		self.down_time = 0
		self.idle_time = 0
		self.jobs_done = 0
		self.proc_cost = 0.0
		self.delay_cost = 0.0

		self.curr_epoch += 1

		maintenance_task.init_epoch()

	def init_totals(self):
		self.total_waiting_time = 0
		self.total_down_time = 0
		self.total_idle_time = 0
		self.total_jobs_done = 0

		self.total_proc_cost = 0.0
		self.total_delay_cost = 0.0

		self.curr_epoch = 0

		self.maintenance_task.init_totals()

	def __cmp__(self, other):
    	return cmp(len(self.job_queue), len(other.job_queue))

    def add_job(self, j, after=0):
    	if isinstance(j, Job):
	    	if j.job_type == 'JOB' and j.job_subtype not in self.compatible_jobs:
				raise Exception('Job type not compatible')
			self.job_queue.append(j)
		elif j=='HIGH' or j=='LOW':
			pm_job = self.maintenance_task.get_pm(j)
			self.job_queue.append(pm_job)
		else:
			raise Exception('Job type is incorrect')

	def evaluate_breakdowns(self):
		cm_job = self.get_cm()
		if cm_job is not None:
			# add CM job to schedule
			self.job_queue.append(cm_job)


class Job:
	def __init__(self, job_type, proc_time, due_after=None, start_time=None, job_subtype=None):
		self.job_type = job_type
		self.proc_time = proc_time
		self.due_after = due_after
		self.job_subtype = job_subtype
		self.start_time = start_time
	def get_proc_time(self):
		return self.proc_time

class JobQueue:
	def __init__(self):
		self.length = 0
		self.jobs = []
	def append(self, j, after=0):
		# after param is only for PM jobs
		if after >= self.epoch_length:
			return None
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
						self.jobs[i].insert(i, j)
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
			if self.length == 0:
				# CM is first and only job
				self.jobs.append(j)
			else:
				if j.start_time == 0:
					# Add CM job at the beginning
					self.jobs.insert(0,j)
				elif j.start_time > self.length:
					# Add CM job at the end
					self.jobs.append(j)
				else:
					# find position to insert CM job at
					for i in range(len(self.jobs)):
						recalc_start_times = False
						start = self.jobs[i].start_time
						end = self.jobs[i].start_time + self.jobs[i].proc_time
						if start == j.start_time:
							self.jobs.insert(i,j)
						if start < j.start_time and j.start_time < end:
							# split this job into two at j.start_time
							#job_type, proc_time, due_after=None, start_time=None, job_subtype=None
							split1 = Job('JOB', j.start_time-start, due_after=self.jobs[i].due_after, start_time=start, job_subtype=self.jobs[i].job_subtype)
							self.jobs[i].start_time = j.start_time+j.proc_time
							self.jobs[i].proc_time -= split1.proc_time
							self.jobs.insert(i,split1)
							self.jobs.insert(i+1, j)
							# i+2 is now the second split
						#recompute start times
						prev_end_time = self.jobs[i+2].start_time + self.jobs[i+2].proc_time
						for k in range(i+3,len(self.jobs)):
							self.jobs[i+3].start_time = prev_end_time
							prev_end_time = self.jobs[i+3].start_time + self.jobs[i+3].proc_time
						break

	def __len__(self):
		return self.length

class Policy:
	def __init__(self, job_sched, pm_plan):
		self.job_sched = job_sched #SJF or EDD
		self.pm_plan = pm_plan
		# dict with key as machine name on which to perform PM on
		# and value HIGH', or 'LOW' indicating the type of PM
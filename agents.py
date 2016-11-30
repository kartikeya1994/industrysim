class MaintenanceTask:
	def __init__(self, RF_low, RF_high, 
		cost_low, cost_high, labor_low, labor_high,
		ttf_low, ttf_high, cost_cm, labor_cm, ttf_cm):
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

		self.init_variables()
		self.init_totals()

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

class Machine:
	def __init__(self, name, eta, beta, age, compatible_jobs, maintenance_task):
		self.name = name
		self.eta = eta
		self.beta = beta
		self.age = age
		self.compatible_jobs = compatible_jobs
		self.maintenance_task = maintenance_task

		self.init_variables()
		self.init_totals()

	def init_next_epoch(self):
		# must be run at the end of each epoch
		#store unfinished jobs as they must be rescheduled
		self.old_job_queue = JobQueue()
		self.unfinished_maintenance_job = None
		first = True
		for j in self.job_queue.jobs: #TODO: check if leftover job has end time > epoch end time
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

		maintenance_task.init_epoch()

	def init_totals(self):
		self.total_waiting_time = 0
		self.total_down_time = 0
		self.total_idle_time = 0
		self.total_jobs_done = 0

		self.total_proc_cost = 0.0
		self.total_delay_cost = 0.0

		self.maintenance_task.init_totals()

	def __cmp__(self, other):
    	return cmp(len(self.job_queue), len(other.job_queue))

    def add_job(self, j, after=0):
    	if isinstance(j, Job):
	    	if j.job_type == 'JOB' and j.job_subtype not in self.compatible_jobs:
				raise Exception('Job type not compatible')
			self.job_queue.append(j)
		elif j=='LOW':
			#TODO
		elif j=='HIGH':
			#TODO
		else:
			raise Exception('Job type is incorrect')

	def compute_job_start_times(self):
		self.job_queue.compute_start_times()


class Job:
	def __init__(self, job_type, proc_time, due_after, job_subtype=None):
		self.job_type = job_type
		self.proc_time = proc_time
		self.due_after = due_after
		self.job_subtype = job_subtype
		self.start_time = None
	def get_proc_time(self):
		return self.proc_time

class JobQueue:
	def __init__(self):
		self.length = 0
		self.jobs = []
	def append(self, j, after=0):
		if isinstance(j, Job): # after param does not apply for this
			raise Exception('Non-Job member was appended to Job schedule')
		if j.job_type == 'JOB':
			if not self.jobs:
				j.start_time = 0
			else:
				j.start_time = self.jobs[-1].start_time + self.jobs[-1].proc_time
			self.length += j.proc_time
			self.jobs.append(j)
		if j.job_type == 'PM':
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
	def __len__(self):
		return self.length

class Policy:
	def __init__(self, job_sched, pm_plan):
		self.job_sched = job_sched #SJF or EDD
		self.pm_plan = pm_plan
		# dict with key as machine name on which to perform PM on
		# and value HIGH', or 'LOW' indicating the type of PM
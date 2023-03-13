#ALR - AI Class
#Main
#Simulated Annealing - Traveling Salesman

#---------- IMPORT DEPENDENCIES ------------------------------+
from random import randint
from random import random
from math import exp
from math import log


#---------- MAIN ------------------------------+
class minimize():
    
    def __init__(self, func, x0, opt_mode, cooling_schedule = 'linear', step_max = 1000, temp_max =1, temp_min = 1e-5, bounds = [], alpha = None, damping = 1):
        
        
        #initalized?
        
        assert opt_mode in ['combinatorial','continuous'] 
        'opt_mode must be either "combinatorial" or "continuous"'
        
        assert cooling_schedule in ['linear','exponential','logarithmic', 'quadratic']
        'cooling_schedule can be either "linear", "exponential", "logarithmic", or "quadratic"'
        
        #initialize starting conditions
        self.temp = temp_max
        self.temp_max = temp_max
        self.temp_min = temp_min
        self.step_max = step_max
        self.opt_mode = opt_mode
        self.hist = []
        self.cooling_schedule = cooling_schedule

        self.cost_func = func
        self.x0 = x0
        self.bounds = bounds[:]
        self.damping = damping
        self.current_state = self.x0
        self.current_energy = func(self.x0)
        self.best_state = self.current_state
        self.best_energy = self.current_energy
        
        #optimization 
        
        if self.opt_mode == 'combinatorial': self.get_neighbor = self.move_combinatorial
        if self.opt_mode == 'continuous': self.get_neighbor = self.move_continuous
            
            
        #cooling schedule
        if self.cooling_schedule == 'linear':
            if alpha != None:
                self.update_temp = self.cooling_linear_m
                self.cooling_schedule = 'linear multiplicative cooling'
                self.alpha = alpha

            if alpha == None:
                self.update_temp = self.cooling_linear_a
                self.cooling_schedule = 'linear additive cooling'

        if self.cooling_schedule == 'quadratic':
            if alpha != None:
                self.update_temp = self.cooling_quadratic_m
                self.cooling_schedule = 'quadratic multiplicative cooling'
                self.alpha = alpha

            if alpha == None:
                self.update_temp = self.cooling_quadratic_a
                self.cooling_schedule = 'quadratic additive cooling'

        if self.cooling_schedule == 'exponential':
            if alpha == None: self.alpha =  0.99
            else: self.alpha = alpha
            self.update_temp = self.cooling_exponential

        if self.cooling_schedule == 'logarithmic':
            if alpha == None: self.alpha =  0.99
            else: self.alpha = alpha
            self.update_temp = self.cooling_logarithmic
            
        #optimize
        self.step, self.accept = 1, 0
        while self.step < self.step_max and self.temp >= self.temp_min and self.temp > 0:
            #get neighbor
            proposed_neighbor = self.get_neighbor()
            
            #get energy level of neighbor
            E_n = self.cost_func(proposed_neighbor)
            diffE = E_n - self.current_energy
            
            #compare energy
            if random() < self.safe_exp(-diffE / self.temp):
                self.current_energy = E_n
                self.current_state = proposed_neighbor[:]
                self.accept += 1
                
            #is neighbor best?
            if E_n < self.best_energy:
                self.best_energy = E_n
                self.best_state = proposed_neighbor[:]
                
            # update metrics
            self.hist.append([
                self.step,
                self.temp,
                self.current_energy,
                self.best_energy])

            # update temp
            self.temp = self.update_temp(self.step)
            self.step += 1

        # generate some final stats
        self.acceptance_rate = self.accept / self.step
        
    def move_continuous(self):
    # preturb current state by a random amount
        neighbor = [item + ((random() - 0.5) * self.damping) for item in self.current_state]

    # clip to upper and lower bounds
        if self.bounds:
            for i in range(len(neighbor)):
                x_min, x_max = self.bounds[i]
                neighbor[i] = min(max(neighbor[i], x_min), x_max)

        return neighbor
    
    
    def move_combinatorial(self):
        '''Swaps random nodes along path...
        '''
        p0 = randint(0, len(self.current_state)-1)
        p1 = randint(0, len(self.current_state)-1)

        neighbor = self.current_state[:]
        neighbor[p0], neighbor[p1] = neighbor[p1], neighbor[p0]

        return neighbor
        
        
    def results(self):
        print('+------------------------ RESULTS -------------------------+\n')
        print(f'      opt.mode: {self.opt_mode}')
        print(f'cooling sched.: {self.cooling_schedule}')
        if self.damping != 1: print(f'       damping: {self.damping}\n')
        else: print('\n')

        print(f'  initial temp: {self.temp_max}')
        print(f'    final temp: {self.temp:0.6f}')
        print(f'     max steps: {self.step_max}')
        print(f'    final step: {self.step}\n')

        print(f'  final energy: {self.best_energy:0.6f}\n')
        print('+-------------------------- END ---------------------------+')
        
            
            
    # linear multiplicative cooling
    def cooling_linear_m(self, step):
        return self.temp_max /  (1 + self.alpha * step)

    # linear additive cooling
    def cooling_linear_a(self, step):
        return self.temp_min + (self.temp_max - self.temp_min) * ((self.step_max - step)/self.step_max)

    # quadratic multiplicative cooling
    def cooling_quadratic_m(self, step):
        return self.temp_min / (1 + self.alpha * step**2)

    # quadratic additive cooling
    def cooling_quadratic_a(self, step):
        return self.temp_min + (self.temp_max - self.temp_min) * ((self.step_max - step)/self.step_max)**2

    # exponential multiplicative cooling
    def cooling_exponential_m(self, step):
        return self.temp_max * self.alpha**step

    # logarithmical multiplicative cooling
    def cooling_logarithmic_m(self, step):
        return self.temp_max / (self.alpha * log(step + 1))


    def safe_exp(self, x):
        try: return exp(x)
        except: return 0

#--- END ----------------------------------------------------------------------+


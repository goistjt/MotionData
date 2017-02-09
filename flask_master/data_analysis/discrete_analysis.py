'''
Created on Feb 9, 2017

@author: yangr
'''
import numpy as np

class discrete_analysis(object):
    '''
    Expect data does not have timestamp, and it is filled with correct number
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        self.derivative_filter = np.matrix('-0.5; 0; 0.5')
        self.constraints = ((-10, 10), (-10, 10), (-10, 10), (-10, 10), (-10, 10), (-10, 10))
        self.columns = 6
    
    #   At this stage, the data will drop the timestamp  
    def calculate_jerk(self, data):
        output = data[0, 1:]
        for i in range(1, data.shape[0] - 4):
            current_block = data[i:i + 3, 1:]
            jerk = np.multiply(current_block, self.derivative_filter).sum()
            output = np.vstack(output, jerk)
        return np.vstack(output, np.zeros(data.shape[1] - 1))
    
    def scaling_function(self, curmin, curmax, newmin, newmax):
        curange = curmax - curmin
        newRange = newmax - newmin
        def scale(point):
            return (point - min) / (curange) * newRange + min
        return scale
    
    def build_scaling_functions(self, data):
        output = []
        for i in range(self.columns):
            new_func = self.scaling_function(data[:,i].min(), data[:,i].max(), self.constraints[i][0], self.constraints[i][1])
            output.append(new_func)
        return output
    
    def analyze(self, data):
        new_data = self.calculate_jerk(data)
        apply_vectorized = np.vectorize(lambda f, x: f(x), otypes=[float])
        list_of_function = self.build_scaling_functions(new_data)
        return apply_vectorized(list_of_function, new_data)
    
    
    
    
     
        
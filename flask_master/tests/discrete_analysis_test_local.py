'''
Created on Jan 18, 2017

@author: yangr
'''
import unittest
import numpy as np
import numpy.testing as npt

from data_analysis import discrete_analysis

class Discrete_Test(unittest.TestCase):
    def setUp(self):
        self.discre = discrete_analysis.discrete_analysis()
        pass
     
    def test_fill_back_in_time(self):
        data = np.matrix('1 0 0 0 0 0 0; 2 0 0 0 0 0 0 ; 3 0 0 0 0 0 0; 4 4 4 4 4 4 4')
        answer = np.matrix('1 1 1 1 0 0 0; 2 2 2 2 0 0 0 ; 3 3 3 3 0 0 0; 4 4 4 4 4 4 4') 
        result = self.discre.fill_back_in_time(0, 3, 1, 4, data)
        self.assertTrue(np.alltrue(answer == result))
        answer = np.matrix('1 1 1 1 1 1 1; 2 2 2 2 2 2 2 ; 3 3 3 3 3 3 3; 4 4 4 4 4 4 4')
        result = self.discre.fill_back_in_time(0, 3, 1, 7, data)
        self.assertTrue(np.alltrue(answer == result))
          
      
    def test_fill_back_multi_row_missing_data(self):
        data = np.matrix('1 0 0 0 0 0 0; 2 0 0 0 0 0 0 ; 3 0 0 0 0 0 0; 4 4 0.5 4 0.1 4 12')
        result = np.matrix('1. 1. 0.125 1. 0.025 1. 3.; 2. 2. 0.25 2. 0.05 2. 6.; 3. 3. 0.375 3. 0.075 3. 9.; 4. 4. 0.5 4. 0.1 4. 12.')
        answer = self.discre.fill_back_in_time(0, 3, 1, 7, data)
        self.assertTrue(np.allclose(answer, result))
          
    def test_fill_forward_in_time(self):
        data = np.matrix('1 4 4.0 -4 0 0 0; 2 0 0 0 0 0 0 ; 3 0 0 0 0 0 0; 4 0 0 0 0 0 0') 
        answer = np.matrix('1. 4. 4. -4. 0. 0. 0. ; 2. 2.66666667  2.66666667 -2.66666667  0. 0. 0. ; 3. 1.33333333  1.33333333 -1.33333333  0. 0. 0. ; 4. 0. 0. -0. 0. 0. 0.')
        result = self.discre.fill_forward_in_time(1, 3, 1, 4, data)
        self.assertTrue(np.allclose(answer, result))
          
    def test_fill_forward_multi_row_missing_data(self):
        data = np.matrix( '1 4 0.5 4 0.1 4 12; 2 0 0 0 0 0 0; 3 0 0 0 0 0 0; 4 0 0 0 0 0 0')  
        answer = np.matrix('1 4. 0.5 4. 0.1 4. 12.; 2 2.667 0.333 2.667 0.067 2.667 8. ; 3 1.333 0.167 1.333 0.033 1.333 4.; 4 0. 0. 0. 0. 0. 0.')
         
        result = self.discre.fill_forward_in_time(1, 3, 1, 7, data)
        self.assertTrue(np.allclose(answer, np.round(result, 3)))
     
    def test_fill_inbetween(self):
        data = np.matrix('1 4 4.0 4 -10 1 3; 2 0 0 0 0 0 0 ; 3 0 0 0 0 0 0; 4 0 1 3 15 4 0')
        result = self.discre.fill_inbetween_time(0, 3, 1, 7, data)
        answer = np.matrix(' 1. 4. 4. 4. -10. 1. 3.; 2. 2.667 3. 3.667  -1.667 2. 2. ; 3. 1.333 2. 3.333 6.667 3. 1. ; 4. 0. 1. 3. 15. 4. 0.')
        self.assertTrue(np.allclose(answer, np.round(result, 3)))
    
    def test_fill_inbetween_multi_row_missing_data(self):
        data = np.matrix('1 4 4.0 4 -10 1 3; 2 0 0 0 0 0 0 ; 3 0 0 0 0 0 0; 4 0 1 3 15 4 0')
        result = self.discre.fill_inbetween_time(0, 3, 1, 4, data)
        answer = np.matrix(' 1. 4. 4. 4. -10. 1. 3.; 2. 2.667 3. 3.667  0 0 0 ; 3. 1.333 2. 3.333 0 0 0 ; 4. 0. 1. 3. 15. 4. 0.')
        self.assertTrue(np.allclose(answer, np.round(result, 3)))


if __name__ == "__main__":
    unittest.main()
    

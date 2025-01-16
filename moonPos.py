from jdCalc import julianCalc
import json 
import math

#override sin and cos function that accept degree
def toRadian(degree):
    return degree*math.pi/180

sin = lambda x: math.sin(toRadian(x))
cos = lambda x: math.cos(toRadian(x))


def reduceAngle(func):
    """A decorator that processes that reduce large angles into less than 360#"""
    def wrapper(self):
        y = func(self)
        return y%360
    return wrapper
    
class moonPosition:
    def __init__(self, day, month, year):
        self.T = julianCalc.compute_T(day, month, year)
        self.L = self.mean_longitude() 
        self.D = self.mean_elongation()
        self.M = self.sun_mean_anomaly()
        self.m2 = self.moon_mean_anomaly()
        self.F = self.moon_latitude_arguments()
        
        self.A1 = self.A1_func()
        self.A2 = self.A2_func()
        self.A3 = self.A3_func()
        self.E = self.compute_E()
        
        self.longitude, self.latitude, self.distance = self.import_moon_coef()
    
    def import_moon_coef(self):
        with open('coefficients.json', 'r') as file:
            data = json.load(file)
        longitude = data['moonPosition']['longitude']
        latitude = data['moonPosition']['latitude']
        distance = data['moonPosition']['distance']
        return longitude, latitude, distance
        
    @reduceAngle
    def mean_longitude(self):
        L = (218.3164477 + 481267.88123431*self.T - 0.0015786*self.T**2 + 
        self.T**3/538841 - self.T**4/65194000)
        return L 
    
    @reduceAngle
    def mean_elongation(self):
        D = (297.8501921 + 445267.1114034*self.T - 0.0018819*self.T**2
        +self.T**3/545868 - self.T**4/113065000)
        return D 
    
    @reduceAngle
    def sun_mean_anomaly(self):
        M = (357.5291092 + 35999.0502909*self.T - 0.0001536*self.T**2 + self.T**3/24490000)
        return M 
    
    @reduceAngle 
    def moon_mean_anomaly(self):
        m2 = (134.9633964+ 477198.8675055*self.T+ 0.0087414*self.T**2+ self.T**3/69699- self.T**4/14712000)
        return m2
    
    @reduceAngle
    def moon_latitude_arguments(self):
        F = 93.2720950 + 483202.0175233*self.T - 0.0036539*self.T**2 - self.T**3/3526000 + self.T**4/863310000
        return F 
    
    @reduceAngle
    def A1_func(self):
        A1  = 119.75+131.849*self.T
        return A1 
    
    @reduceAngle
    def A2_func(self):
        A2 = 53.09+ 479264.290*self.T
        return A2 
    
    @reduceAngle
    def A3_func(self):
        A3 = 313.45 + 481266.484*self.T 
        return A3
    
    def compute_E(self):
        E = 1 - 0.002516*self.T - 0.0000074*self.T 
        return E 
    
    def _compute_coef(self, coef_dataset, coef_number = None, cor_ecc = True, use_sin = True):
        sum_all = 0
        E = self.E if cor_ecc else 1
        terms = coef_number if coef_number else len(coef_dataset)
        func = sin if use_sin else cos
        
        for coef in coef_dataset[:terms]:
            param = coef[0]*self.D + coef[1]*self.M + coef[2]*self.m2 + coef[3]*self.F
            one_term = coef[4]*func(param)
            if abs(coef[1]) == 1:
                one_term*=E
            elif abs(coef[1]) == 2:
                one_term*=E**2
            sum_all += one_term
        
        return sum_all
    
    def compute_long_cor(self, coef_number = None, cor_ecc = True, cor_else = True):
        long_cor = self._compute_coef(self.longitude, coef_number, cor_ecc)
        
        if cor_else:
            long_cor += 3958*sin(self.A1)+ 1962*sin(self.L-self.F)+ 318*sin(self.A2)
        
        return long_cor
    
    def compute_dist_cor(self, coef_number = None, cor_ecc = True):
        dist_cor = self._compute_coef(self.distance, coef_number, cor_ecc, use_sin=False)
        
        return dist_cor
    
    def compute_lat_cor(self, coef_number = None, cor_ecc = True, cor_else = True):
        lat_cor = self._compute_coef(self.latitude, coef_number, cor_ecc)
        
        if cor_else:
            lat_cor += (-2235*sin(self.L) + 382*sin(self.A3) + 175*sin(self.A1-self.F) + 175*sin(self.A1+self.F) +
                            127*sin(self.L-self.m2)-115*sin(self.L+self.m2) )
        
        return lat_cor
    
    def compute_moon_coord(self, coef_number = None, cor_ecc = True, cor_else = True):
        lat_cor = self.compute_lat_cor(coef_number, cor_ecc, cor_else)
        long_cor = self.compute_long_cor(coef_number, cor_ecc, cor_else)
        dist_cor = self.compute_dist_cor(coef_number, cor_ecc)
        
        lambda_ = self.L + long_cor/1e6
        beta_ = lat_cor/1e6
        delta_ = 385000.56 + dist_cor/1e3
        
        return lambda_, beta_, delta_

mP = moonPosition(12, 4, 1992)
print(mP.compute_moon_coord())
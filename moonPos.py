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
    def wrapper(self, T):
        y = func(self, T)
        return y%360
    return wrapper
    
class moonPosition:
    def __init__(self):
        self.longitude, self.latitude, self.distance = self.import_moon_coef()
    
    def import_moon_coef(self):
        with open('coefficients.json', 'r') as file:
            data = json.load(file)
        longitude = data['moonPosition']['longitude']
        latitude = data['moonPosition']['latitude']
        distance = data['moonPosition']['distance']
        return longitude, latitude, distance
        
    @reduceAngle
    def mean_longitude(self, T):
        L = (218.3164477 + 481267.88123431*T - 0.0015786*T**2 + 
        T**3/538841 - T**4/65194000)
        return L 
    
    @reduceAngle
    def mean_elongation(self, T):
        D = (297.8501921 + 445267.1114034*T - 0.0018819*T**2
        +T**3/545868 - T**4/113065000)
        return D 
    
    @reduceAngle
    def sun_mean_anomaly(self, T):
        M = (357.5291092 + 35999.0502909*T - 0.0001536*T**2 + T**3/24490000)
        return M 
    
    @reduceAngle 
    def moon_mean_anomaly(self, T):
        m2 = (134.9633964+ 477198.8675055*T+ 0.0087414*T**2+ T**3/69699- T**4/14712000)
        return m2
    
    @reduceAngle
    def moon_latitude_arguments(self, T):
        F = 93.2720950 + 483202.0175233*T - 0.0036539*T**2 - T**3/3526000 + T**4/863310000
        return F 
    
    @reduceAngle
    def A1_func(self, T):
        A1  = 119.75+131.849*T
        return A1 
    
    @reduceAngle
    def A2_func(self, T):
        A2 = 53.09+ 479264.290*T
        return A2 
    
    @reduceAngle
    def A3_func(self, T):
        A3 = 313.45 + 481266.484*T 
        return A3
    
    def compute_E(self, T):
        E = 1 - 0.002516*T - 0.0000074*T 
        return E 
    
    def _compute_coef(self, coef_dataset, coef_number = None, use_sin = True, **kwargs):
        '''Computing Moon Position Coefficient'''
        
        D = kwargs['D']
        M = kwargs['M']
        m2 = kwargs['m2']
        F = kwargs['F']
        E = kwargs['E']
        
        sum_all = 0
        terms = coef_number if coef_number else len(coef_dataset)
        func = sin if use_sin else cos
        
        for coef in coef_dataset[:terms]:
            param = coef[0]*D + coef[1]*M + coef[2]*m2 + coef[3]*F
            one_term = coef[4]*func(param)
            if abs(coef[1]) == 1:
                one_term*=E
            elif abs(coef[1]) == 2:
                one_term*=E**2
            sum_all += one_term
        
        return sum_all
    
    def compute_long_cor(self, coef_number = None, cor_else = True, **kwargs):
        
        A1 = kwargs['A1']
        A2 = kwargs['A2']
        F = kwargs['F']
        L = kwargs['L']
        long_cor = self._compute_coef(self.longitude, coef_number, **kwargs)
        
        if cor_else:
            long_cor += 3958*sin(A1)+ 1962*sin(L-F)+ 318*sin(A2)
        
        return long_cor
    
    def compute_dist_cor(self, coef_number = None, **kwargs):
        dist_cor = self._compute_coef(self.distance, coef_number, use_sin=False, **kwargs)
        
        return dist_cor
    
    def compute_lat_cor(self, coef_number = None, cor_else = True, **kwargs):
        lat_cor = self._compute_coef(self.latitude, coef_number, **kwargs)
        A1 = kwargs['A1']
        A3 = kwargs['A3']
        F = kwargs['F']
        L = kwargs['L']
        m2 = kwargs['m2']
        
        
        if cor_else:
            lat_cor += (-2235*sin(L) + 382*sin(A3) + 175*sin(A1-F) + 175*sin(A1+F) +
                            127*sin(L-m2)-115*sin(L+m2) )
        
        return lat_cor
    
    def compute_moon_coord(self, T, coef_number = None, cor_else = True):
        L = self.mean_longitude(T)
        D = self.mean_elongation(T)
        M = self.sun_mean_anomaly(T)
        m2 = self.moon_mean_anomaly(T)
        F = self.moon_latitude_arguments(T)
        E = self.compute_E(T)
        
        A1 = self.A1_func(T)
        A2 = self.A2_func(T)
        A3 = self.A3_func(T)
        
        
        lat_cor = self.compute_lat_cor(coef_number, cor_else, L = L, D = D, M = M, m2 = m2, F = F, E = E,
                                      A1 = A1, A2 = A2, A3 = A3)
        long_cor = self.compute_long_cor(coef_number, cor_else, L = L, D = D, M = M, m2 = m2, F = F, E = E,
                                      A1 = A1, A2 = A2, A3 = A3)
        dist_cor = self.compute_dist_cor(coef_number, L = L, D = D, M = M, m2 = m2, F = F, E = E,
                                      A1 = A1, A2 = A2, A3 = A3)
        
        lambda_ = L + long_cor/1e6
        beta_ = lat_cor/1e6
        delta_ = 385000.56 + dist_cor/1e3
        
        return lambda_, beta_, delta_

T = julianCalc.compute_T(12, 4, 1992)
mP = moonPosition()
print(mP.compute_moon_coord(T))
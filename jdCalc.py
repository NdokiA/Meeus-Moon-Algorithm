
class julianCalc:
    """
    Calculates Julian Dates and T, measured in Julian centuries
    """

    @staticmethod
    def compute_JD(day: int, month: int, year: int) -> float:
        """
        Compute Julian Date of given day, month, and year in gregorian calendar

        Args:
            day (int): day in a month
            month (int): month in a year
            year (int): year

        Returns:
            JD (float): Julian dates
        """
        if month < 2:
            year -= 1; month += 12
        
        A = int(year/100)
        B = 2 - A + int(A/4)
        
        JD = int(365.25*(year+4716)) + int(30.6001*(month+1)) + day + B - 1524.5
        return JD
    
    @staticmethod
    def compute_T(day: int, month: int, year: int) -> float:
        """
        Compute time measured in Julian centuries from Epoch J2000.0

        Args:
            day (int): day in Gregorian calendar
            month (int): month in Gregorian calendar
            year (int): year in Gregorian calendar

        Returns:
            T (time, in Julian centuries)
        """        
        JDE = julianCalc.compute_JD(day, month, year)
        T = (JDE-2451545)/36525
        
        return T
        
export const julianCalc = {
    /*
    Compute the Julian Date from a Gregorian calendar date.
    @ param {number} year - The year of the date.
    @ param {number} month - The month of the date.
    @ param {number} day - The day of the date.
    @ return {number} - The Julian Date.
    */
   computeJD(year, month, day) {
    if (month < 3){
        year--;
        month += 12;
    }
    const A = Math.floor(year / 100);
    const B = 2 - A + Math.floor(A / 4);

    const JD = 
        Math.floor(365.25 * (year + 4716)) +
        Math.floor(30.6001 * (month + 1)) +
        day + B - 1524.5;
    return JD;
   },

   /*
   Compute time measured in Julian centuries from Epoch J200.0
    @ param {number} year - The year of the date.
    @ param {number} month - The month of the date.
    @ param {number} day - The day of the date.
    @ returns {number} Time in Julian centuries
   */
    computeT(year, month, day) {
    const JD = this.computeJD(year, month, day);
    const T = (JD - 2451545.0) / 36525.0;
    return T;
  }
}

// Usage
// import { julianCalc } from './julianCalc.mjs';
// const JD = julianCalc.computeJD(15, 10, 2023);
// const T = julianCalc.computeT(15, 10, 2023);

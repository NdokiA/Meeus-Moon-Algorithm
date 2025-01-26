import { on } from 'events';
import fs from 'fs';
import { julianCalc } from './julianCalc.mjs';
import { customTrig } from './radianTrig.mjs';

const data = JSON.parse(fs.readFileSync('./package/coefficients.json', 'utf-8'));
const longitudeConst = data.moonPosition.longitude;
const latitudeConst = data.moonPosition.latitude;
const distanceConst = data.moonPosition.distance;

const moonConst ={
    meanLongitude(T){
        let L = 218.3164477 + 481267.88123431*T 
                - 0.0015786*T**2 + T**3/538841 
                - T**4/65194000
        
        L = customTrig.reduceAngle(L);
        return L;
    },
    meanElongation(T){
        let D = 297.8501921 + 445267.1114034*T 
                - 0.0018819*T**2 + T**3/545868 
                - T**4/113065000
        
        D = customTrig.reduceAngle(D);
        return D;
    },
    meanSunAnomaly(T){
        let mS = 357.5291092 + 35999.0502909*T 
                - 0.0001536*T**2 + T**3/24490000
        
        mS = customTrig.reduceAngle(mS);
        return mS;
    },
    meanMoonAnomaly(T){
        let mM = 134.9633964 + 477198.8675055*T 
                + 0.0087414*T**2 + T**3/69699 
                - T**4/14712000
        
        mM = customTrig.reduceAngle(mM);
        return mM;
    },
    moonLatitudeArgument(T){
        let F = 93.2720950 + 483202.0175233*T 
                - 0.0036539*T**2 - T**3/3526000 
                + T**4/863310000
        
        F = customTrig.reduceAngle(F);
        return F;
    },
    funcA1(T){
        let A1 = 119.75 + 131.849*T;
        A1 = customTrig.reduceAngle(A1);
        return A1;
    },
    funcA2(T){
        let A2 = 53.09 + 479264.290*T;
        A2 = customTrig.reduceAngle(A2);
        return A2;
    },
    funcA3(T){
        let A3 = 313.45 + 481266.484*T;
        A3 = customTrig.reduceAngle(A3);
        return A3;
    },
    eccentricityFactor(T){
        const E = 1 - 0.002516*T - 0.0000074*T**2;
        return E;
    },
    computeCoef(T, coefDataset, coefNumber = null, useSin = true){
        const D = this.meanElongation(T);
        const mS = this.meanSunAnomaly(T);
        const mM = this.meanMoonAnomaly(T);
        const F = this.moonLatitudeArgument(T);
        const E = this.eccentricityFactor(T);

        let sumAll = 0

        const terms = coefNumber || coefDataset.length;
        const func = useSin ? customTrig.sin : customTrig.cos;

        for (const coef of coefDataset.slice(0, terms)){
            const param = coef[0]*D+coef[1]*mS+coef[2]*mM+coef[3]*F
            let oneTerm = coef[4]*func(param);

            if(Math.abs(coef[1] === 1)){
                oneTerm *= E;
            } else if (Math.abs(coef[1] === 2)){
                oneTerm *= E**2;
            }
            sumAll += oneTerm;
        }
        return sumAll;
    }
};

const moonPos = {
    computeLongitude(T, coefNumber = null){
        const A1 = moonConst.funcA1(T);
        const A2 = moonConst.funcA2(T);
        const F = moonConst.moonLatitudeArgument(T);

        let lambda = moonConst.meanLongitude(T);
        let correction = moonConst.computeCoef(T, data.moonPosition.longitude, coefNumber);
        correction += 3958*customTrig.sin(A1) + 1962*customTrig.sin(lambda-F) + 318*customTrig.sin(A2);
        
        lambda += correction/1e6;
        return lambda;
    },
    computeLatitude(T, coefNumber = null){
        let beta = moonConst.computeCoef(T, data.moonPosition.latitude, coefNumber);
        const A1 = moonConst.funcA1(T);
        const A3 = moonConst.funcA3(T);
        const F = moonConst.moonLatitudeArgument(T);
        const L = moonConst.meanLongitude(T);
        const mM = moonConst.meanMoonAnomaly(T);

        beta += -2235*customTrig.sin(L)+ 382*customTrig.sin(A3)
                +175*customTrig.sin(A1-F) + 175*customTrig.sin(A1+F)
                +127*customTrig.sin(L-mM) - 115*customTrig.sin(L+mM);
        
        return beta/1e6;
    },
    computeDistance(T, coefNumber = null){
        let delta = moonConst.computeCoef(T, data.moonPosition.distance, coefNumber, false);
        delta = 385000.56 + delta/1e3;
        return delta;
    }
}

export { moonConst, moonPos };
const radian = (degrees) => {
  return degrees * Math.PI / 180;
};

const customTrig = {
    sin(degrees) {
        return Math.sin(radian(degrees));
    },
    cos(degrees) {
        return Math.cos(radian(degrees));
    },
    reduceAngle(degrees) {
        const reduced = degrees % 360;
        return reduced < 0 ? reduced + 360 : reduced;
    }
}

export { customTrig };
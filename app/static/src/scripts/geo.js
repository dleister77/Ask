
const getCurrentLocation = () => new Promise((resolve, reject)=> {
    navigator.geolocation.getCurrentPosition(
        position => {
            resolve(position.coords);
        },
        error => {
            reject(error)
        },
        {
            enableHighAccuracy: true,
            timeout: 1 * 60 * 1000,
            maximumAge: 5 * 60 * 1000,
        }
    );
});
export {getCurrentLocation};
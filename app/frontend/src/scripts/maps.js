
import mapboxgl from 'mapboxgl';

let map;

function makeBusinessPopup(business) {
  const popup = new mapboxgl.Popup({ offset: 25 }); // add popups
  const link = new URL(`/provider/${business.name}/${business.id}`, origin);
  popup.setHTML(`
  <ul class="list-group list-group-flush text-left border-0">
      <li class="map-popup-row list-group-item py-1"><a href=${link.href}>${business.name}</a></li>
      <li class="map-popup-row list-group-item py-1">${business.categories}</li>
      <li class="map-popup-row list-group-item py-1">${business.line1}\n
                                  ${business.line2}\n
                                  ${business.city}, ${business.state_short} ${business.zip}
      </li>
      <li class="map-popup-row list-group-item py-1">
      (${business.telephone.slice(0, 3)}) ${business.telephone.slice(3, 6)}-${business.telephone.slice(6,)}
      </li>
  </ul>
              `);
  return popup;
}

function addMarkers(businessList) {
  businessList.forEach((business) => {
    const marker = new mapboxgl.Marker({
      color: 'red',
    });
    marker.setLngLat([business.longitude, business.latitude]);
    marker.setPopup(makeBusinessPopup(business));
    marker.addTo(map);
  });
}

function makeMap(mapArgs, businessList) {
  mapboxgl.accessToken = 'pk.eyJ1IjoibGVpc3RlcmJyYXUiLCJhIjoiY2s2Yzg1MTI2MTljcjNvcWJ5bTdrb2ozayJ9.qZRovROoQTGWjWl1cQqWPQ';

  const home = [mapArgs.center.longitude, mapArgs.center.latitude];

  map = new mapboxgl.Map({
    center: home,
    container: mapArgs.container,
    style: 'mapbox://styles/mapbox/streets-v11',
    zoom: 9,
  });

  const homeMarker = new mapboxgl.Marker().setLngLat(home);
  homeMarker.addTo(map);

  addMarkers(businessList);
}


export default makeMap;

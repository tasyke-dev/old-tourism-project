
    var dropdown = document.getElementsByClassName("dropdown-btn");
    var i;
    
    for (i = 0; i < dropdown.length; i++) {
      dropdown[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var dropdownContent = this.nextElementSibling;
        if (dropdownContent.style.display === "block") {
          dropdownContent.style.display = "none";
        } else {
          dropdownContent.style.display = "block";
        }
      });
    }
    
    
    
    
    $(document).ready(function () {
    const map = L.map('map_div', {
        center: [53.2007, 45.0046],
        zoom: 10
      });
    map.setView([51.2, 7], 9);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }).addTo(map);
    
    var sidebar = L.control.sidebar('side-bar', {
        closeButton: true,
        position: 'right'
    });

    var sidesidebar = L.control.sidebar('side-side-bar', {
        closeButton: true,
        position: 'right'
    });

    map.addControl(sidebar);

    //setTimeout(function () {
    //    sidebar.show();
    //}, 500);


    L.Routing.control({
        waypoints: [
            L.latLng(57.74, 11.94),
            L.latLng(57.6792, 11.949),
            L.latLng(57.65, 12)
        ]
    }).addTo(map);

    var marker999;
    var marker = L.marker([57.74, 11.94]).addTo(map).on('click', function () {
        sidebar.toggle();
        marker999 = new L.Marker([57.77, 11.94], {draggable:false});
        map.addLayer(marker999);
        marker999.bindPopup("<b>Hello world!</b><br />I am a popup.").openPopup();
    });

    var markerr = L.marker([57.6792, 11.949]).addTo(map).on('click', function () {
        sidebar.toggle();
    });


    map.on('click', function () {
        sidebar.hide();
        map.removeLayer(marker999)
    })

    const basicFoodIcon = L.icon({iconUrl: '../static/food2.svg', iconSize: [25, 25]});

    const marker1 = L.marker([-37.699450, 176.279420], {icon: basicFoodIcon}).addTo(map);
    const marker2 = L.marker([-27.643310, 153.305140]).addTo(map);
    const marker3 = L.marker([-33.956330, 122.150270]).addTo(map);
    const marker4 = L.marker([-34.962390, 117.391220]).addTo(map);
    const marker5 = L.marker([-17.961210, 122.214820]).addTo(map);
    const marker6 = L.marker([-16.505960, 151.751520]).addTo(map);
    const marker7 = L.marker([-22.594400, 167.484440]).addTo(map);
    const marker8 = L.marker([-37.977000, 177.057000]).addTo(map);
    const marker9 = L.marker([-41.037600, 173.017000]).addTo(map);
    const marker10 = L.marker([-37.670300, 176.212000]).addTo(map);
    
    
    



function addRowTable(code, coords){
    var tr = document.createElement("tr");
    var td = document.createElement("td");
    td.textContent = code;
    tr.appendChild(td);
    tr.onclick = function(){map.flyTo(coords, 17);};
    document.getElementById("t_points").appendChild(tr);
  }
  
  function addMarker(code,lat,lng){
    var p = L.marker([lat,lng]);
    p.title = code;
    p.alt = code;
    p.bindPopup(code);
    p.addTo(map);
    addRowTable(code, [lat,lng]);
  }
  
  
  $(document).ready(function (){
    var points = [["Музей",46.76336,-71.32453],
                  ["Зоопарк",46.76186,-71.32247],
                  ["Статуя",46.76489,-71.32664],
                  ["Кафе",46.76672,-71.32919]];
    for (var i=0; i < points.length; i++){
      addMarker(points[i][0],points[i][1],points[i][2]);
    }
  });
});
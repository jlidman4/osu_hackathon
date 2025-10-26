let map = L.map('map').setView([21.3, -157.8], 8);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let lineLayers = [];
let busLayers = [];

async function fetchGridData(ambient={}) {
    const response = await fetch("/grid_data", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(ambient)
    });
    return await response.json();
}

function drawGrid(data) {
    lineLayers.forEach(l => map.removeLayer(l));
    busLayers.forEach(b => map.removeLayer(b));
    lineLayers = [];
    busLayers = [];

    data.lines.forEach(line => {
        let latlngs = line.coords.map(c => [c[1], c[0]]);
        let polyline = L.polyline(latlngs, {color: line.color, weight: 4}).addTo(map);
        polyline.bindPopup(`${line.name}<br>Flow: ${line.flow.toFixed(1)} MVA<br>Rating: ${line.rating.toFixed(1)} MVA<br>Loading: ${line.loading.toFixed(1)}%`);
        lineLayers.push(polyline);
    });

    data.buses.forEach(bus => {
        let marker = L.circleMarker([bus.coords[1], bus.coords[0]], {radius:6, color:'red'}).addTo(map);
        marker.bindPopup(bus.name);
        busLayers.push(marker);
    });

    populateTable(data.table);
}

function populateTable(tableData) {
    const tbody = document.querySelector("#lineTable tbody");
    tbody.innerHTML = "";
    tableData.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.name}</td>
            <td>${row.from}</td>
            <td>${row.to}</td>
            <td>${row.load}</td>
        `;
        if (row.load >= 90) tr.style.backgroundColor = "#ffcccc";
        else if (row.load >= 70) tr.style.backgroundColor = "#fff0b3";
        else tr.style.backgroundColor = "#ccffcc";
        tbody.appendChild(tr);
    });
}

async function updateGrid() {
    let ambient = {
        Ta: parseFloat(document.getElementById('Ta').value),
        WindVelocity: parseFloat(document.getElementById('WindVelocity').value),
        SunTime: parseFloat(document.getElementById('SunTime').value)
    };
    let data = await fetchGridData(ambient);
    drawGrid(data);
}

document.getElementById('updateBtn').addEventListener('click', updateGrid);
updateGrid();

window.addEventListener('load', () => { map.invalidateSize(); });

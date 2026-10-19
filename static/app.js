let map;
let markerLayer;
let currentTab = 'ALL';
let incidentsData = [];
let unitsData = [];

// Initialize Map
function initMap() {
  try {
    const centerLat = 12.8750;
    const centerLon = 74.8520;

    map = L.map('map', {
      zoomControl: true,
      attributionControl: true
    }).setView([centerLat, centerLon], 13);

    // 100% Free OpenStreetMap Tiles - ZERO API KEY, ZERO WATERMARK!
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      className: 'osm-tactical-tiles'
    }).addTo(map);

    markerLayer = L.layerGroup().addTo(map);

    // Force map to recalculate container dimensions
    [100, 300, 800, 1500].forEach(delay => {
      setTimeout(() => {
        if (map) map.invalidateSize();
      }, delay);
    });

    window.addEventListener('resize', () => {
      if (map) map.invalidateSize();
    });

    console.log('Tactical GIS map initialized successfully.');
  } catch (err) {
    console.error('Failed to initialize Leaflet map:', err);
  }
}

// Fetch all system data
async function refreshDashboard() {
  try {
    const [statusRes, incRes, unitsRes, geoRes] = await Promise.all([
      fetch('/api/status').then(r => r.json()),
      fetch('/api/incidents?include_duplicates=false').then(r => r.json()),
      fetch('/api/units').then(r => r.json()),
      fetch('/api/geojson').then(r => r.json())
    ]);

    // Update Top Metrics
    const summary = statusRes.triage_summary || {};
    document.getElementById('metric-red').innerText = summary.RED || 0;
    document.getElementById('metric-yellow').innerText = summary.YELLOW || 0;
    document.getElementById('metric-green').innerText = summary.GREEN || 0;

    const fleet = statusRes.fleet || {};
    document.getElementById('metric-fleet').innerText = `${fleet.available_units || 0}/${fleet.total_units || 0}`;

    incidentsData = incRes.incidents || [];
    unitsData = unitsRes.units || [];

    const mobileCountEl = document.getElementById('mobile-inc-count');
    if (mobileCountEl) mobileCountEl.innerText = incidentsData.length;

    renderFeed();
    renderMap(geoRes);
  } catch (err) {
    console.error('Error fetching dashboard telemetry:', err);
  }
}

// Render Map Markers
function renderMap(geoJson) {
  markerLayer.clearLayers();

  if (!geoJson || !geoJson.features) return;

  geoJson.features.forEach(feat => {
    const [lon, lat] = feat.geometry.coordinates;
    const props = feat.properties;

    if (props.entity_type === 'INCIDENT') {
      const radius = props.triage_level === 'RED' ? 10 : 8;
      const marker = L.circleMarker([lat, lon], {
        radius: radius,
        fillColor: props.marker_color,
        color: '#ffffff',
        weight: 1.5,
        opacity: 0.9,
        fillOpacity: 0.85
      });

      const popupContent = `
        <div style="font-family: sans-serif; font-size: 12px; color: #111;">
          <strong style="color: ${props.marker_color}">[${props.triage_level}] ${props.location_name}</strong><br>
          <div style="margin: 4px 0;">Urgency Score: <strong>${props.urgency_score}%</strong></div>
          <div>Survivors: ${props.survivor_count} (Trapped: ${props.trapped_count})</div>
          <div>Status: <strong>${props.status}</strong></div>
          ${props.assigned_unit_id ? `<div style="color: #0284c7; margin-top: 4px;">Assigned: ${props.assigned_unit_id}</div>` : ''}
          <div style="margin-top: 6px;">
            <button onclick="resolveIncident('${props.id}')" style="background: #10b981; color: white; border: none; padding: 3px 8px; border-radius: 4px; cursor: pointer; font-size: 11px;">Mark Resolved</button>
          </div>
        </div>
      `;
      marker.bindPopup(popupContent);
      markerLayer.addLayer(marker);
    } else if (props.entity_type === 'RESCUE_UNIT') {
      const unitIcon = L.divIcon({
        className: 'custom-unit-icon',
        html: `<div style="background: #0284c7; color: white; border: 2px solid white; border-radius: 50%; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; box-shadow: 0 0 8px rgba(2,132,199,0.8);">U</div>`,
        iconSize: [22, 22]
      });

      const marker = L.marker([lat, lon], { icon: unitIcon });
      marker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 12px; color: #111;">
          <strong>${props.name}</strong> (${props.callsign})<br>
          Type: <strong>${props.unit_type}</strong><br>
          Status: <strong>${props.status}</strong>
        </div>
      `);
      markerLayer.addLayer(marker);
    } else if (props.entity_type === 'EVAC_ZONE') {
      const shelterIcon = L.divIcon({
        className: 'custom-shelter-icon',
        html: `<div style="background: #10b981; color: white; border: 2px solid white; border-radius: 4px; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold;">🏕️</div>`,
        iconSize: [24, 24]
      });

      const marker = L.marker([lat, lon], { icon: shelterIcon });
      marker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 12px; color: #111;">
          <strong>Shelter: ${props.name}</strong><br>
          Occupancy: ${props.occupancy} / ${props.capacity}
        </div>
      `);
      markerLayer.addLayer(marker);
    }
  });
}

// Render Sidebar Feed
function renderFeed() {
  const container = document.getElementById('incidents-feed');

  if (currentTab === 'FLEET') {
    if (!unitsData.length) {
      container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 2rem;">No units registered.</div>';
      return;
    }
    container.innerHTML = unitsData.map(u => `
      <div class="inc-card" style="border-left: 4px solid var(--cyan-accent)">
        <div class="inc-header">
          <strong style="font-size: 0.85rem;">${u.name}</strong>
          <span class="badge badge-unit">${u.status}</span>
        </div>
        <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.4rem;">
          Callsign: <span class="mono">${u.contact_callsign}</span> | Type: ${u.unit_type}
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--text-secondary);">
          <span>Fuel: <strong>${u.fuel_pct}%</strong></span>
          <span>Speed: <strong>${u.speed_kmh} km/h</strong></span>
          <span>Capacity: <strong>${u.capacity}</strong></span>
        </div>
        ${u.current_incident_id ? `<div style="margin-top: 0.4rem; font-size: 0.72rem; color: #38bdf8;">Assigned Incident: ${u.current_incident_id}</div>` : ''}
      </div>
    `).join('');
    return;
  }

  let filtered = incidentsData;
  if (currentTab !== 'ALL') {
    filtered = incidentsData.filter(inc => inc.triage_level === currentTab);
  }

  if (!filtered.length) {
    container.innerHTML = `<div style="text-align: center; color: var(--text-secondary); padding: 2rem;">No ${currentTab.toLowerCase()} incidents reported.</div>`;
    return;
  }

  container.innerHTML = filtered.map(inc => {
    const levelClass = inc.triage_level.toLowerCase();
    const hazardsHtml = (inc.hazards || []).map(h => `<span class="badge badge-hazard">${h.replace('_', ' ')}</span>`).join(' ');
    const duplicatesHtml = (inc.duplicate_reports && inc.duplicate_reports.length > 0)
      ? `<div style="font-size: 0.7rem; color: #a855f7; margin-top: 0.3rem;">⚡ Clustered ${inc.duplicate_reports.length} duplicate citizen reports</div>`
      : '';

    return `
      <div class="inc-card ${levelClass}" onclick="focusIncident(${inc.latitude}, ${inc.longitude})">
        <div class="inc-header">
          <strong style="font-size: 0.85rem;">${inc.location_name}</strong>
          <div style="display: flex; gap: 0.3rem; align-items: center;">
            <span class="badge badge-${levelClass}">${inc.triage_level}</span>
            <span class="mono" style="font-size: 0.75rem; color: var(--cyan-accent);">${inc.urgency_score}%</span>
          </div>
        </div>

        <p style="font-size: 0.78rem; color: #d1d5db; margin: 0.35rem 0; line-height: 1.35;">
          ${inc.raw_report}
        </p>

        <div style="display: flex; flex-wrap: wrap; gap: 0.3rem; margin: 0.4rem 0;">
          <span class="badge badge-unit">${inc.required_unit_type.replace('_', ' ')}</span>
          ${hazardsHtml}
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.72rem; color: var(--text-secondary); margin-top: 0.4rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.35rem;">
          <span>Survivors: <strong>${inc.survivor_count}</strong> (Trapped: ${inc.trapped_count})</span>
          <span style="font-weight: 600; color: ${inc.status === 'RESOLVED' ? '#10b981' : (inc.assigned_unit_id ? '#38bdf8' : '#f59e0b')}">
            ${inc.status} ${inc.assigned_unit_id ? `(${inc.assigned_unit_id})` : ''}
          </span>
        </div>

        ${duplicatesHtml}
      </div>
    `;
  }).join('');
}

function setTab(tab, btn) {
  currentTab = tab;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderFeed();
}

function focusIncident(lat, lon) {
  scrollToSection('map-section');
  map.flyTo([lat, lon], 15, { duration: 1.2 });
}

// Smooth scrolling between map and feed
function scrollToSection(id) {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    if (id === 'map-section') {
      setTimeout(() => { if (map) map.invalidateSize(); }, 350);
    }
  }
}

window.addEventListener('resize', () => {
  if (map) map.invalidateSize();
});

// Actions
async function triggerAutoDispatch() {
  try {
    const res = await fetch('/api/dispatch/auto', { method: 'POST' }).then(r => r.json());
    if (res.dispatches_created > 0) {
      alert(`⚡ ICS Dispatch Optimizer matched ${res.dispatches_created} rescue units to highest priority incidents!`);
    } else {
      alert('All pending critical incidents are already assigned, or no compatible units are currently available.');
    }
    refreshDashboard();
  } catch (err) {
    alert('Dispatch execution error: ' + err);
  }
}

async function resolveIncident(id) {
  try {
    await fetch(`/api/incidents/${id}/resolve`, { method: 'POST' });
    refreshDashboard();
  } catch (err) {
    console.error(err);
  }
}

async function seedScenario() {
  try {
    await fetch('/api/simulation/seed', { method: 'POST' });
    refreshDashboard();
  } catch (err) {
    alert('Error seeding scenario: ' + err);
  }
}

async function simulateMeshSync() {
  const sampleBatch = {
    sender_node_id: 'aerial-drone-relay-04',
    sent_at: Date.now() / 1000,
    incidents: [
      {
        id: 'drone-inc-' + Math.floor(Math.random() * 1000),
        latitude: 12.8790,
        longitude: 74.8476,
        location_name: 'Market Road rear alley',
        raw_report: 'Thermal camera detects 2 heat signatures trapped under slab rubble on Market Road!',
        triage_level: 'RED',
        urgency_score: 91.5,
        survivor_count: 2,
        trapped_count: 2,
        hazards: ['structural_collapse'],
        required_unit_type: 'HEAVY_SAR',
        origin_node_id: 'aerial-drone-relay-04'
      }
    ],
    unit_updates: []
  };

  try {
    const res = await fetch('/api/mesh/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(sampleBatch)
    }).then(r => r.json());

    alert(`🔄 Mesh Sync Completed:\nNode: ${res.peer_node_id}\nAdded: ${res.new_incidents_added}\nDuplicates Clustered: ${res.duplicates_clustered}`);
    refreshDashboard();
  } catch (err) {
    alert('Mesh sync simulation error: ' + err);
  }
}

// Modal handling
function openReportModal() {
  document.getElementById('report-modal').classList.add('open');
}

function closeReportModal() {
  document.getElementById('report-modal').classList.remove('open');
}

async function submitReport(e) {
  e.preventDefault();
  const payload = {
    location_name: document.getElementById('rep-location').value,
    latitude: parseFloat(document.getElementById('rep-lat').value),
    longitude: parseFloat(document.getElementById('rep-lon').value),
    raw_report: document.getElementById('rep-text').value,
    origin_node_id: 'citizen-sos-pwa'
  };

  try {
    const res = await fetch('/api/incidents', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).then(r => r.json());

    closeReportModal();
    document.getElementById('report-form').reset();
    alert(`Report Processed!\nTriage Category: ${res.incident.triage_level}\nUrgency: ${res.incident.urgency_score}%\nStatus: ${res.status}`);
    refreshDashboard();
  } catch (err) {
    alert('Failed to submit report: ' + err);
  }
}

// Initialize on DOM load or immediately if already ready
function boot() {
  initMap();
  refreshDashboard();
  setInterval(refreshDashboard, 5000);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot);
} else {
  boot();
}

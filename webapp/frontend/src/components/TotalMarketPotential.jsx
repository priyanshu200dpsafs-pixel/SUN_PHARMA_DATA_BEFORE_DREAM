import React, { useState, useMemo, useEffect } from 'react';
import Plot from 'react-plotly.js';

const QUADRANT_COLORS = {
  "Invest Now": "#10b981",
  "Harvest": "#3b82f6",
  "Emerging": "#f59e0b",
  "Watch": "#ef4444"
};

import Select from 'react-select';

// Premium Glassmorphic Styles for react-select
const selectStyles = {
  control: (provided, state) => ({
    ...provided,
    backgroundColor: '#FFFFFF',
    borderColor: state.isFocused ? '#3B82F6' : '#D1D5DB',
    boxShadow: state.isFocused ? '0 0 0 2px rgba(59, 130, 246, 0.5)' : null,
    '&:hover': { borderColor: '#9CA3AF' },
    borderRadius: '8px',
  }),
  menu: (provided) => ({
    ...provided,
    backgroundColor: '#FFFFFF',
    border: '1px solid #E5E7EB',
    zIndex: 100,
  }),
  option: (provided, state) => ({
    ...provided,
    backgroundColor: state.isFocused ? '#F3F4F6' : 'transparent',
    color: '#111827',
    cursor: 'pointer',
    '&:active': { backgroundColor: '#E5E7EB' }
  }),
  singleValue: (provided) => ({ ...provided, color: '#111827' }),
  input: (provided) => ({ ...provided, color: '#111827' }),
  placeholder: (provided) => ({ ...provided, color: '#6B7280' }),
};

export default function TotalMarketPotential({ data }) {
  const [mapMetric, setMapMetric] = useState('Overall_MAI');
  const [searchState, setSearchState] = useState('');
  const [searchDistrict, setSearchDistrict] = useState('');
  
  // Debounced Threshold Logic
  const [searchThresholdInput, setSearchThresholdInput] = useState('');
  const [searchThreshold, setSearchThreshold] = useState('');
  useEffect(() => {
    const timer = setTimeout(() => setSearchThreshold(searchThresholdInput), 300);
    return () => clearTimeout(timer);
  }, [searchThresholdInput]);

  // Dynamic Camera & Spotlight Logic
  const [mapCenter, setMapCenter] = useState({ lat: 22.0, lon: 79.0 });
  const [mapZoom, setMapZoom] = useState(3.5);
  const [spotlightDistrict, setSpotlightDistrict] = useState(null);

  useEffect(() => {
    if (searchDistrict && data && data.map_data) {
      const distStr = searchDistrict.toUpperCase();
      const match = data.map_data.find(d => d.district_name === distStr);
      if (match && match.lat && match.lon) {
        setMapCenter({ lat: match.lat, lon: match.lon });
        setMapZoom(7);
        const details = data.scatter_data.find(d => d.district_name === distStr);
        setSpotlightDistrict(details || null);
        return;
      }
    }
    setMapCenter({ lat: 22.0, lon: 79.0 });
    setMapZoom(3.5);
    setSpotlightDistrict(null);
  }, [searchDistrict, data]);

  const metrics = [
    { label: "Total Market Potential", value: "Overall_MAI" },
    { label: "Chronic Disease Burden Index", value: "Chronic_MAI" },
    { label: "Acute & Infectious Disease Index", value: "Acute_MAI" }
  ];

  // Calculate KPIs
  const kpis = useMemo(() => {
    if (!data) return null;
    const totalDists = data.scatter_data.length;
    const avgOverall = (data.scatter_data.reduce((acc, r) => acc + r.Overall_MAI, 0) / totalDists).toFixed(1);
    const investNow = data.scatter_data.filter(r => r.Quadrant === "Invest Now").length;
    return { totalDists, avgOverall, investNow };
  }, [data]);

  // Extract unique lists for Search Dropdowns
  const stateOptions = useMemo(() => {
    if (!data) return [];
    const unique = [...new Set(data.scatter_data.map(d => d.state_name))].sort();
    return unique.map(s => ({ label: s, value: s }));
  }, [data]);
  
  const districtOptions = useMemo(() => {
    if (!data) return [];
    let dists = data.scatter_data;
    if (searchState) dists = dists.filter(d => d.state_name === searchState);
    const unique = [...new Set(dists.map(d => d.district_name))].sort();
    return unique.map(d => ({ label: d, value: d }));
  }, [data, searchState]);

  // PERFORMANCE HACK: Keep array length constant to prevent WebGL mesh rebuilds.
  // We simply inject `null` for the Z value if it's filtered out!
  const optimizedZArray = useMemo(() => {
    if (!data) return [];
    return data.map_data.map(d => {
      if (d[mapMetric] === null) return null;
      if (searchState && d.state_name !== searchState.toUpperCase()) return null;
      if (searchDistrict && d.district_name !== searchDistrict.toUpperCase()) return null;
      if (searchThreshold && !isNaN(searchThreshold) && d[mapMetric] < parseFloat(searchThreshold)) return null;
      return d[mapMetric];
    });
  }, [data, mapMetric, searchState, searchDistrict, searchThreshold]);

  if (!data) return null;

  return (
    <div>
      <div className="title-bar" style={{marginBottom: '2rem'}}>
        <h1>Total Market Potential</h1>
        <p className="subtitle">National macroeconomic overview and strategic prioritization mapping.</p>
      </div>

      <div className="metric-grid">
        <div className="glass-card">
          <h3 style={{fontSize: '0.9rem'}}>Analyzed Territories</h3>
          <div className="metric-value">{kpis.totalDists}</div>
          <div className="metric-delta">Target Districts</div>
        </div>
        <div className="glass-card">
          <h3 style={{fontSize: '0.9rem'}}>Average Market Potential</h3>
          <div className="metric-value">{kpis.avgOverall}</div>
          <div className="metric-delta">National Baseline Index</div>
        </div>
        <div className="glass-card">
          <h3 style={{fontSize: '0.9rem'}}>Priority Action Zones</h3>
          <div className="metric-value" style={{color: '#10b981'}}>{kpis.investNow}</div>
          <div className="metric-delta">"Invest Now" Quadrant</div>
        </div>
      </div>

      <div className="glass-card" style={{marginBottom: '2rem', position: 'relative'}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem'}}>
          <h2>Interactive Market Attractiveness Map</h2>
          <div style={{width: '300px'}}>
            <Select
              options={metrics}
              value={metrics.find(m => m.value === mapMetric)}
              onChange={selected => setMapMetric(selected.value)}
              isSearchable={false}
              styles={selectStyles}
            />
          </div>
        </div>
        
        {/* Premium React-Select Controls */}
        <div style={{display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap', alignItems: 'flex-end'}}>
          <div style={{flex: 1, minWidth: '200px'}}>
            <label style={{display: 'block', fontSize: '0.8rem', color: '#6B7280', marginBottom: '0.2rem'}}>State Filter</label>
            <Select 
              options={stateOptions}
              value={searchState ? { label: searchState, value: searchState } : null}
              onChange={selected => {
                setSearchState(selected ? selected.value : '');
                setSearchDistrict(''); // auto clear district
              }}
              isClearable
              placeholder="Search State..."
              styles={selectStyles}
            />
          </div>
          <div style={{flex: 1, minWidth: '200px'}}>
            <label style={{display: 'block', fontSize: '0.8rem', color: '#6B7280', marginBottom: '0.2rem'}}>District Auto-Zoom</label>
            <Select 
              options={districtOptions}
              value={searchDistrict ? { label: searchDistrict, value: searchDistrict } : null}
              onChange={selected => setSearchDistrict(selected ? selected.value : '')}
              isClearable
              placeholder="Search District..."
              styles={selectStyles}
            />
          </div>
          <div style={{flex: 1}}>
            <label style={{display: 'block', fontSize: '0.8rem', color: '#6B7280', marginBottom: '0.2rem'}}>Highlight Minimum Score</label>
            <input 
              type="number"
              placeholder="e.g. 90" 
              value={searchThresholdInput} 
              onChange={e => setSearchThresholdInput(e.target.value)}
              style={{width: '100%', padding: '0.5rem', borderRadius: '8px', border: '1px solid #D1D5DB', background: '#FFFFFF', color: '#111827'}}
            />
          </div>
          <div style={{display: 'flex', alignItems: 'flex-end'}}>
             <button 
               className="btn" 
               onClick={() => {setSearchState(''); setSearchDistrict(''); setSearchThresholdInput(''); setSearchThreshold('');}}
               style={{padding: '0.5rem 1rem', background: '#F3F4F6', color: '#111827', border: '1px solid #D1D5DB', borderRadius: '8px', cursor: 'pointer'}}
             >Clear</button>
          </div>
        </div>

        <div className="map-container" style={{position: 'relative'}}>
          
          {/* Spotlight Overlay Panel */}
          {spotlightDistrict && (
            <div style={{
              position: 'absolute', top: '10px', right: '10px', zIndex: 10, width: '300px', 
              background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', 
              borderRadius: '8px', border: '1px solid #E5E7EB', padding: '1rem',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            }}>
              <h3 style={{color: '#1D4ED8', marginBottom: '0.2rem', marginTop: 0}}>{spotlightDistrict.district_name} Spotlight</h3>
              <p style={{fontSize: '0.75rem', color: '#6B7280', margin: '0 0 1rem 0'}}>Key Market Drivers</p>
              <ul style={{listStyle: 'none', padding: 0, margin: 0, fontSize: '0.85rem'}}>
                <li style={{marginBottom: '0.4rem', display: 'flex', justifyContent: 'space-between'}}>
                  <span>Total Population:</span> <b>{(spotlightDistrict.macro_population/1000000).toFixed(2)}M</b>
                </li>
                <li style={{marginBottom: '0.4rem', display: 'flex', justifyContent: 'space-between'}}>
                  <span>Health Infra (Hospitals):</span> <b>{spotlightDistrict.infra_hospitals_count}</b>
                </li>
                <li style={{marginBottom: '0.4rem', display: 'flex', justifyContent: 'space-between'}}>
                  <span>Econ Establishments:</span> <b>{spotlightDistrict.macro_economic_establishments.toLocaleString()}</b>
                </li>
                <li style={{marginBottom: '0.4rem', display: 'flex', justifyContent: 'space-between'}}>
                  <span>Diabetes Prevalence:</span> <b>{spotlightDistrict.chronic_diabetes_prevalence.toFixed(1)}%</b>
                </li>
                <li style={{marginBottom: '0.4rem', display: 'flex', justifyContent: 'space-between'}}>
                  <span>Annual Rainfall:</span> <b>{spotlightDistrict.climate_rainfall_annual_mm.toFixed(0)} mm</b>
                </li>
              </ul>
            </div>
          )}

          <Plot
            data={[
              {
                type: 'choroplethmapbox',
                geojson: data.geojson,
                locations: data.map_data.map(d => d.district_name),
                z: data.map_data.map(() => 1),
                colorscale: [[0, '#F9FAFB'], [1, '#F9FAFB']],
                showscale: false,
                hoverinfo: 'skip',
                marker: { line: { width: 0.5, color: 'rgba(0,0,0,0.1)' } }
              },
              {
                type: 'choroplethmapbox',
                geojson: data.geojson,
                locations: data.map_data.map(d => d.district_name),
                z: optimizedZArray,
                text: data.map_data.map(d => `${d.district_name} (${d.state_name})`),
                hovertemplate: '<b>%{text}</b><br>Score: %{z:.1f}<extra></extra>',
                colorscale: 'Viridis',
                zmin: 0,
                zmax: 100,
                marker: { line: { width: 0.5, color: 'rgba(0,0,0,0.1)' } }
              },
              ...(spotlightDistrict && mapCenter.lat ? [{
                type: 'scattermapbox',
                lat: [mapCenter.lat],
                lon: [mapCenter.lon],
                mode: 'markers',
                marker: { size: 16, color: '#ef4444', symbol: 'star' },
                hoverinfo: 'skip'
              }] : [])
            ]}
            layout={{
              uirevision: searchDistrict,
              mapbox: {
                style: "carto-positron",
                center: mapCenter,
                zoom: mapZoom
              },
              margin: { r: 0, t: 0, l: 0, b: 0 },
              height: 500,
              paper_bgcolor: 'rgba(0,0,0,0)',
              plot_bgcolor: 'rgba(0,0,0,0)',
              font: { color: '#374151' }
            }}
            style={{ width: '100%', height: '100%' }}
            config={{ responsive: true, displayModeBar: false }}
          />
        </div>
      </div>

      <div className="glass-card">
        <h2>Strategic Trajectory: Scale vs Momentum</h2>
        <div className="map-container">
          <Plot
            data={Object.keys(QUADRANT_COLORS).map(quadrant => {
              const quadData = data.scatter_data.filter(d => d.Quadrant === quadrant);
              return {
                type: 'scatter',
                mode: 'markers',
                name: quadrant,
                x: quadData.map(d => d.Overall_MAI),
                y: quadData.map(d => d.Momentum_Score),
                text: quadData.map(d => `${d.district_name} (${d.state_name})`),
                marker: {
                  size: quadData.map(d => Math.max(8, d.macro_population / 500000)),
                  color: QUADRANT_COLORS[quadrant],
                  opacity: 0.8,
                  line: { width: 1, color: '#FFFFFF' }
                },
                hovertemplate: '<b>%{text}</b><br>Market Potential: %{x:.1f}<br>Growth Momentum: %{y:.1f}<extra></extra>'
              };
            })}
            layout={{
              xaxis: { title: 'Total Market Potential (Scale)', gridcolor: '#E5E7EB' },
              yaxis: { title: 'Momentum Score (Growth)', gridcolor: '#E5E7EB' },
              shapes: [
                { type: 'line', x0: 50, x1: 50, y0: -20, y1: 20, line: { color: '#D1D5DB', dash: 'dash' } },
                { type: 'line', x0: 0, x1: 100, y0: 0, y1: 0, line: { color: '#D1D5DB', dash: 'dash' } }
              ],
              height: 500,
              paper_bgcolor: 'rgba(0,0,0,0)',
              plot_bgcolor: 'rgba(0,0,0,0)',
              font: { color: '#374151' },
              hovermode: 'closest'
            }}
            style={{ width: '100%', height: '100%' }}
            config={{ responsive: true, displayModeBar: false }}
          />
        </div>
      </div>
    </div>
  );
}

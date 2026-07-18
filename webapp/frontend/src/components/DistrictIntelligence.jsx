import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';
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

export default function DistrictIntelligence({ 
  scatterData, 
  selectedState, 
  setSelectedState, 
  selectedDistrict, 
  setSelectedDistrict,
  apiBase
}) {
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(false);

  // States list
  const stateOptions = useMemo(() => {
    const states = new Set(scatterData.map(d => d.state_name));
    return ["All States", ...Array.from(states).sort()].map(s => ({label: s, value: s}));
  }, [scatterData]);

  // Districts list dependent on selected state
  const districtOptions = useMemo(() => {
    let filtered = scatterData;
    if (selectedState !== "All States") {
      filtered = scatterData.filter(d => d.state_name === selectedState);
    }
    return filtered
      .map(d => `${d.district_name} (${d.state_name})`)
      .sort((a,b) => a.localeCompare(b))
      .map(d => ({label: d, value: d}));
  }, [scatterData, selectedState]);

  // Handle Dropdown Sync
  const handleStateChange = (selectedOption) => {
    if (!selectedOption) return;
    const newState = selectedOption.value;
    setSelectedState(newState);
    if (newState !== "All States") {
      const firstDist = scatterData
        .filter(d => d.state_name === newState)
        .sort((a,b) => a.district_name.localeCompare(b.district_name))[0];
      setSelectedDistrict(`${firstDist.district_name} (${firstDist.state_name})`);
    }
  };

  const handleDistrictChange = (selectedOption) => {
    if (!selectedOption) return;
    const newDist = selectedOption.value;
    setSelectedDistrict(newDist);
    // Auto-update state
    const actualState = newDist.split(" (")[1].replace(")", "");
    setSelectedState(actualState);
  };

  // Fetch details when district changes
  useEffect(() => {
    if (!selectedDistrict) return;
    
    const fetchDetails = async () => {
      setLoading(true);
      const distName = selectedDistrict.split(" (")[0];
      const stateName = selectedDistrict.split(" (")[1].replace(")", "");
      try {
        const res = await axios.get(`${apiBase}/district/${stateName}/${distName}`);
        setDetails(res.data);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    };
    
    fetchDetails();
  }, [selectedDistrict, apiBase]);

  return (
    <div>
      <div className="title-bar" style={{marginBottom: '2rem'}}>
        <h1>District Intelligence Profile</h1>
        <p className="subtitle">Micro-level diagnostics and machine-learning interpretability.</p>
      </div>

      <div className="glass-card" style={{marginBottom: '2rem'}}>
        <div style={{display: 'flex', gap: '1rem'}}>
          <div style={{flex: 1}}>
            <label style={{color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '8px', display: 'block'}}>State/UT</label>
            <Select 
              options={stateOptions}
              value={stateOptions.find(o => o.value === selectedState)}
              onChange={handleStateChange}
              styles={selectStyles}
            />
          </div>
          <div style={{flex: 1}}>
            <label style={{color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '8px', display: 'block'}}>Search District</label>
            <Select 
              options={districtOptions}
              value={districtOptions.find(o => o.value === selectedDistrict)}
              onChange={handleDistrictChange}
              styles={selectStyles}
            />
          </div>
        </div>
      </div>

      {loading && (
        <div style={{textAlign: 'center', padding: '3rem', color: 'var(--text-accent)'}}>
          <div className="spinner" style={{margin: '0 auto', width: '30px', height: '30px'}}></div>
          <p style={{marginTop: '1rem'}}>Aggregating Intelligence...</p>
        </div>
      )}

      {!loading && details && (
        <>
          <div className="metric-grid">
            <div className="glass-card">
              <h3 style={{fontSize: '0.9rem'}}>Total Market Potential</h3>
              <div className="metric-value">{details.metrics.Overall_MAI.toFixed(1)}</div>
              <div className={`metric-delta ${details.gap_score > 0 ? 'positive' : 'negative'}`}>
                {details.gap_score.toFixed(1)} Unmet Infra Gap
              </div>
            </div>
            <div className="glass-card">
              <h3 style={{fontSize: '0.9rem'}}>Chronic Burden</h3>
              <div className="metric-value">{details.metrics.Chronic_MAI.toFixed(1)}</div>
            </div>
            <div className="glass-card">
              <h3 style={{fontSize: '0.9rem'}}>Acute Burden</h3>
              <div className="metric-value">{details.metrics.Acute_MAI.toFixed(1)}</div>
            </div>
          </div>

          <div className="glass-card" style={{marginBottom: '2rem', display: 'flex', gap: '2rem'}}>
            <div style={{flex: 1}}>
              <h3 style={{marginBottom: '0.5rem'}}>Confidence Tier</h3>
              <span className={`badge badge-${details.metrics.confidence_tier.toLowerCase()}`}>
                {details.metrics.confidence_tier}
              </span>
            </div>
            <div style={{flex: 1}}>
              <h3 style={{marginBottom: '0.5rem'}}>Market Strategy Quadrant</h3>
              <span className={`badge badge-${details.metrics.Quadrant.toLowerCase().replace(' ', '-')}`}>
                {details.metrics.Quadrant}
              </span>
            </div>
          </div>

          <div className="glass-card">
            <h2>Machine Learning Insights</h2>
            {details.explanation ? (
              <div style={{background: 'rgba(59, 130, 246, 0.1)', borderLeft: '4px solid #3B82F6', padding: '1rem', borderRadius: '4px', marginBottom: '1.5rem', color: '#111827', lineHeight: 1.5}}>
                💡 {details.explanation}
              </div>
            ) : (
              <div style={{background: '#F9FAFB', padding: '1rem', borderRadius: '4px', marginBottom: '1.5rem', color: '#6B7280'}}>
                💡 Intelligence narrative generated only for top market movers.
              </div>
            )}

            {details.shap_features.length > 0 && (
              <div className="map-container" style={{padding: '1rem'}}>
                <Plot
                  data={[
                    {
                      type: 'bar',
                      orientation: 'h',
                      x: details.shap_features.map(f => f.Impact),
                      y: details.shap_features.map(f => f.Feature),
                      marker: {
                        color: details.shap_features.map(f => f.Impact),
                        colorscale: 'Viridis'
                      }
                    }
                  ]}
                  layout={{
                    title: 'XGBoost Feature Drivers',
                    margin: { l: 200, r: 20, t: 40, b: 40 },
                    height: 400,
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: { color: '#374151' },
                    xaxis: { gridcolor: '#E5E7EB' },
                    yaxis: { automargin: true }
                  }}
                  style={{ width: '100%', height: '100%' }}
                  config={{ responsive: true, displayModeBar: false }}
                />
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

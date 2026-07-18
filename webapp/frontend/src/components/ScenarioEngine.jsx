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

export default function ScenarioEngine({ scatterData, apiBase }) {
  const [selectedDistrict, setSelectedDistrict] = useState(
    scatterData.length > 0 ? `${scatterData[0].district_name} (${scatterData[0].state_name})` : ''
  );
  
  const [shocks, setShocks] = useState({
    pop_growth: 0,
    emp_growth: 0,
    est_growth: 0,
    dia_growth: 0
  });

  const [simResult, setSimResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const districtOptions = useMemo(() => {
    return scatterData
      .map(d => `${d.district_name} (${d.state_name})`)
      .sort((a,b) => a.localeCompare(b))
      .map(d => ({ label: d, value: d }));
  }, [scatterData]);

  // Run Simulation
  useEffect(() => {
    if (!selectedDistrict) return;

    const runSimulation = async () => {
      setLoading(true);
      const distName = selectedDistrict.split(" (")[0];
      const stateName = selectedDistrict.split(" (")[1].replace(")", "");
      
      try {
        const res = await axios.post(`${apiBase}/simulate`, {
          state_name: stateName,
          dist_name: distName,
          ...shocks
        });
        setSimResult(res.data);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    };

    // Debounce slider updates slightly
    const timeoutId = setTimeout(() => {
      runSimulation();
    }, 300);
    
    return () => clearTimeout(timeoutId);
  }, [selectedDistrict, shocks, apiBase]);

  const handleSlider = (e) => {
    setShocks({
      ...shocks,
      [e.target.name]: parseFloat(e.target.value)
    });
  };

  return (
    <div>
      <div className="title-bar" style={{marginBottom: '2rem'}}>
        <h1>Strategic Scenario Engine</h1>
        <p className="subtitle">Stress-test the XGBoost intelligence model by simulating macroeconomic shocks.</p>
      </div>

      <div className="glass-card" style={{marginBottom: '2rem'}}>
        <label style={{color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '8px', display: 'block'}}>Select Target Market</label>
        <Select 
          options={districtOptions}
          value={districtOptions.find(o => o.value === selectedDistrict)}
          onChange={selectedOption => {
            if (selectedOption) setSelectedDistrict(selectedOption.value);
          }}
          styles={selectStyles}
        />
      </div>

      <div style={{display: 'flex', gap: '2rem', flexWrap: 'wrap'}}>
        {/* Sliders */}
        <div className="glass-card" style={{flex: '1 1 300px'}}>
          <h2 style={{marginBottom: '1.5rem'}}>Market Shocks</h2>
          
          <div style={{marginBottom: '1.5rem'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem'}}>
              <label>Population Growth</label>
              <span style={{color: 'var(--text-accent)'}}>{shocks.pop_growth > 0 ? '+' : ''}{shocks.pop_growth}%</span>
            </div>
            <input type="range" name="pop_growth" min="-50" max="150" value={shocks.pop_growth} onChange={handleSlider} />
          </div>

          <div style={{marginBottom: '1.5rem'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem'}}>
              <label>Economic Employees Growth</label>
              <span style={{color: 'var(--text-accent)'}}>{shocks.emp_growth > 0 ? '+' : ''}{shocks.emp_growth}%</span>
            </div>
            <input type="range" name="emp_growth" min="-50" max="150" value={shocks.emp_growth} onChange={handleSlider} />
          </div>

          <div style={{marginBottom: '1.5rem'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem'}}>
              <label>Economic Establishments Growth</label>
              <span style={{color: 'var(--text-accent)'}}>{shocks.est_growth > 0 ? '+' : ''}{shocks.est_growth}%</span>
            </div>
            <input type="range" name="est_growth" min="-50" max="150" value={shocks.est_growth} onChange={handleSlider} />
          </div>

          <div style={{marginBottom: '1.5rem'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem'}}>
              <label>Diabetes Prevalence Shift</label>
              <span style={{color: 'var(--text-accent)'}}>{shocks.dia_growth > 0 ? '+' : ''}{shocks.dia_growth}%</span>
            </div>
            <input type="range" name="dia_growth" min="-5" max="5" step="0.1" value={shocks.dia_growth} onChange={handleSlider} />
          </div>
          
          <button 
            style={{width: '100%', padding: '12px', background: '#F3F4F6', border: '1px solid #D1D5DB', borderRadius: '8px', color: '#111827', cursor: 'pointer', marginTop: '1rem', fontWeight: '500'}}
            onClick={() => setShocks({pop_growth: 0, emp_growth: 0, est_growth: 0, dia_growth: 0})}
          >
            Reset Scenarios
          </button>
        </div>

        {/* Results */}
        <div className="glass-card" style={{flex: '2 1 400px', display: 'flex', flexDirection: 'column'}}>
          <h2>Simulation Outcomes</h2>
          
          {loading && !simResult ? (
            <div className="loader-container" style={{height: '200px'}}><div className="spinner"></div></div>
          ) : simResult ? (
            <>
              <div className="metric-grid" style={{marginBottom: '1rem'}}>
                <div style={{background: '#FFFFFF', padding: '1rem', borderRadius: '8px', border: '1px solid #E5E7EB', boxShadow: '0 1px 2px rgba(0,0,0,0.05)'}}>
                  <h3 style={{fontSize: '0.85rem'}}>Projected Infra Requirement</h3>
                  <div className="metric-value">{simResult.sim_pred.toFixed(1)}</div>
                  <div className={`metric-delta ${simResult.sim_pred - simResult.base_pred > 0 ? 'positive' : 'negative'}`}>
                    {(simResult.sim_pred - simResult.base_pred).toFixed(1)} vs Baseline
                  </div>
                </div>
                
                <div style={{background: '#FFFFFF', padding: '1rem', borderRadius: '8px', border: '1px solid #E5E7EB', boxShadow: '0 1px 2px rgba(0,0,0,0.05)'}}>
                  <h3 style={{fontSize: '0.85rem'}}>Unmet Supply Gap</h3>
                  <div className="metric-value">{simResult.sim_unmet_need.toFixed(1)}</div>
                  <div className="metric-delta">Actual Existing: {simResult.actual_infra.toFixed(1)}</div>
                </div>
              </div>

              <div className="map-container" style={{flex: 1, minHeight: '300px'}}>
                <Plot
                  data={[
                    {
                      type: 'bar',
                      x: ['Actual Existing', 'Baseline ML', 'Simulated Need'],
                      y: [simResult.actual_infra, simResult.base_pred, simResult.sim_pred],
                      text: [simResult.actual_infra.toFixed(1), simResult.base_pred.toFixed(1), simResult.sim_pred.toFixed(1)],
                      textposition: 'auto',
                      marker: {
                        color: ['#440154', '#21918c', '#5ec962']
                      }
                    }
                  ]}
                  layout={{
                    margin: { l: 40, r: 20, t: 40, b: 40 },
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: { color: '#374151' },
                    yaxis: { gridcolor: '#E5E7EB' }
                  }}
                  style={{ width: '100%', height: '100%' }}
                  config={{ responsive: true, displayModeBar: false }}
                />
              </div>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}

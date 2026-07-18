import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LayoutDashboard, Map, BarChart3, Database } from 'lucide-react';
import TotalMarketPotential from './components/TotalMarketPotential';
import DistrictIntelligence from './components/DistrictIntelligence';
import ScenarioEngine from './components/ScenarioEngine';
import DataExplorer from './components/DataExplorer';

// Nuke lingering Streamlit Service Workers that break XHR requests
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(function(registrations) {
    for(let registration of registrations) {
      registration.unregister();
    }
  });
}

// Global axios defaults to bypass tunnel warnings for API calls
axios.defaults.headers.common['ngrok-skip-browser-warning'] = '69420';
axios.defaults.headers.common['Bypass-Tunnel-Reminder'] = 'true';

const API_BASE = '/api';

function App() {
  const [activeTab, setActiveTab] = useState('Overview');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [loadingPhase, setLoadingPhase] = useState('Connecting to server...');

  // Global State for Selections (for two-way sync across views)
  const [selectedState, setSelectedState] = useState('All States');
  const [selectedDistrict, setSelectedDistrict] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoadingPhase('Connecting to server...');
        // Quick ping to confirm server is alive before the heavy payload
        await axios.get(`${API_BASE}/ping`);
        
        setLoadingPhase('Downloading map intelligence data...');
        const res = await axios.get(`${API_BASE}/dashboard_data`);
        
        setLoadingPhase('Rendering dashboard...');
        setData(res.data);
        
        // Auto-select first district
        if (res.data.scatter_data.length > 0) {
          const firstDist = res.data.scatter_data.sort((a,b) => a.district_name.localeCompare(b.district_name))[0];
          setSelectedDistrict(`${firstDist.district_name} (${firstDist.state_name})`);
        }
        
        setLoading(false);
      } catch (err) {
        console.error("Failed to load data", err);
        setError("Failed to load dashboard data. Ensure backend is running.");
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="loader-container">
        <div className="spinner"></div>
        <h3 style={{color: 'var(--text-accent)', marginTop: '1rem'}}>{loadingPhase}</h3>
        <p style={{color: '#9ca3af', fontSize: '0.85rem', marginTop: '0.5rem'}}>This may take a moment on first load</p>
      </div>
    );
  }

  if (error) {
    return <div className="loader-container"><h2 style={{color: 'red'}}>{error}</h2></div>;
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'Overview':
        return <TotalMarketPotential data={data} />;
      case 'District':
        return <DistrictIntelligence 
          scatterData={data.scatter_data} 
          selectedState={selectedState}
          setSelectedState={setSelectedState}
          selectedDistrict={selectedDistrict}
          setSelectedDistrict={setSelectedDistrict}
          apiBase={API_BASE}
        />;
      case 'Simulator':
        return <ScenarioEngine 
          scatterData={data.scatter_data}
          apiBase={API_BASE}
        />;
      case 'Explorer':
        return <DataExplorer scatterData={data.scatter_data} />;
      default:
        return null;
    }
  };

  return (
    <div className="app-container">
      {/* SIDEBAR */}
      <nav className="sidebar">
        <div style={{marginBottom: '2rem', padding: '0 10px'}}>
          <h2 style={{fontSize: '1.2rem', color: '#fff', marginBottom: '4px'}}>Sun Pharma</h2>
          <h3 style={{fontSize: '0.8rem', color: 'var(--text-accent)'}}>Market Attractiveness Platform</h3>
        </div>
        
        <button className={`nav-item ${activeTab === 'Overview' ? 'active' : ''}`} onClick={() => setActiveTab('Overview')}>
          <LayoutDashboard size={20} />
          Total Market Potential
        </button>
        <button className={`nav-item ${activeTab === 'District' ? 'active' : ''}`} onClick={() => setActiveTab('District')}>
          <Map size={20} />
          District Intelligence
        </button>
        <button className={`nav-item ${activeTab === 'Simulator' ? 'active' : ''}`} onClick={() => setActiveTab('Simulator')}>
          <BarChart3 size={20} />
          Strategic Scenarios
        </button>
        <button className={`nav-item ${activeTab === 'Explorer' ? 'active' : ''}`} onClick={() => setActiveTab('Explorer')}>
          <Database size={20} />
          Data Explorer
        </button>
      </nav>

      {/* MAIN CONTENT */}
      <main className="main-content">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;

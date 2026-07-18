import React, { useState } from 'react';

export default function DataExplorer({ scatterData }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortConfig, setSortConfig] = useState({ key: 'Overall_MAI', direction: 'desc' });

  // Use the same subset as Streamlit
  const columns = [
    { key: 'state_name', label: 'State/UT' },
    { key: 'district_name', label: 'District Name' },
    { key: 'Overall_MAI', label: 'Total Market Potential (Overall MAI)', isNumeric: true },
    { key: 'Chronic_MAI', label: 'Chronic Burden', isNumeric: true },
    { key: 'Acute_MAI', label: 'Acute Burden', isNumeric: true },
    { key: 'Momentum_Score', label: 'Momentum Score', isNumeric: true },
    { key: 'Quadrant', label: 'Market Strategy' },
    { key: 'macro_population', label: 'Population', isNumeric: true }
  ];

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const sortedData = [...scatterData].sort((a, b) => {
    if (a[sortConfig.key] < b[sortConfig.key]) {
      return sortConfig.direction === 'asc' ? -1 : 1;
    }
    if (a[sortConfig.key] > b[sortConfig.key]) {
      return sortConfig.direction === 'asc' ? 1 : -1;
    }
    return 0;
  });

  const filteredData = sortedData.filter(d => 
    d.state_name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    d.district_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.Quadrant.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const downloadCSV = () => {
    const headers = columns.map(c => c.key).join(',');
    const rows = filteredData.map(d => columns.map(c => d[c.key]).join(',')).join('\n');
    const csv = `${headers}\n${rows}`;
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sun_pharma_intelligence_export.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div className="title-bar" style={{marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'}}>
        <div>
          <h1>Data Explorer & Export</h1>
          <p className="subtitle">Raw intelligence repository for offline analysis.</p>
        </div>
        <button 
          onClick={downloadCSV}
          style={{padding: '12px 24px', background: '#1D4ED8', border: 'none', borderRadius: '8px', color: '#FFFFFF', fontWeight: '600', cursor: 'pointer', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}}
        >
          Export CSV
        </button>
      </div>

      <div className="glass-card" style={{marginBottom: '1rem'}}>
        <input 
          type="text" 
          placeholder="Search by District, State, or Strategy Quadrant..." 
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="glass-card" style={{padding: 0, overflowX: 'auto'}}>
        <table style={{minWidth: '1000px'}}>
          <thead>
            <tr>
              {columns.map(col => (
                <th 
                  key={col.key} 
                  style={{cursor: 'pointer', whiteSpace: 'nowrap'}}
                  onClick={() => handleSort(col.key)}
                >
                  {col.label} {sortConfig.key === col.key ? (sortConfig.direction === 'asc' ? '↑' : '↓') : ''}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredData.map((row, i) => (
              <tr key={i}>
                {columns.map(col => (
                  <td key={col.key}>
                    {col.isNumeric ? 
                      (col.key === 'macro_population' ? row[col.key].toLocaleString() : row[col.key].toFixed(1)) 
                      : row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
            {filteredData.length === 0 && (
              <tr>
                <td colSpan={columns.length} style={{textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)'}}>
                  No records found matching your search.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div style={{marginTop: '1rem', color: 'var(--text-secondary)', fontSize: '0.9rem', textAlign: 'right'}}>
        Showing {filteredData.length} of {scatterData.length} entries
      </div>
    </div>
  );
}

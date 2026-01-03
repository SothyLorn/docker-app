import React, { useState } from 'react';
import './App.css';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/info');
      const json = await response.json();
      setData(json);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>React Docker App</h1>
        <p>Welcome to React with Docker!</p>
        <button onClick={fetchData} disabled={loading}>
          {loading ? 'Loading...' : 'Fetch Data'}
        </button>
        {data && (
          <pre>{JSON.stringify(data, null, 2)}</pre>
        )}
      </header>
    </div>
  );
}

export default App;

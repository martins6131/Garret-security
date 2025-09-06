import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const Dashboard = () => {
  const { token } = useAuth();
  const [logs, setLogs] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    // WebSocket for live alerts
    const ws = new WebSocket(process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws');
    ws.onmessage = (event) => {
      setAlerts(prev => [...prev, event.data]);
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    // Fetch logs with error handling
    fetch('/api/logs', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.ok ? res.json() : Promise.reject(res.statusText))
      .then(setLogs)
      .catch(err => console.error("Failed to load logs:", err));
  }, [token]);

  const armSystem = () => {
    fetch('/api/arm', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(res => res.ok ? console.log("System armed") : console.error("Arm failed"))
  };

  return (
    <div>
      <h1>🔐 Security Dashboard</h1>
      
      <section>
        <h2>Live Alerts</h2>
        <ul>
          {alerts.map((a, i) => <li key={i}>{a}</li>)}
        </ul>
      </section>

      <section>
        <button onClick={armSystem}>Arm System</button>
      </section>

      <section>
        <h2>Logs</h2>
        <table>
          <thead><tr><th>Time</th><th>Event</th></tr></thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id}>
                <td>{log.time}</td>
                <td>{log.event}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default Dashboard;

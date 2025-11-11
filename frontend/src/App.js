import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, Database, Users, Folder, Cpu, Bell, Settings, TrendingUp, Zap, Clock, CheckCircle, XCircle, AlertTriangle, Play, Pause, Eye, RefreshCw, Table, Code } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';
const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [systemHealth, setSystemHealth] = useState(null);
  const [frameworks, setFrameworks] = useState([]);
  const [researchers, setResearchers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [simulations, setSimulations] = useState([]);
  const [selectedTrigger, setSelectedTrigger] = useState(null);

  // Trigger demo state
  const [triggerDemo, setTriggerDemo] = useState({
    before: null,
    after: null,
    isRunning: false,
    results: []
  });

  useEffect(() => {
    fetchData();
    const interval = autoRefresh ? setInterval(fetchData, 5000) : null;
    return () => interval && clearInterval(interval);
  }, [autoRefresh]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const dashRes = await fetch(`${API_BASE}/analytics/dashboard/enhanced`);
      const dashData = await dashRes.json();
      setDashboard(dashData);

      const fwRes = await fetch(`${API_BASE}/analytics/frameworks`);
      const fwData = await fwRes.json();
      setFrameworks(fwData);

      const healthRes = await fetch(`${API_BASE}/health`);
      const healthData = await healthRes.json();
      setSystemHealth(healthData);

      const resRes = await fetch(`${API_BASE}/researchers`);
      const resData = await resRes.json();
      setResearchers(resData.slice(0, 10));

      const projRes = await fetch(`${API_BASE}/projects`);
      const projData = await projRes.json();
      setProjects(projData.slice(0, 10));

      const simRes = await fetch(`${API_BASE}/simulations`);
      const simData = await simRes.json();
      setSimulations(simData.slice(0, 10));
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const runTriggerDemo = async (demoType) => {
    setTriggerDemo({ before: null, after: null, isRunning: true, results: [] });
    
    const addResult = (message, type = 'info') => {
      setTriggerDemo(prev => ({
        ...prev,
        results: [...prev.results, { message, type, time: new Date().toLocaleTimeString() }]
      }));
    };

    try {
      if (demoType === 'researcher') {
        addResult('📊 Fetching current researcher data...', 'info');
        const beforeRes = await fetch(`${API_BASE}/researchers/1`);
        const beforeData = await beforeRes.json();
        setTriggerDemo(prev => ({ ...prev, before: beforeData }));
        addResult(`✅ BEFORE: updated_at = ${beforeData.updated_at}`, 'success');
        
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        addResult('🔥 Triggering UPDATE (email change)...', 'warning');
        await fetch(`${API_BASE}/researchers/1`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: `alice.trigger-${Date.now()}@quantumlab.edu`
          })
        });
        
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        addResult('📊 Fetching updated researcher data...', 'info');
        const afterRes = await fetch(`${API_BASE}/researchers/1`);
        const afterData = await afterRes.json();
        setTriggerDemo(prev => ({ ...prev, after: afterData }));
        addResult(`✅ AFTER: updated_at = ${afterData.updated_at}`, 'success');
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        if (beforeData.updated_at !== afterData.updated_at) {
          addResult('🎉 TRIGGER WORKED! Timestamp automatically updated!', 'trigger');
        } else {
          addResult('⚠️ Timestamps are the same', 'warning');
        }
      }
    } catch (error) {
      addResult(`❌ Error: ${error.message}`, 'error');
    } finally {
      setTriggerDemo(prev => ({ ...prev, isRunning: false }));
    }
  };

  const OverviewTab = () => (
    <div className="space-y-6">
      <div className={`rounded-lg p-6 ${systemHealth?.status === 'ok' ? 'bg-green-900/30 border border-green-700' : 'bg-red-900/30 border border-red-700'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={`p-3 rounded-full ${systemHealth?.status === 'ok' ? 'bg-green-600' : 'bg-red-600'}`}>
              <Activity className="text-white" size={28} />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">System Status: {systemHealth?.status?.toUpperCase()}</h3>
              <p className="text-gray-300">Database: {systemHealth?.database || 'Unknown'} • Version: {systemHealth?.version || 'N/A'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                autoRefresh ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              {autoRefresh ? <Pause size={18} /> : <Play size={18} />}
              {autoRefresh ? 'Auto-Refresh ON' : 'Auto-Refresh OFF'}
            </button>
            <button onClick={fetchData} className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2 transition-colors">
              <RefreshCw size={18} />
              Refresh Now
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Researchers" value={dashboard?.overview?.total_researchers || 0} icon={<Users className="text-blue-400" size={32} />} />
        <StatCard title="Active Projects" value={dashboard?.overview?.total_projects || 0} icon={<Folder className="text-green-400" size={32} />} />
        <StatCard title="Simulations" value={dashboard?.overview?.total_simulations || 0} icon={<Cpu className="text-purple-400" size={32} />} />
        <StatCard title="Avg Fidelity" value={`${((dashboard?.quality_metrics?.avg_fidelity || 0) * 100).toFixed(1)}%`} icon={<TrendingUp className="text-orange-400" size={32} />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Cpu size={20} className="text-blue-400" />
            Framework Distribution
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={frameworks.map((f) => ({ name: f.framework, value: f.total_simulations }))}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {frameworks.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Activity size={20} className="text-green-400" />
            Simulation Status
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={Object.entries(dashboard?.status_breakdown || {}).map(([key, value]) => ({ status: key, count: value }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="status" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );

  const TriggerDemoTab = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-900 to-pink-900 p-6 rounded-lg border border-purple-500">
        <div className="flex items-center gap-3 mb-4">
          <Zap size={32} className="text-yellow-400" />
          <div>
            <h2 className="text-2xl font-bold text-white">Live Trigger Demonstration</h2>
            <p className="text-purple-200">Watch database triggers execute in real-time</p>
          </div>
        </div>
        <p className="text-purple-100 text-sm">
          Click the button below to see how database triggers automatically update timestamps.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <button
          onClick={() => runTriggerDemo('researcher')}
          disabled={triggerDemo.isRunning}
          className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-600 disabled:to-gray-700 text-white p-8 rounded-lg transition-all transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
        >
          <Users size={48} className="mb-3 mx-auto" />
          <h3 className="text-2xl font-bold mb-2">Run Researcher Trigger Demo</h3>
          <p className="text-sm text-blue-100">Update researcher email → Watch timestamp auto-update</p>
        </button>
      </div>

      {triggerDemo.results.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Activity size={24} className="text-green-400" />
            Live Execution Log
          </h3>
          <div className="space-y-3">
            {triggerDemo.results.map((result, i) => (
              <div
                key={i}
                className={`p-4 rounded-lg border ${
                  result.type === 'success' ? 'bg-green-900/30 border-green-700' :
                  result.type === 'error' ? 'bg-red-900/30 border-red-700' :
                  result.type === 'warning' ? 'bg-yellow-900/30 border-yellow-700' :
                  result.type === 'trigger' ? 'bg-purple-900/30 border-purple-500' :
                  'bg-blue-900/30 border-blue-700'
                }`}
              >
                <div className="flex items-center gap-3">
                  {result.type === 'success' && <CheckCircle size={20} className="text-green-400" />}
                  {result.type === 'error' && <XCircle size={20} className="text-red-400" />}
                  {result.type === 'warning' && <AlertTriangle size={20} className="text-yellow-400" />}
                  {result.type === 'trigger' && <Zap size={20} className="text-purple-400" />}
                  {result.type === 'info' && <Activity size={20} className="text-blue-400" />}
                  <div className="flex-1">
                    <p className="text-white font-medium text-lg">{result.message}</p>
                    <p className="text-gray-400 text-sm">{result.time}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {(triggerDemo.before || triggerDemo.after) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {triggerDemo.before && (
            <div className="bg-gray-800 rounded-lg p-6 border-4 border-yellow-600">
              <h3 className="text-xl font-bold text-yellow-400 mb-4 flex items-center gap-2">
                <Clock size={24} />
                BEFORE UPDATE
              </h3>
              <div className="space-y-3 font-mono text-lg">
                <div className="flex justify-between">
                  <span className="text-gray-400">ID:</span>
                  <span className="text-white">{triggerDemo.before.researcher_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Name:</span>
                  <span className="text-white">{triggerDemo.before.full_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Email:</span>
                  <span className="text-white text-sm">{triggerDemo.before.email}</span>
                </div>
                <div className="flex justify-between border-t-4 border-yellow-600 pt-3 mt-3">
                  <span className="text-gray-400">updated_at:</span>
                  <span className="text-yellow-400 font-bold text-lg">{triggerDemo.before.updated_at}</span>
                </div>
              </div>
            </div>
          )}

          {triggerDemo.after && (
            <div className="bg-gray-800 rounded-lg p-6 border-4 border-green-600">
              <h3 className="text-xl font-bold text-green-400 mb-4 flex items-center gap-2">
                <CheckCircle size={24} />
                AFTER UPDATE
              </h3>
              <div className="space-y-3 font-mono text-lg">
                <div className="flex justify-between">
                  <span className="text-gray-400">ID:</span>
                  <span className="text-white">{triggerDemo.after.researcher_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Name:</span>
                  <span className="text-white">{triggerDemo.after.full_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Email:</span>
                  <span className="text-white text-sm">{triggerDemo.after.email}</span>
                </div>
                <div className="flex justify-between border-t-4 border-green-600 pt-3 mt-3">
                  <span className="text-gray-400">updated_at:</span>
                  <span className="text-green-400 font-bold text-lg">{triggerDemo.after.updated_at}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {triggerDemo.isRunning && (
        <div className="flex items-center justify-center p-12">
          <RefreshCw size={64} className="text-blue-500 animate-spin" />
          <span className="ml-4 text-2xl text-white font-bold">Running demo...</span>
        </div>
      )}
    </div>
  );

  const DatabaseTab = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Database Explorer</h2>
        <p className="text-gray-400">View database tables</p>
      </div>

      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-4 border-b border-gray-700">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Table size={20} className="text-blue-400" />
            Researchers ({researchers.length})
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-900">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Name</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Email</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Institution</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {researchers.map((r) => (
                <tr key={r.researcher_id} className="hover:bg-gray-750">
                  <td className="px-4 py-3 text-sm text-gray-300">{r.researcher_id}</td>
                  <td className="px-4 py-3 text-sm text-white font-medium">{r.full_name}</td>
                  <td className="px-4 py-3 text-sm text-gray-400">{r.email}</td>
                  <td className="px-4 py-3 text-sm text-gray-400">{r.institution}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const StatCard = ({ title, value, icon }) => (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-blue-500 transition-colors">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm mb-1">{title}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
        </div>
        <div className="p-3 bg-gray-700 rounded-lg">{icon}</div>
      </div>
    </div>
  );

  if (loading && !dashboard) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw size={48} className="text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400 text-lg">Loading QSLRM Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-2 rounded-lg">
                <Database size={28} className="text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">QSLRM Admin</h1>
                <p className="text-xs text-gray-400">Quantum Simulation Lab Manager</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-400">Live</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-8">
            {[
              { id: 'overview', label: 'Overview', icon: TrendingUp },
              { id: 'demo', label: 'Live Trigger Demo', icon: Zap },
              { id: 'database', label: 'Database', icon: Table },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 py-4 px-2 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300'
                }`}
              >
                <tab.icon size={20} />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'demo' && <TriggerDemoTab />}
        {activeTab === 'database' && <DatabaseTab />}
      </div>
    </div>
  );
}

export default App;
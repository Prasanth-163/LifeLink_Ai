import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart3, Users, HeartHandshake, Zap, Target } from 'lucide-react';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get('http://localhost:5000/api/admin/stats');
        setStats(res.data);
      } catch (err) {
        console.error('Error fetching admin stats', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="text-center mt-20">Loading Analytics...</div>;

  return (
    <div className="py-8 px-4 max-w-7xl mx-auto">
      <header className="mb-10 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-dark">Network Analytics</h1>
          <p className="text-gray-500">System-wide performance and engagement metrics.</p>
        </div>
        <div className="text-sm font-medium text-gray-400">Last updated: Just now</div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <StatCard title="Total Donors" value={stats.total_donors} icon={<Users className="text-blue-600" />} color="bg-blue-50" />
        <StatCard title="Active Patients" value={stats.total_patients} icon={<HeartHandshake className="text-red-600" />} color="bg-red-50" />
        <StatCard title="Success Rate" value={`${stats.success_rate}%`} icon={<Target className="text-green-600" />} color="bg-green-50" />
        <StatCard title="Avg. Participation" value={`${stats.avg_participation_score}%`} icon={<Zap className="text-amber-600" />} color="bg-amber-50" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
            <BarChart3 className="text-primary" /> Growth Overview
          </h2>
          <div className="h-64 bg-gray-50 rounded-2xl flex items-center justify-center text-gray-400 italic">
            Chart integration (e.g., Chart.js) would go here.
          </div>
        </div>

        <div className="bg-dark rounded-3xl p-8 text-white">
          <h2 className="text-xl font-bold mb-6">System Health</h2>
          <div className="space-y-6">
            <HealthIndicator label="API Status" status="Operational" color="bg-green-500" />
            <HealthIndicator label="Database Sync" status="Healthy" color="bg-green-500" />
            <HealthIndicator label="AI Model Engine" status="Online" color="bg-green-500" />
            <HealthIndicator label="Notification Service" status="Operational" color="bg-green-500" />
          </div>
          <button className="mt-10 w-full py-3 bg-white/10 hover:bg-white/20 rounded-xl font-bold transition">
            Download Full Report
          </button>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, color }) => (
  <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4">
    <div className={`p-3 ${color} rounded-xl`}>{icon}</div>
    <div>
      <p className="text-sm text-gray-400 font-medium">{title}</p>
      <p className="text-2xl font-bold text-dark">{value}</p>
    </div>
  </div>
);

const HealthIndicator = ({ label, status, color }) => (
  <div className="flex justify-between items-center">
    <span className="text-gray-400">{label}</span>
    <div className="flex items-center gap-2">
      <span className={`w-2 h-2 rounded-full ${color}`}></span>
      <span className="font-medium">{status}</span>
    </div>
  </div>
);

export default AdminDashboard;

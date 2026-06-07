import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import React from 'react';
import Register from './pages/Register';
import Login from './pages/Login';
import DonorDashboard from './pages/DonorDashboard';
import PatientDashboard from './pages/PatientDashboard';
import VolunteerDashboard from './pages/VolunteerDashboard';
import AdminDashboard from './pages/AdminDashboard';
import Profile from './pages/Profile';
import Navbar from './components/Navbar';

const Home = () => (
  <div className="py-20 text-center">
    <h1 className="text-6xl font-extrabold text-primary mb-6">LifeLink AI</h1>
    <p className="text-2xl text-gray-600 max-w-3xl mx-auto mb-10 leading-relaxed">
      The world's first autonomous blood care coordination network. 
      Saving lives through AI-driven donor-patient matching.
    </p>
    <div className="flex justify-center gap-6">
      <a href="/register" className="px-10 py-4 bg-primary text-white rounded-full font-bold hover:bg-secondary transition-all transform hover:scale-105 shadow-xl">Get Started</a>
      <a href="/login" className="px-10 py-4 bg-white text-primary border-2 border-primary rounded-full font-bold hover:bg-gray-50 transition-all">Login</a>
    </div>
  </div>
);

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background text-dark font-sans">
        <Navbar />
        
        <main className="container mx-auto px-6">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/donor-dashboard" element={<DonorDashboard />} />
            <Route path="/patient-dashboard" element={<PatientDashboard />} />
            <Route path="/volunteer-dashboard" element={<VolunteerDashboard />} />
            <Route path="/admin-dashboard" element={<AdminDashboard />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

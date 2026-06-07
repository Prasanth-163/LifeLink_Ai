import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Users, Calendar, Activity, Heart, PlusCircle, Clock, AlertTriangle, ShieldCheck } from 'lucide-react';

const PatientDashboard = () => {
  const [profile, setProfile] = useState(null);
  const [circle, setCircle] = useState([]);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const userId = localStorage.getItem('user_id');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const profileRes = await axios.get(`http://localhost:5000/api/patient/profile/${userId}`);
        setProfile(profileRes.data);
        
        const circleRes = await axios.get(`http://localhost:5000/api/patient/circle/${profileRes.data.patient_id}`);
        setCircle(circleRes.data);
        
        const requestsRes = await axios.get(`http://localhost:5000/api/patient/requests/${profileRes.data.patient_id}`);
        setRequests(requestsRes.data);
      } catch (err) {
        console.error('Error fetching dashboard data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [userId]);

  const createEmergencyRequest = async () => {
    const confirm = window.confirm("LifeLink AI automatically schedules your requests 5 days before your transfusion. Are you sure you want to raise an IMMEDIATE emergency request?");
    if (!confirm) return;

    try {
      await axios.post('http://localhost:5000/api/patient/request/create', {
        patient_id: profile.patient_id,
        blood_group: profile.blood_group,
        urgency: 'critical'
      });
      alert('Emergency request created! Your circle and our volunteers have been alerted.');
      // Refresh requests
      const requestsRes = await axios.get(`http://localhost:5000/api/patient/requests/${profile.patient_id}`);
      setRequests(requestsRes.data);
    } catch (err) {
      alert('Failed to create request');
    }
  };

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
      <p className="text-gray-500 font-medium">Loading your care network...</p>
    </div>
  );

  return (
    <div className="py-8 px-4 max-w-7xl mx-auto mb-20">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12">
        <div>
          <h1 className="text-4xl font-black text-dark tracking-tight mb-2">Patient Care Dashboard</h1>
          <p className="text-gray-500 font-medium text-lg">Your health is our priority. Your dedicated circle is ready.</p>
        </div>
        <div className="flex flex-col gap-2">
          <button 
            onClick={createEmergencyRequest}
            className="bg-red-600 text-white px-8 py-4 rounded-2xl font-bold flex items-center gap-2 hover:bg-red-700 transition shadow-lg shadow-red-100"
          >
            <PlusCircle size={20} /> Emergency Blood Request
          </button>
          <p className="text-[10px] text-gray-400 text-center font-bold uppercase tracking-wider">Use only in urgent cases</p>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        {/* Left Column: Health Stats */}
        <div className="lg:col-span-4 space-y-8">
          <div className="bg-white p-8 rounded-[40px] shadow-xl border border-gray-50">
            <h2 className="text-2xl font-black mb-8 flex items-center gap-3">
              <Activity className="text-primary" size={24} /> Health Status
            </h2>
            <div className="space-y-6">
              <div className="p-6 bg-red-50 rounded-3xl border border-red-100">
                <p className="text-xs text-red-400 font-black uppercase tracking-widest mb-1">Blood Group</p>
                <p className="text-4xl font-black text-primary leading-none">{profile?.blood_group}</p>
              </div>
              
              <div className={`p-6 rounded-3xl border-2 ${profile?.days_until_transfusion <= 5 ? 'bg-orange-50 border-orange-200' : 'bg-blue-50 border-blue-100'}`}>
                <div className="flex justify-between items-center mb-4">
                  <p className="text-xs text-blue-400 font-black uppercase tracking-widest">Next Transfusion</p>
                  <Clock size={16} className="text-blue-400" />
                </div>
                <div className="flex items-baseline gap-2 mb-1">
                  <p className="text-5xl font-black leading-none">{profile?.days_until_transfusion}</p>
                  <p className="text-lg font-bold opacity-60">Days</p>
                </div>
                <p className="text-sm font-bold opacity-70 mb-4">Scheduled: {new Date(profile?.expected_next_transfusion_date).toLocaleDateString()}</p>
                
                <div className="flex items-center gap-2 text-xs font-bold text-blue-600 bg-white/50 p-2 rounded-xl">
                  <ShieldCheck size={14} /> 
                  {profile?.days_until_transfusion <= 5 
                    ? "AI is now contacting your donors."
                    : `Automation starts in ${profile?.days_until_transfusion - 5} days.`}
                </div>
              </div>

              <div className="flex items-center gap-3 px-6 py-4 bg-gray-50 rounded-2xl text-gray-500 text-sm font-medium">
                <Calendar size={18} /> Frequency: Every {profile?.frequency_in_days} days
              </div>
            </div>
          </div>

          <div className="bg-white p-8 rounded-[40px] shadow-xl border border-gray-50">
            <h2 className="text-xl font-black mb-6 flex items-center gap-3">
              <Users className="text-primary" size={20} /> Your Donor Circle
            </h2>
            <div className="space-y-4">
              {circle.map((donor, idx) => (
                <div key={idx} className="flex justify-between items-center p-4 bg-gray-50 rounded-2xl hover:bg-white hover:shadow-md transition-all border border-transparent hover:border-gray-100">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary text-white rounded-xl flex items-center justify-center font-bold shadow-sm">
                      {donor.full_name[0]}
                    </div>
                    <div>
                      <p className="font-bold text-sm text-dark">{donor.full_name}</p>
                      <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Rank #{donor.ranking_position}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs font-black text-blue-600">{donor.participation_score}%</p>
                    <p className="text-[10px] text-gray-400 font-bold">MATCH</p>
                  </div>
                </div>
              ))}
              {circle.length === 0 && (
                <div className="text-center py-8">
                   <div className="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-3">
                     <Users size={20} className="text-gray-300" />
                   </div>
                   <p className="text-sm text-gray-400 font-medium">AI is generating your dedicated circle...</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Request Timeline */}
        <div className="lg:col-span-8 space-y-8">
          <h2 className="text-2xl font-black flex items-center gap-3">
            <Heart className="text-primary" size={24} /> Care Timeline
          </h2>
          
          {requests.length === 0 ? (
            <div className="bg-white p-20 rounded-[40px] border-2 border-dashed border-gray-100 text-center">
              <div className="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-6">
                <Calendar size={32} className="text-gray-200" />
              </div>
              <p className="text-xl font-bold text-gray-400">No care activities recorded yet.</p>
              <p className="text-gray-400 max-w-sm mx-auto mt-2">Your automated requests will appear here as they are created by LifeLink AI.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {requests.map(req => (
                <div key={req.request_id} className="bg-white p-8 rounded-[32px] shadow-sm border border-gray-100 hover:shadow-xl hover:shadow-red-50 transition-all border-l-8 border-l-primary">
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-3 py-1 rounded-full text-[10px] font-black tracking-widest uppercase ${req.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                          {req.status}
                        </span>
                        <p className="text-[10px] font-bold text-gray-400 uppercase">{new Date(req.request_date).toLocaleDateString()}</p>
                      </div>
                      <h3 className="text-2xl font-black text-dark">Donation Request for {req.units_required} Unit(s)</h3>
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap items-center gap-8">
                    <div className="flex items-center gap-3">
                      <p className="text-sm font-bold text-gray-400 uppercase tracking-widest">Matched Donors</p>
                      <div className="flex -space-x-3">
                        {req.confirmed_donors.map((d, i) => (
                          <div key={i} title={d.full_name} className="w-12 h-12 rounded-2xl bg-white border-4 border-gray-50 flex items-center justify-center shadow-sm text-primary font-black">
                            {d.full_name[0]}
                          </div>
                        ))}
                        {req.confirmed_donors.length === 0 && (
                          <div className="flex items-center gap-2 text-xs font-bold text-gray-400 bg-gray-50 px-4 py-2 rounded-xl">
                            <Clock size={14} /> Waiting for circle response...
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {req.status === 'pending' && (
                      <div className="flex items-center gap-2 text-amber-600 bg-amber-50 px-4 py-2 rounded-xl text-xs font-bold">
                        <AlertTriangle size={14} /> AI is currently searching your circle...
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PatientDashboard;


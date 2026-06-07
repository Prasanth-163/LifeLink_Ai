import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { AlertTriangle, TrendingUp, Users, ShieldAlert, CheckCircle, Droplet, Phone, MapPin, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';

const VolunteerDashboard = () => {
  const [activeRequests, setActiveRequests] = useState([]);
  const [healthReports, setHealthReports] = useState([]);
  const [upcoming, setUpcoming] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedRequest, setExpandedRequest] = useState(null);

  const fetchData = async () => {
    try {
      const [requestsRes, healthRes, upcomingRes] = await Promise.all([
        axios.get('http://localhost:5000/api/volunteer/active-requests'),
        axios.get('http://localhost:5000/api/volunteer/circle-health'),
        axios.get('http://localhost:5000/api/volunteer/upcoming-patients')
      ]);
      
      setActiveRequests(requestsRes.data);
      setHealthReports(healthRes.data);
      setUpcoming(upcomingRes.data);
    } catch (err) {
      console.error('Error fetching volunteer data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const closeRequest = async (requestId) => {
    if (!window.confirm("Are you sure you want to close this request? This will stop all notifications.")) return;
    try {
      await axios.post('http://localhost:5000/api/volunteer/request/close', {
        request_id: requestId
      });
      alert('Request closed successfully!');
      fetchData();
    } catch (err) {
      alert('Failed to close request');
    }
  };

  const confirmDonation = async (requestId, donorId) => {
    if (!window.confirm("Confirm this donation? This will update stats and schedule the next transfusion.")) return;
    try {
      const response = await axios.post('http://localhost:5000/api/volunteer/confirm-donation', {
        request_id: requestId,
        donor_id: donorId
      });
      alert(response.data.message || 'Donation confirmed successfully!');
      fetchData();
    } catch (err) {
      const errorMsg = err.response?.data?.message || 'Failed to confirm donation. Please check backend logs.';
      alert(errorMsg);
      console.error('Donation confirmation error:', err);
    }
  };

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
      <p className="text-gray-500 font-medium">Loading network oversight...</p>
    </div>
  );

  return (
    <div className="py-8 px-4 max-w-7xl mx-auto mb-20">
      <header className="mb-12 text-center lg:text-left">
        <h1 className="text-4xl font-black text-dark tracking-tight mb-2">Volunteer Command Center</h1>
        <p className="text-gray-500 font-medium text-lg">Orchestrating the LifeLink AI care network.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        
        {/* Main Column: Active Requests Management */}
        <div className="lg:col-span-8 space-y-10">
          <section>
            <h2 className="text-2xl font-black mb-6 flex items-center gap-3">
              <ShieldAlert className="text-primary" size={28} /> Active Care Requests
            </h2>
            
            <div className="space-y-6">
              {activeRequests.map(req => (
                <div key={req.request_id} className={`bg-white p-8 rounded-[32px] shadow-sm border ${req.urgency === 'critical' ? 'border-red-200 bg-red-50/10' : 'border-gray-100'}`}>
                  <div className="flex justify-between items-start mb-6">
                    <div className="flex items-start gap-4">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-3 py-1 rounded-full text-[10px] font-black tracking-widest uppercase ${req.urgency === 'critical' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'}`}>
                            {req.urgency}
                          </span>
                          <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">{req.status}</span>
                        </div>
                        <h3 className="text-2xl font-black text-dark">{req.patient_name}</h3>
                        <div className="flex items-center gap-4 text-gray-500 mt-1 font-medium text-sm">
                           <div className="flex items-center gap-1"><Droplet size={14} className="text-primary" /> {req.blood_group}</div>
                           <div className="flex items-center gap-1"><MapPin size={14} className="text-primary" /> {req.city}</div>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button 
                        onClick={() => setExpandedRequest(expandedRequest === req.request_id ? null : req.request_id)}
                        className="px-4 py-2 bg-gray-50 text-gray-400 rounded-xl text-[10px] font-black tracking-widest uppercase hover:bg-gray-100 transition flex items-center gap-2"
                      >
                        {expandedRequest === req.request_id ? <><ChevronUp size={14} /> Hide Logs</> : <><ChevronDown size={14} /> AI Logs</>}
                      </button>
                      <button 
                        onClick={() => closeRequest(req.request_id)}
                        className="px-4 py-2 bg-gray-100 text-gray-500 rounded-xl text-[10px] font-black tracking-widest uppercase hover:bg-gray-200 transition"
                      >
                        Close
                      </button>
                    </div>
                  </div>

                  {/* Approach History (Conditional) */}
                  {expandedRequest === req.request_id && (
                    <div className="mb-6 p-4 bg-amber-50 rounded-2xl border border-amber-100">
                       <p className="text-[10px] font-black text-amber-600 uppercase tracking-widest mb-3 flex items-center gap-2">
                         <Users size={12} /> AI Contact Sequence
                       </p>
                       <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                         {req.approach_history?.map((entry, i) => (
                           <div key={i} className="flex items-center gap-3 bg-white/60 p-3 rounded-xl border border-amber-50">
                             <div className="w-5 h-5 bg-amber-200 text-amber-700 rounded-full flex items-center justify-center text-[9px] font-black flex-shrink-0">
                               {i + 1}
                             </div>
                             <div className="flex-1 min-w-0">
                               <p className="text-[11px] font-black text-amber-800 truncate">{entry.full_name}</p>
                               <p className="text-[9px] text-amber-500 font-bold uppercase truncate">
                                 {new Date(entry.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • {entry.status}
                               </p>
                             </div>
                           </div>
                         ))}
                         {(!req.approach_history || req.approach_history.length === 0) && (
                           <p className="text-[10px] text-amber-400 italic">Initiating contact sequence...</p>
                         )}
                       </div>
                    </div>
                  )}

                  <div className="space-y-4">
                    <p className="text-xs font-black text-gray-400 uppercase tracking-widest">Confirmed Circle Matches</p>
                    {req.matched_donors.length === 0 ? (
                      <div className="p-4 bg-gray-50 rounded-2xl text-sm text-gray-400 font-medium italic">
                        No donors have accepted this request yet.
                      </div>
                    ) : (
                      <div className="grid gap-3">
                        {req.matched_donors.map(donor => (
                          <div key={donor.donor_id} className="bg-white p-4 rounded-2xl border border-gray-100 flex justify-between items-center shadow-sm">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 bg-green-50 text-green-600 rounded-xl flex items-center justify-center font-bold">
                                {donor.full_name[0]}
                              </div>
                              <div>
                                <p className="font-bold text-sm">{donor.full_name}</p>
                                <p className="text-xs text-gray-400 flex items-center gap-1 font-medium"><Phone size={10} /> {donor.phone}</p>
                              </div>
                            </div>
                            <button 
                              onClick={() => confirmDonation(req.request_id, donor.donor_id)}
                              className="px-6 py-2 bg-green-600 text-white rounded-xl text-xs font-black tracking-widest uppercase hover:bg-green-700 transition shadow-lg shadow-green-100"
                            >
                              Confirm
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {activeRequests.length === 0 && (
                <div className="bg-white p-20 rounded-[40px] border-2 border-dashed border-gray-100 text-center text-gray-400">
                  <CheckCircle size={48} className="mx-auto mb-4 opacity-20" />
                  <p className="text-lg font-bold">Network state is optimal.</p>
                </div>
              )}
            </div>
          </section>
        </div>

        {/* Sidebar: Intelligence & Monitoring */}
        <div className="lg:col-span-4 space-y-8">
          <div className="bg-white p-8 rounded-[40px] shadow-xl border border-gray-50">
            <h2 className="text-xl font-black mb-6 flex items-center gap-3 text-blue-600">
              <TrendingUp size={20} /> Forecast
            </h2>
            <div className="space-y-4">
              {upcoming.map(p => (
                <div key={p.patient_id} className="p-4 bg-blue-50 rounded-2xl border border-blue-100 group hover:bg-white transition-all">
                  <p className="font-black text-blue-900 text-sm">{p.full_name}</p>
                  <div className="flex justify-between items-center mt-2">
                    <div className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Target Date</div>
                    <div className="text-xs font-black text-blue-700">{new Date(p.expected_next_transfusion_date).toLocaleDateString()}</div>
                  </div>
                </div>
              ))}
              {upcoming.length === 0 && <p className="text-gray-400 text-sm italic text-center py-4">No upcoming transfusions.</p>}
            </div>
          </div>

          <div className="bg-white p-8 rounded-[40px] shadow-xl border border-gray-50">
            <h2 className="text-xl font-black mb-1 flex items-center gap-3 text-purple-600">
              <Sparkles size={20} /> AI Self-Healing
            </h2>
            <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-6 ml-8">Auto-replacing inactive donors</p>
            <div className="space-y-4">
              {healthReports.map(report => (
                <div key={report.patient_id} className="p-4 bg-purple-50 rounded-2xl border border-purple-100">
                  <p className="font-black text-purple-900 text-xs mb-2">Circle: {report.patient_name}</p>
                  {report.recommendations.map((rec, i) => (
                    <div key={i} className="bg-white/60 p-3 rounded-xl border border-purple-50 flex items-start gap-2 mb-2 last:mb-0">
                      <AlertTriangle size={14} className="text-purple-600 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-[11px] font-black text-purple-800 uppercase tracking-tight">Optimization</p>
                        <p className="text-[9px] text-purple-600 font-medium leading-tight">{rec.reason}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ))}
              {healthReports.length === 0 && (
                <div className="p-6 text-center">
                   <div className="w-12 h-12 bg-green-50 text-green-600 rounded-full flex items-center justify-center mx-auto mb-3">
                     <CheckCircle size={24} />
                   </div>
                   <p className="text-gray-400 text-[10px] font-black uppercase tracking-widest">Circles Healthy</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VolunteerDashboard;

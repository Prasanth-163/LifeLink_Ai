import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Droplet, Calendar, Award, Bell, CheckCircle, XCircle, TrendingUp, MapPin, Heart, Clock, ShieldCheck } from 'lucide-react';

const DonorDashboard = () => {
  const [profile, setProfile] = useState(null);
  const [requests, setRequests] = useState([]);
  const [acceptedRequests, setAcceptedRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const userId = localStorage.getItem('user_id');

  const fetchData = async () => {
    try {
      const profileRes = await axios.get(`http://localhost:5000/api/donor/profile/${userId}`);
      setProfile(profileRes.data);
      
      const requestsRes = await axios.get(`http://localhost:5000/api/donor/requests/${profileRes.data.donor_id}`);
      // Filter requests: those not yet responded to, and those accepted but not completed
      setRequests(requestsRes.data);
    } catch (err) {
      console.error('Error fetching dashboard data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [userId]);

  const handleResponse = async (requestId, response) => {
    try {
      const res = await axios.post('http://localhost:5000/api/donor/respond', {
        donor_id: profile.donor_id,
        request_id: requestId,
        response: response
      });
      if (response === 'accepted') {
        if (res.data.escalated_message) {
           alert(res.data.escalated_message);
        } else {
           alert('Thank you! Please visit the hospital to donate within the next 24 hours. A volunteer will confirm your donation.');
        }
      } else {
        alert('You have declined the request. We will notify the next donor in the circle.');
      }
      fetchData();
    } catch (err) {
      alert('Failed to record response');
    }
  };

  const confirmDonation = async (requestId) => {
    try {
      await axios.post('http://localhost:5000/api/donor/donation/confirm', {
        donor_id: profile.donor_id,
        request_id: requestId
      });
      alert('Donation confirmed! Thank you for your life-saving contribution.');
      fetchData();
    } catch (err) {
      alert('Failed to confirm donation');
    }
  };

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
      <p className="text-gray-500 font-medium animate-pulse">Syncing with LifeLink AI...</p>
    </div>
  );

  if (!profile) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <p className="text-red-500 font-black text-xl mb-4">Access Denied / Profile Not Found</p>
      <p className="text-gray-500 mb-8">Please ensure you are logged in correctly.</p>
      <a href="/login" className="px-8 py-3 bg-primary text-white rounded-2xl font-bold shadow-lg shadow-red-100">Go to Login</a>
    </div>
  );

  return (
    <div className="py-8 px-4 max-w-7xl mx-auto mb-20">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12">
        <div>
          <h1 className="text-4xl font-black text-dark tracking-tight mb-2">
            Hello, {profile?.full_name.split(' ')[0]}! <span className="inline-block animate-bounce text-primary">❤️</span>
          </h1>
          <p className="text-gray-500 font-medium text-lg">Your blood type <span className="text-primary font-bold">{profile?.blood_group}</span> is in high demand today.</p>
        </div>
        
        <div className="grid grid-cols-2 gap-4 w-full md:w-auto">
          <div className="bg-white p-5 rounded-3xl shadow-xl shadow-red-50 border border-gray-100 flex items-center gap-4">
            <div className="p-3 bg-red-50 rounded-2xl text-primary"><Droplet size={32} fill="currentColor" /></div>
            <div>
              <p className="text-[10px] text-gray-400 font-black tracking-widest uppercase">Group</p>
              <p className="text-3xl font-black text-primary leading-tight">{profile?.blood_group}</p>
            </div>
          </div>
          <div className="bg-white p-5 rounded-3xl shadow-xl shadow-blue-50 border border-gray-100 flex items-center gap-4">
            <div className="p-3 bg-blue-50 rounded-2xl text-blue-600"><Award size={32} /></div>
            <div>
              <p className="text-[10px] text-gray-400 font-black tracking-widest uppercase">Score</p>
              <p className="text-3xl font-black text-blue-600 leading-tight">{profile?.participation_score}%</p>
            </div>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        {/* Main Content: Requests */}
        <div className="lg:col-span-8 space-y-10">
          <section>
            <h2 className="text-2xl font-black mb-6 flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center text-primary">
                <Bell size={24} />
              </div>
              New Requests
              {requests.length > 0 && <span className="ml-2 px-3 py-1 bg-primary text-white text-xs rounded-full">{requests.length}</span>}
            </h2>
            
            {requests.length === 0 ? (
              <div className="bg-white p-16 rounded-[40px] border-2 border-dashed border-gray-100 text-center group hover:border-primary/20 transition-all">
                <div className="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                  <Heart size={32} className="text-gray-300" />
                </div>
                <p className="text-xl font-bold text-gray-400 mb-2">No active requests right now</p>
                <p className="text-gray-400 max-w-sm mx-auto">We'll notify you as soon as a compatible patient in your circle needs support.</p>
              </div>
            ) : (
              <div className="grid gap-6">
                {requests.map(req => (
                  <div key={req.request_id} className="bg-white p-8 rounded-[32px] shadow-sm border border-gray-100 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 hover:shadow-xl hover:shadow-red-50 hover:border-primary/20 transition-all group">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <span className={`text-[10px] font-black px-3 py-1 rounded-full tracking-widest uppercase ${req.urgency === 'critical' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'}`}>
                          {req.urgency}
                        </span>
                        <div className="flex items-center gap-1 text-gray-400 text-xs font-bold">
                           <Clock size={12} /> {new Date(req.request_date).toLocaleDateString()}
                        </div>
                      </div>
                      <h3 className="text-2xl font-black text-dark mb-2 group-hover:text-primary transition-colors">{req.patient_name}</h3>
                      <div className="flex flex-wrap gap-4 text-gray-500 font-medium">
                        <div className="flex items-center gap-1.5"><MapPin size={16} className="text-primary" /> {req.city}</div>
                        <div className="flex items-center gap-1.5"><Droplet size={16} className="text-primary" /> {req.units_required} Units</div>
                      </div>
                      
                      {req.status === 'matched' && (
                        <div className="mt-4 p-4 bg-green-50 rounded-2xl border border-green-100 flex items-center gap-3 text-green-700 font-bold text-sm">
                          <ShieldCheck size={20} />
                          Please visit the hospital within 24 hours to complete your donation.
                        </div>
                      )}
                    </div>
                    <div className="flex gap-4 w-full md:w-auto">
                      {req.status === 'pending' ? (
                        <>
                          <button 
                            onClick={() => handleResponse(req.request_id, 'declined')}
                            className="flex-1 md:flex-none p-4 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-2xl transition-all font-bold flex items-center justify-center gap-2 border border-gray-100 md:border-transparent"
                          >
                            <XCircle size={24} /> <span className="md:hidden">Decline</span>
                          </button>
                          <button 
                            onClick={() => handleResponse(req.request_id, 'accepted')}
                            className="flex-1 md:flex-none px-8 py-4 bg-primary text-white rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-secondary transition-all shadow-lg shadow-red-100"
                          >
                            <CheckCircle size={24} /> Accept Request
                          </button>
                        </>
                      ) : (
                        <div className="px-6 py-3 bg-green-100 text-green-700 rounded-xl font-black text-xs tracking-widest uppercase flex items-center gap-2">
                           <CheckCircle size={16} /> Accepted
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>

        {/* Sidebar: Impact & Stats */}
        <div className="lg:col-span-4 space-y-8">
          <div className="bg-white p-8 rounded-[40px] shadow-xl shadow-gray-100 border border-gray-50">
            <h2 className="font-black text-2xl mb-8 flex items-center gap-3">
              <div className="w-10 h-10 bg-green-50 rounded-xl flex items-center justify-center text-green-600">
                <TrendingUp size={24} />
              </div>
              Your Impact
            </h2>
            
            <div className="space-y-6">
              <div className="p-6 bg-gray-50 rounded-3xl group hover:bg-primary hover:text-white transition-all">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-gray-500 font-bold text-xs uppercase tracking-widest group-hover:text-red-100">Total Donations</span>
                  <Heart size={16} className="text-primary group-hover:text-white" />
                </div>
                <p className="text-4xl font-black leading-none">{profile?.donations_till_date}</p>
                <p className="text-xs mt-2 text-gray-400 group-hover:text-red-100 font-medium">Lives impacted through your care</p>
              </div>
              
              <div className={`p-6 rounded-3xl border-2 ${profile?.donor_status === 'eligible' ? 'bg-green-50 border-green-100' : 'bg-orange-50 border-orange-100'}`}>
                <div className="flex justify-between items-center mb-3">
                  <span className="text-gray-500 font-bold text-xs uppercase tracking-widest">Eligibility Status</span>
                  <div className={`w-3 h-3 rounded-full animate-pulse ${profile?.donor_status === 'eligible' ? 'bg-green-500' : 'bg-orange-500'}`}></div>
                </div>
                <p className={`text-xl font-black mb-2 ${profile?.donor_status === 'eligible' ? 'text-green-700' : 'text-orange-700'}`}>
                  {profile?.donor_status === 'eligible' ? 'ELIGIBLE TO DONATE' : 'RESTING PERIOD'}
                </p>
                <p className="text-xs text-gray-500 leading-relaxed font-medium">
                  {profile?.donor_status === 'eligible' 
                    ? "You are ready to save lives! Your health and commitment make a difference."
                    : `Next eligible to donate on ${profile?.next_eligible_date}. Rest well, hero!`}
                </p>
              </div>

              <div className="flex justify-between items-center px-6 py-5 bg-blue-50 rounded-3xl text-blue-900">
                <div>
                  <p className="text-[10px] font-black uppercase tracking-widest opacity-60">Last Donation</p>
                  <p className="font-bold">{profile?.last_donation_date || 'New Blood Warrior'}</p>
                </div>
                <Calendar size={20} className="opacity-40" />
              </div>
            </div>
          </div>

          <div className="bg-dark rounded-[40px] p-8 text-white shadow-2xl relative overflow-hidden group">
            <div className="absolute -right-10 -bottom-10 w-40 h-40 bg-primary/20 rounded-full blur-3xl group-hover:bg-primary/40 transition-all"></div>
            <h3 className="font-black text-xl mb-4 relative z-10">Did you know?</h3>
            <p className="text-gray-400 text-sm leading-relaxed relative z-10">
              A single blood donation can save up to three lives. Since you joined LifeLink AI, you've become a critical part of a patient's survival circle.
            </p>
            <a 
              href="https://www.google.com/search?q=what+is+thalassemia+and+why+is+blood+donation+important" 
              target="_blank" 
              rel="noopener noreferrer"
              className="mt-6 flex items-center gap-2 text-primary font-bold text-sm relative z-10 cursor-pointer hover:underline"
            >
              Learn more about Thalassemia <Heart size={14} fill="currentColor" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DonorDashboard;


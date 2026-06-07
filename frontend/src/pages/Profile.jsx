import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { User, Phone, MapPin, Save, AlertCircle, Droplet, Award, Calendar, CheckCircle } from 'lucide-react';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const userId = localStorage.getItem('user_id');
  const role = localStorage.getItem('role');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await axios.get(`http://localhost:5000/api/${role}/profile/${userId}`);
        setProfile(res.data);
      } catch (err) {
        console.error('Error fetching profile', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [userId, role]);

  const handleChange = (e) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      await axios.put(`http://localhost:5000/api/${role}/profile/update`, {
        user_id: userId,
        phone: profile.phone,
        city: profile.city
      });
      setMessage('Profile updated successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage('Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="text-center mt-20 text-gray-500 italic">Loading your profile...</div>;

  if (!profile) return (
    <div className="text-center mt-20">
      <p className="text-red-500 font-bold text-lg mb-4">Failed to load profile.</p>
      <button onClick={() => window.location.reload()} className="px-6 py-2 bg-primary text-white rounded-xl">Retry</button>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto mt-12 px-4 mb-20">
      <div className="flex flex-col md:flex-row gap-8">
        {/* Left Column: Stats & Profile Card */}
        <div className="w-full md:w-1/3 space-y-6">
          <div className="bg-white p-8 rounded-3xl shadow-xl border border-gray-100 text-center">
            <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center text-primary mx-auto mb-4 border-4 border-white shadow-inner">
              <User size={48} />
            </div>
            <h1 className="text-2xl font-bold text-dark mb-1">{profile.full_name}</h1>
            <p className="text-gray-400 font-medium capitalize mb-6">{profile.role}</p>
            
            <div className="flex justify-center gap-3">
               <div className="px-4 py-2 bg-red-50 rounded-xl text-primary font-bold text-sm flex items-center gap-2">
                 <Droplet size={16} /> {profile.blood_group}
               </div>
               <div className="px-4 py-2 bg-blue-50 rounded-xl text-blue-600 font-bold text-sm flex items-center gap-2">
                 <Award size={16} /> {profile.participation_score}%
               </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-primary to-secondary p-8 rounded-3xl text-white shadow-lg shadow-red-100">
            <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
              <CheckCircle size={20} /> Eligibility Status
            </h3>
            <div className="space-y-4">
              <div className="pb-4 border-b border-white/20">
                <p className="text-xs text-red-100 font-bold tracking-wider uppercase mb-1">Current Status</p>
                <p className="text-xl font-black">{profile.donor_status === 'eligible' ? 'ELIGIBLE' : 'NOT ELIGIBLE'}</p>
              </div>
              <div>
                <p className="text-xs text-red-100 font-bold tracking-wider uppercase mb-1">Next Possible Donation</p>
                <p className="text-lg font-bold">
                  {profile.donor_status === 'eligible' ? 'Available Now' : profile.next_eligible_date}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Edit Form */}
        <div className="w-full md:w-2/3">
          <div className="bg-white p-8 rounded-3xl shadow-xl border border-gray-100">
            <h2 className="text-xl font-bold mb-8 flex items-center gap-2">
              Edit Profile Information
            </h2>

            {message && (
              <div className={`mb-6 p-4 rounded-xl flex items-center gap-2 ${message.includes('success') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                <AlertCircle size={20} />
                <span className="font-bold">{message}</span>
              </div>
            )}

            <form onSubmit={handleUpdate} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-bold text-gray-500 ml-1">Full Name</label>
                  <input 
                    value={profile.full_name} 
                    disabled 
                    className="w-full p-4 bg-gray-50 border border-gray-100 rounded-2xl text-gray-400 cursor-not-allowed"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-bold text-gray-500 ml-1">Email Address</label>
                  <input 
                    value={profile.email} 
                    disabled 
                    className="w-full p-4 bg-gray-50 border border-gray-100 rounded-2xl text-gray-400 cursor-not-allowed"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-bold text-gray-500 ml-1">Phone Number</label>
                  <div className="relative">
                    <Phone className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                    <input 
                      name="phone"
                      value={profile.phone} 
                      onChange={handleChange}
                      className="w-full p-4 pl-12 bg-white border border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary/20 focus:border-primary transition"
                      placeholder="Enter phone number"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-bold text-gray-500 ml-1">City</label>
                  <div className="relative">
                    <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                    <input 
                      name="city"
                      value={profile.city} 
                      onChange={handleChange}
                      className="w-full p-4 pl-12 bg-white border border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary/20 focus:border-primary transition"
                      placeholder="Enter city"
                    />
                  </div>
                </div>
              </div>

              <div className="pt-4">
                <button 
                  type="submit" 
                  disabled={saving}
                  className="w-full md:w-auto px-10 py-4 bg-primary text-white rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-secondary transition shadow-lg shadow-red-100 disabled:opacity-50"
                >
                  {saving ? 'Saving...' : <><Save size={20} /> Save Changes</>}
                </button>
              </div>
            </form>
          </div>
          
          <div className="mt-8 bg-blue-50 p-6 rounded-3xl border border-blue-100 flex items-start gap-4">
            <div className="p-3 bg-white rounded-2xl text-blue-600 shadow-sm">
              <Calendar size={24} />
            </div>
            <div>
              <h4 className="font-bold text-blue-900 mb-1">Why is my Participation Score {profile.participation_score}%?</h4>
              <p className="text-sm text-blue-700 leading-relaxed">
                Our AI calculates this score based on your donation frequency, responsiveness to calls, and total lives saved. 
                Regular donations and responding to requests help increase your score and ranking in donor circles!
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;


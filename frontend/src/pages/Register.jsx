import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { UserPlus, Droplet, Heart, ShieldCheck, Sparkles } from 'lucide-react';

const Register = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    dob: '',
    city: '',
    role: 'donor',
    blood_group: '',
    last_donation_date: '',
    frequency_in_days: '',
    expected_next_transfusion_date: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/auth/register', formData);
      alert(response.data.message);
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 bg-gray-50">
      <div className="max-w-5xl w-full grid grid-cols-1 lg:grid-cols-2 bg-white rounded-[40px] shadow-2xl overflow-hidden border border-gray-100">
        
        {/* Left Side: Motivational Content */}
        <div className="bg-primary p-12 text-white flex flex-col justify-center relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32 blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-red-900/20 rounded-full -ml-32 -mb-32 blur-3xl"></div>
          
          <div className="relative z-10">
            <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mb-8 backdrop-blur-md">
              <Heart size={32} fill="white" />
            </div>
            <h1 className="text-5xl font-black mb-6 leading-tight">Be the Lifeline for Someone Today.</h1>
            <p className="text-red-100 text-xl mb-12 font-medium leading-relaxed">
              Thalassemia patients require regular blood transfusions every 15-21 days to survive. Your one donation can be their tomorrow.
            </p>
            
            <div className="space-y-6">
              <div className="flex items-center gap-4 bg-white/10 p-4 rounded-2xl backdrop-blur-sm border border-white/10">
                <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center text-white">
                  <Droplet size={20} fill="currentColor" />
                </div>
                <div>
                  <p className="font-bold">Automated Matching</p>
                  <p className="text-sm text-red-100">AI finds the perfect match for your blood type.</p>
                </div>
              </div>
              <div className="flex items-center gap-4 bg-white/10 p-4 rounded-2xl backdrop-blur-sm border border-white/10">
                <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center text-white">
                  <ShieldCheck size={20} />
                </div>
                <div>
                  <p className="font-bold">Real-time Coordination</p>
                  <p className="text-sm text-red-100">No more manual calls. Everything is autonomous.</p>
                </div>
              </div>
            </div>

            <div className="mt-12 pt-8 border-t border-white/10">
              <p className="text-sm italic font-medium opacity-80 italic">"Every drop counts in the fight against Thalassemia. Join the elite circle of donors today."</p>
            </div>
          </div>
        </div>

        {/* Right Side: Registration Form */}
        <div className="p-12 lg:p-16 overflow-y-auto max-h-[90vh]">
          <div className="mb-10 text-center lg:text-left">
            <h2 className="text-3xl font-black text-dark flex items-center gap-3 justify-center lg:justify-start">
              <UserPlus className="text-primary" size={32} /> Join LifeLink AI
            </h2>
            <p className="text-gray-400 font-medium mt-2">Start your journey as a life-saver.</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 text-red-600 rounded-2xl border border-red-100 text-sm font-bold flex items-center gap-2">
              <ShieldCheck size={18} /> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div className="space-y-1">
                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Full Name</label>
                <input name="full_name" placeholder="John Doe" onChange={handleChange} required className="w-full p-4 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all font-medium" />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Email Address</label>
                <input name="email" type="email" placeholder="john@example.com" onChange={handleChange} required className="w-full p-4 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all font-medium" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div className="space-y-1">
                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Phone Number</label>
                <input name="phone" placeholder="+91 9876543210" onChange={handleChange} required className="w-full p-4 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all font-medium" />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Create Password</label>
                <input name="password" type="password" placeholder="••••••••" onChange={handleChange} required className="w-full p-4 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all font-medium" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div className="space-y-1">
                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Date of Birth</label>
                <input name="dob" type="date" onChange={handleChange} required className="w-full p-4 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all font-medium" />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Your City</label>
                <input name="city" placeholder="Hyderabad" onChange={handleChange} required className="w-full p-4 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all font-medium" />
              </div>
            </div>
            
            <div className="space-y-1">
              <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">I want to join as a</label>
              <select name="role" onChange={handleChange} className="w-full p-4 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all font-medium appearance-none">
                <option value="donor">Volunteer Donor</option>
                <option value="patient">Thalassemia Patient</option>
                <option value="volunteer">Network Coordinator (Volunteer)</option>
              </select>
            </div>

            {(formData.role === 'donor' || formData.role === 'patient') && (
              <div className="space-y-1">
                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Blood Group</label>
                <select name="blood_group" onChange={handleChange} required className="w-full p-4 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all font-medium appearance-none">
                  <option value="">Select Blood Group</option>
                  {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map(bg => (
                    <option key={bg} value={bg}>{bg}</option>
                  ))}
                </select>
              </div>
            )}

            {formData.role === 'donor' && (
              <div className="space-y-1">
                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Last Donation Date (Optional)</label>
                <input name="last_donation_date" type="date" onChange={handleChange} className="w-full p-4 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all font-medium" />
              </div>
            )}

            {formData.role === 'patient' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div className="space-y-1">
                  <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Frequency (Days)</label>
                  <input name="frequency_in_days" type="number" placeholder="21" onChange={handleChange} required className="w-full p-4 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all font-medium" />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Next Transfusion Date</label>
                  <input name="expected_next_transfusion_date" type="date" onChange={handleChange} required className="w-full p-4 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all font-medium" />
                </div>
              </div>
            )}

            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full bg-primary text-white p-5 rounded-2xl font-black uppercase tracking-widest hover:bg-secondary transition-all shadow-xl shadow-red-100 flex items-center justify-center gap-3 disabled:opacity-50"
            >
              {isLoading ? (
                <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <>Register Now <Sparkles size={20} /></>
              )}
            </button>
          </form>
          
          <p className="mt-8 text-center text-gray-400 font-medium">
            Already a member? <a href="/login" className="text-primary font-bold hover:underline">Login here</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;

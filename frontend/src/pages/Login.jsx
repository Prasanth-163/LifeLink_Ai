import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await axios.post('http://localhost:5000/api/auth/login', formData);
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('role', response.data.role);
      localStorage.setItem('user', JSON.stringify({
        user_id: response.data.user_id,
        role: response.data.role
      }));
      localStorage.setItem('user_id', response.data.user_id);
      
      // Navigate to respective dashboard
      navigate(`/${response.data.role}-dashboard`);
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed');
    }
  };

  return (
    <div className="max-w-md mx-auto mt-20 p-6 bg-white rounded-lg shadow-xl">
      <h2 className="text-2xl font-bold text-center text-primary mb-6">Welcome Back</h2>
      {error && <div className="mb-4 text-red-500 text-sm text-center">{error}</div>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <input name="email" type="email" placeholder="Email" onChange={handleChange} required className="w-full p-2 border rounded" />
        <input name="password" type="password" placeholder="Password" onChange={handleChange} required className="w-full p-2 border rounded" />
        <button type="submit" className="w-full bg-primary text-white p-2 rounded hover:bg-secondary font-bold transition">Login</button>
      </form>
      <p className="mt-4 text-center text-sm">
        Don't have an account? <a href="/register" className="text-primary hover:underline">Register</a>
      </p>
    </div>
  );
};

export default Login;

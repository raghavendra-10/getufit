'use client';
import React, { useState } from 'react';
import { onboardUser } from '../../services/api';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useRouter } from 'next/navigation';

const Onboarding = () => {
  const [formData, setFormData] = useState({
    user_id: '',
    name: '',
    age: '',
    height: '',
    weight: '',
    goal: '',
    health_issues: '',
    experience: '',
  });

  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await onboardUser(formData);
      toast.success('User onboarded successfully!');
      router.push('/activities');
      console.log('Response:', response);
    } catch (error) {
      toast.error(error.message || 'Failed to onboard user');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className=" max-h-[750px] bg-gradient-to-r from-blue-100 to-purple-100 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="bg-white p-6 sm:p-8 rounded-lg shadow-lg w-full max-w-sm sm:max-w-md md:max-w-lg">
        <ToastContainer />
        {/* <h1 className="text-2xl sm:text-3xl font-bold mb-6 text-center text-blue-600">Fitness Onboarding</h1> */}
        <form onSubmit={handleSubmit} className="space-y-2  h-[700px]">
          {/* User ID */}
          <div>
            <label className="block text-sm font-medium text-gray-900">User ID</label>
            <input
              type="text"
              name="user_id"
              placeholder="Enter User ID"
              value={formData.user_id}
              onChange={handleChange}
              className="mt-1 w-full p-2 sm:p-3 border text-black border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-900">Name</label>
            <input
              type="text"
              name="name"
              placeholder="Enter Name"
              value={formData.name}
              onChange={handleChange}
              className="mt-1 w-full p-2 sm:p-3 border text-black border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          {/* Age */}
          <div>
            <label className="block text-sm font-medium text-gray-900">Age</label>
            <input
              type="number"
              name="age"
              placeholder="Enter Age"
              value={formData.age}
              onChange={handleChange}
              className="mt-1 w-full p-2 sm:p-3 border text-black border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          {/* Height */}
          <div>
            <label className="block text-sm font-medium text-gray-900">Height (in feet)</label>
            <input
              type="text"
              name="height"
              placeholder="e.g., 5.9"
              value={formData.height}
              onChange={handleChange}
              className="mt-1 w-full p-2 sm:p-3 border text-black border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          {/* Weight */}
          <div>
            <label className="block text-sm font-medium text-gray-900">Weight (in lbs)</label>
            <input
              type="number"
              name="weight"
              placeholder="e.g., 160"
              value={formData.weight}
              onChange={handleChange}
              className="mt-1 w-full p-2 sm:p-3 border text-black border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          {/* Goal */}
          <div>
            <label className="block text-sm font-medium text-gray-900">Fitness Goal</label>
            <select
              name="goal"
              value={formData.goal}
              onChange={handleChange}
              className="mt-1 w-full p-2 sm:p-3 border text-black border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select Fitness Goal</option>
              <option value="weight loss">Weight Loss</option>
              <option value="muscle gain">Muscle Gain</option>
              <option value="endurance">Endurance</option>
              <option value="general fitness">General Fitness</option>
            </select>
          </div>

          {/* Health Issues */}
          <div>
            <label className="block text-sm font-medium text-gray-900">Health Issues</label>
            <input
              type="text"
              name="health_issues"
              placeholder="e.g., none"
              value={formData.health_issues}
              onChange={handleChange}
              className="mt-1 w-full p-2 sm:p-3 border text-black border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Experience */}
          <div>
            <label className="block text-sm font-medium text-gray-900">Experience Level</label>
            <select
              name="experience"
              value={formData.experience}
              onChange={handleChange}
              className="mt-1 w-full p-2 sm:p-3 border text-black border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select Experience Level</option>
              <option value="newbie">Newbie</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className={`w-full py-2 sm:py-3 text-white font-semibold rounded-lg ${loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'}`}
            disabled={loading}
          >
            {loading ? 'Submitting...' : 'Submit'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Onboarding;

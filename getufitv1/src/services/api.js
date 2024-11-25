import axios from 'axios';

const BASE_URL = 'https://flask-app-58742455872.us-central1.run.app'; // Replace with your backend URL

export const onboardUser = async (userData) => {
  try {
    const response = await axios.post(`${BASE_URL}/onboard_user`, userData, {
      headers: { 'Content-Type': 'application/json' },
    });
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  } catch (error) {
    throw error.response?.data || 'An error occurred while onboarding the user';
  }
};

// services/api.ts
import axios from 'axios';

// 1. Create minimal Axios instance
const apiClient = axios.create({
  baseURL: '/api', // Direct backend URL
});

export const initiateGoogleAuth = async () => {
  try {
    window.location.href = '/api/auth/login';
    // const response = await apiClient.get('/auth/login');
    
    // Redirect user to Google's OAuth page
    
  } catch (error) {
    console.error('Failed to initiate Google auth:', error);
    throw error; // Re-throw for component handling
  }
};
// services/api.ts
import axios from 'axios';

// 1. Create minimal Axios instance
const apiClient = axios.create({
  baseURL: '/api', // Direct backend URL
});

export const initiateGoogleAuth = async () => {
  try {
    console.log('/api/auth/login')
    window.location.href = '/api/auth/login';

    // const response = await apiClient.get('/auth/login');
    
    // Redirect user to Google's OAuth page
    
  } catch (error) {
    console.error('Failed to initiate Google auth:', error);
    throw error; // Re-throw for component handling
  }
};

export const emailService = {
  checkConnection: async () => {
    try {
      const response = await apiClient.get('/emails');
      return response.data;
    } catch (error) {
      console.error('Connection check failed:', error);
      throw error;
    }
  },

  getEmailAddress: async () => {
    try {
      const response = await apiClient.get('/emails/address');
      return response.data;
    } catch (error) {
      console.error('Failed to get email address:', error);
      throw error;
    }
  },

  getUserCredentials: async () => {
    try {
      const response = await apiClient.get('/emails/creds');
      return response.data;
    } catch (error) {
      console.error('Failed to get user credentials:', error);
      throw error;
    }
  },

  getMessage: async (messageId: string) => {
    try {
      const response = await apiClient.get(`/emails/messages/${messageId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get message:', error);
      throw error;
    }
  },

  initializeUserFolders: async () => {
    try {
      const response = await apiClient.post('/emails/setfolders');
      return response.data;
    } catch (error) {
      console.error('Failed to initialize folders:', error);
      throw error;
    }
  },

  checkEmailsForScams: async (maxEmails = 10) => {
    try {
      const response = await apiClient.get('/emails/check', {
        params: { max: maxEmails }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to check emails for scams:', error);
      throw error;
    }
  },

  getRawEmails: async (maxEmails = 10) => {
    try {
      const response = await apiClient.get('/emails/raw', {
        params: { max: maxEmails }
      });
      
      // Transformation logic
      const formattedEmails = response.data.map(email => {
        // Extract name and email from "From" field using regex
        const fromMatch = email.From.match(/(.*?)\s*<([^>]+)>/);
        const [name, emailAddress] = fromMatch 
          ? [fromMatch[1].trim(), fromMatch[2]]
          : ['Unknown Sender', 'unknown@example.com'];

        return {
          id: email.id || crypto.randomUUID(), // Use existing ID or generate new
          name: name,
          email: emailAddress,
          subject: email.Subject,
          text: email.Body,
          date: new Date(email['Date Received']).toISOString(),
          read: false, // Default to unread
          labels: [] // Initialize empty labels array
        };
      });

      return formattedEmails;
      console.log(response.data)
      return response.data;
    } catch (error) {
      console.error('Failed to fetch raw emails:', error);
      throw error;
    }
  }
};
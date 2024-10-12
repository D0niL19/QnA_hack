import axios from 'axios';

const API_URL = 'http://176.123.163.187:8080'; // Replace with your actual API endpoint

const botService = {
  sendMessage: async (message) => {
    try {
      const response = await axios.post(`${API_URL}/question`, { "question": message });
      return response.data.answer;
    } catch (error) {
      console.error('Error sending message to bot:', error);
      throw error;
    }
  },
  sendMessageHistory: async (history) => {
    console.log('Sending message history:', history);
    try {
      const response = await axios.post(`${API_URL}/message-history`, history);
      return response.data; // Возвращаем ответ от сервера, если нужно
    } catch (error) {
      console.error('Error sending message history:', error);
      throw error;
    }
  },
};

export default botService;

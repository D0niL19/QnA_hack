import axios from 'axios';

const API_URL = 'http://localhost:8080'; // Replace with your actual API endpoint

const botService = {
  send_message: async (message) => {
    try {
      const response = await axios.post(`${API_URL}/question`, { "question": message });
      return response.data.answer;
    } catch (error) {
      console.error('Error sending message to bot:', error);
      throw error;
    }
  },
  update_mark: async (history) => {
    console.log('Sending message history:', history);
    try {
      const response = await axios.post(`${API_URL}/update_mark`, history, {
        headers: {
          'Content-Type': 'application/json'
          }
        });
      return response.data; // Возвращаем ответ от сервера, если нужно
    } catch (error) {
      console.error('Error sending message history:', error);
      throw error;
    }
  },

  download_chat_history: async () => {
    try {
      const response = await axios.get(`${API_URL}/download`, {
        responseType: 'blob', // Важно указать responseType 'blob'
      });
      
      // Создаем ссылку на blob и скачиваем файл
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'chat_history.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading chat history:', error);
      throw error;
    }
  },

};

export default botService;

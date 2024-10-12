import { useState, useCallback, useEffect } from 'react';
import botService from '../services/botService';

const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [rating, setRating] = useState(null);

  //const addWelcomeMessage = useCallback(() => {
  //  const welcomeMessage = {
  //    text: 'Привет! Как я могу помочь вам сегодня?',
  //    sender: 'bot',
  //    timestamp: new Date().toISOString(),
  //  };
  //  setMessages((prevMessages) => [...prevMessages, welcomeMessage]);
  //}, []);
  //
  // Эффект для добавления приветственного сообщения при первом рендере
  //useEffect(() => {
  //  addWelcomeMessage();
  //}, [addWelcomeMessage]);

  const sendMessage = useCallback(async (text) => {
    if (!text.trim()) return;

    const userMessage = {
      text,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setIsLoading(true);

    try {
      const botResponse = await botService.sendMessage(text);
      const botMessage = {
        text: botResponse,
        sender: 'bot',
        timestamp: new Date().toISOString(),
      };

      setMessages((prevMessages) => [...prevMessages, botMessage]);
      const history = {
        question: userMessage.text,
        answer: botMessage.text,
        mark: rating || 0,
      };
      await botService.sendMessageHistory(history);
    } catch (error) {
      console.error('Error getting bot response:', error);
      const errorMessage = {
        text: 'Извините, я получил ошибку, попробуйте заново.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);

    } finally {
      setIsLoading(false);
    }
  }, [rating]);

  const handleRating = useCallback((ratingValue) => {
    console.log('Оценка получена:', ratingValue);
    setRating(ratingValue);
    // Здесь можно добавить логику для обработки рейтинга, например, отправить на сервер или сохранить в состоянии
  }, []);

  const startNewChat = useCallback(() => {
    setMessages([]);
    setRating(null); 
    //addWelcomeMessage();
  })//, [addWelcomeMessage]);

  return {
    messages,
    isLoading,
    sendMessage,
    startNewChat,
    handleRating
  };
};

export default useChat;
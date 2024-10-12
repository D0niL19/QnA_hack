import { useState, useCallback, useEffect } from 'react';
import botService from '../services/botService'; // Импорт сервиса для общения с ботом

const useChat = () => {
  const [messages, setMessages] = useState([]); // Состояние для хранения сообщений
  const [isLoading, setIsLoading] = useState(false); // Состояние загрузки
  const [botResponse, setBotResponse] = useState(null); // Ответ от бота
  const [Message, setMessage] = useState(null); 
  const [rating, setRating] = useState(null); // Состояние оценки
  const [ratedMessageId, setRatedMessageId] = useState(null); // Состояние для хранения ID сообщения, которое было оценено
  const [lastBotMessageId, setLastBotMessageId] = useState(null); 



  const sendMessage = useCallback(async (text) => {
    if (!text.trim()) return; // Проверка на пустое сообщение

    const userMessage = {
      text,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };
    setMessage(userMessage.text); // Сохраняем сообщение пользователя

    setMessages((prevMessages) => [...prevMessages, userMessage]); // Обновляем список сообщений
    setIsLoading(true); // Устанавливаем состояние загрузки

    try {
      const response = await botService.send_message(text); // Отправка сообщения боту
      setBotResponse(response); // Сохраняем ответ от бота
      const botMessage = {
        text: response,
        sender: 'bot',
        timestamp: new Date().toISOString(),
      };

      setMessages((prevMessages) => [...prevMessages, botMessage]); // Добавляем ответ бота в сообщения
      
    } catch (error) {
      console.error('Error getting bot response:', error); // Логируем ошибку
      const errorMessage = {
        text: 'Извините, я получил ошибку, попробуйте заново.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]); // Добавляем сообщение об ошибке

    } finally {
      setIsLoading(false); // Сбрасываем состояние загрузки
    }
    setRating(null);
    setRatedMessageId(null); 
  }, []);

  const handleRating = useCallback(async (ratingValue, messageId) => {
    console.log('Оценка получена:', ratingValue); // Логируем оценку
    setRating(ratingValue); // Сохраняем оценку
    setRatedMessageId(messageId); 
    const history = {
        question: Message, // Вопрос пользователя
        answer: botResponse, // Ответ бота
        mark: ratingValue || 0, // Оценка
    };
    try {
        await botService.update_mark(history); // Отправка истории взаимодействия
        console.log('История успешно отправлена'); // Логируем успешный ответ от сервера
    } catch (error) {
        console.error('Ошибка при отправке истории:', error); // Обработка ошибки
    }
  }, [Message, botResponse]); // Зависимости

  const startNewChat = useCallback(() => {
    setMessages([]); // Сбрасываем сообщения
    setRating(null); // Сбрасываем оценку
  }, []);

  const downloadChatHistory = useCallback(async () => {
    try {
      await botService.download_chat_history();
    } catch (error) {
      console.error('Error downloading chat history:', error);
      throw error;
    }
  }, []);

  useEffect(() => {
    // Обновляем lastBotMessageId при изменении сообщений
    const lastBotMessage = messages.filter(m => m.sender === 'bot').pop();
    if (lastBotMessage) {
      setLastBotMessageId(messages.indexOf(lastBotMessage));
    }

    const formatBoldText = (text) => {
      return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    };

    const messageTextElements = document.querySelectorAll('.message-text');
    messageTextElements.forEach(element => {
      element.innerHTML = formatBoldText(element.innerHTML);
    });
    
  }, [messages]);

  return {
    messages,
    isLoading,
    sendMessage,
    startNewChat,
    handleRating,
    downloadChatHistory,
    rating,
    ratedMessageId,
    lastBotMessageId,
  };
};

export default useChat; // Экспорт хука
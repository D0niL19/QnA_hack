import React from 'react';
import ChatWindow from '../ChatWindow/ChatWindow'; // Компонент для отображения сообщений
import UserInput from '../UserInput/UserInput'; // Компонент для ввода сообщений
import useChat from '../../hooks/useChat'; // Хук для управления состоянием чата
import './ChatInterface.css'; // Стили для интерфейса

const ChatInterface = () => {
  const {
    messages, // Сообщения чата
    isLoading, // Состояние загрузки
    sendMessage, // Функция для отправки сообщения
    startNewChat, // Функция для начала нового чата
    handleRating, // Функция для обработки рейтинга
  } = useChat();

  const handleSendMessage = (message) => {
    sendMessage(message); // Отправка сообщения
  };

  const handleNewChat = () => {
    startNewChat(); // Начало нового чата
  };

  return (
    <div className="chat-interface">
      <ChatWindow 
        className="chat-window" 
        messages={messages} 
        isLoading={isLoading} 
        onNewChat={handleNewChat} 
        onRate={handleRating} 
      />
      <UserInput 
        className="user-input" 
        onSendMessage={handleSendMessage} 
      />
    </div>
  );
};

export default ChatInterface; // Экспорт компонента
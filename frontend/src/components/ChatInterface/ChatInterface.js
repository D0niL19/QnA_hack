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
    downloadChatHistory, // Функция для загрузки истории чата
    lastBotMessageId, // ID последнего сообщения от бота
  } = useChat();

  const handleSendMessage = (message) => {
    sendMessage(message); // Отправка сообщения
  };

  const handleNewChat = () => {
    startNewChat(); // Начало нового чата
  };
  
  const onDownloadHistory = async () => {
    try {
      await downloadChatHistory();
    } catch (error) {
      console.error('Error downloading chat history:', error);
      // Здесь можно добавить обработку ошибки, например, показать уведомление пользователю
    }
  };

  return (
    <div className="chat-interface">
      <button className="download-history" onClick={onDownloadHistory}>
          Скачать чат
      </button>
      <ChatWindow 
        className="chat-window" 
        messages={messages} 
        isLoading={isLoading} 
        onNewChat={handleNewChat} 
        onRate={handleRating}
        lastBotMessageId={lastBotMessageId}
      />
      <UserInput 
        className="user-input" 
        onSendMessage={handleSendMessage} 
      />
    </div>
  );
};

export default ChatInterface; // Экспорт компонента
import React, { useEffect, useRef } from 'react';
import Message from '../Message/Message'; // Компонент для отображения отдельного сообщения
import './ChatWindow.css'; // Стили для окна чата

const ChatWindow = ({ messages, isLoading, onNewChat, onRate, lastBotMessageId, downloadChatHistory }) => {
  const messagesEndRef = useRef(null); // Ссылка для прокрутки к последнему сообщению

  // Прокручиваем вниз при изменении сообщений
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' }); // Плавная прокрутка
    }
  }, [messages]); // Зависимость от messages

  const onDownloadHistory = async () => {
    try {
      await downloadChatHistory();
    } catch (error) {
      console.error('Error downloading chat history:', error);
      // Здесь можно добавить обработку ошибки, например, показать уведомление пользователю
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-controls">
        <button className="download-history" onClick={onDownloadHistory} disabled={isLoading}>
          Скачать чат
        </button>
        <button className="new-chat-button" onClick={onNewChat} disabled={isLoading}>
          Начать новый чат
        </button>
      </div>
      <div className="chat-messages">
        {messages.map((message, index) => (
          <Message key={index} message={message} onRate={onRate} messageId={index} lastBotMessageId={lastBotMessageId} isLoading={isLoading}   /> // Отображаем сообщения
        ))}
        {isLoading && <div className="loading-indicator">Бот печатает...</div>} {/* Индикатор загрузки */}
        <div ref={messagesEndRef} /> {/* Элемент для прокрутки */}
      </div>
    </div>
  );
};

export default ChatWindow; // Экспорт компонента

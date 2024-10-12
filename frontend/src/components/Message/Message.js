import React, { useState } from 'react';
import './Message.css';

const Message = ({ message, onRate }) => {
  const { text, sender, timestamp } = message;

  const messageClass = sender === 'user' ? 'message-user' : 'message-bot';

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Состояние для оценки (видно только для сообщений от бота)
  const [rating, setRating] = useState(0);
  const [rateCheck, setRateCheck] = useState(false);

  // Обработчик клика по кружочкам
  const handleRatingClick = (value) => {
    setRating(value);
    setRateCheck(true);
    onRate(value);
  };

  return (
    <div className={`message ${messageClass}`}>
      <div className="message-content">
        <p className="message-text">{text}</p>
        <span className="message-timestamp">{formatTimestamp(timestamp)}</span>
      </div>

      {rateCheck ? ( // Условие для отображения благодарности
        <div className="rating-result">Спасибо за оценку!</div>
      ) : (
        sender === 'bot' && ( // Условие для отображения оценок
          <div className="rating-container">
            <span className="rating-text">Оцените ответ: </span>
            <div className="rating-circles">
              {[1, 2, 3, 4, 5].map((value) => (
                <span
                  key={value}
                  className={`rating-circle ${rating >= value ? 'rated' : ''}`}
                  onClick={() => handleRatingClick(value)}
                >
                  ●
                </span>
              ))}
            </div>
          </div>
        )
      )}

      <div className="message-sender">{sender === 'user' ? 'Вы' : 'Бот'}</div>
    </div>
  );
};

export default Message;
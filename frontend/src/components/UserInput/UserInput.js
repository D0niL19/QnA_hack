import React, { useState } from 'react';
import './UserInput.css'; // Стили для поля ввода

const UserInput = ({ onSendMessage }) => {
  const [message, setMessage] = useState(''); // Состояние для сообщения

  const handleInputChange = (event) => {
    setMessage(event.target.value); // Обновление состояния при вводе
  };

  const handleKeyDown = (event) => {
    // Отправка сообщения при нажатии Enter, если не удерживается Shift
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault(); // Предотвращаем переход на новую строку
      handleSubmit(); // Вызываем отправку
    }
  };

  const handleSubmit = (event) => {
    if (event) {
      event.preventDefault(); // Предотвращаем стандартное поведение формы
    } 
    if (message.trim()) {
      onSendMessage(message); // Отправка сообщения
      setMessage(''); // Очистка поля после отправки
    }
  };

  return (
    <form className="user-input" onSubmit={handleSubmit}>
      <textarea
        type="text"
        value={message}
        onChange={handleInputChange} // Обработчик изменения текста
        onKeyDown={handleKeyDown} // Обработчик нажатий клавиш
        placeholder="Спросите что нибудь..."
        className="user-input-field"
      />
      <button type="submit" className="send-button">
        Отправить
      </button>
    </form>
  );
};

export default UserInput; // Экспорт компонента
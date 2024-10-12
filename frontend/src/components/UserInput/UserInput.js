import React, { useState } from 'react';
import './UserInput.css';

const UserInput = ({ onSendMessage }) => {
  const [message, setMessage] = useState('');

  const handleInputChange = (event) => {
    setMessage(event.target.value);
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault(); // Prevent default behavior of Enter key
      handleSubmit(); // Call submit function
    }
  };

  const handleSubmit = (event) => {
    if (event) {
      event.preventDefault(); // Prevent default form submission
    } // Check if there is an event passed
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <form className="user-input" onSubmit={handleSubmit}>
      <textarea
        type="text"
        value={message}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder="Спросите что нибудь..."
        className="user-input-field"
      />
      <button type="submit" className="send-button">
        Отправить
      </button>
    </form>
  );
};

export default UserInput;
import React from 'react';
import ChatWindow from '../ChatWindow/ChatWindow';
import UserInput from '../UserInput/UserInput';
import useChat from '../../hooks/useChat';
import './ChatInterface.css';

const ChatInterface = () => {
  const {
    messages,
    isLoading,
    sendMessage,
    startNewChat,
    handleRating,
  } = useChat();

  const handleSendMessage = (message) => {
    sendMessage(message);
  };

  const handleNewChat = () => {
    startNewChat();
  };

  return (
    <div className="chat-interface">
      <ChatWindow className="chat-window" 
        messages={messages} 
        isLoading={isLoading} 
        onNewChat={handleNewChat}
        onRate={handleRating}
      />
      <UserInput className="user-input" onSendMessage={handleSendMessage} />
    </div>
  );
};

export default ChatInterface;
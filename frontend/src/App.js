import React from 'react';
import ChatInterface from './components/ChatInterface/ChatInterface';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>BLESSED.</h1>
      </header>
      <main className="App-main">
        <ChatInterface />
      </main>
      <footer className="App-footer">
        <p>© 2024 AI чат бот. Команда BLESSED.</p>
      </footer>
    </div>
  );
}

export default App;
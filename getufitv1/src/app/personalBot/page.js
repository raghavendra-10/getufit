'use client';

import React, { useState, useEffect } from 'react';

const PersonalBot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const userid = JSON.parse(localStorage.getItem('user')).user_data.user_id;
  const patientId = userid;

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessage = { sender: 'user', text: input };
    setMessages([...messages, newMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('https://rag-58742455872.us-central1.run.app/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          patient_id: patientId,
          query: input,
        }),
      });

      const data = await response.json();

      if (data.response) {
        // Check if the response contains JSON
        const isJsonResponse = data.response.trim().startsWith('```json');
        if (isJsonResponse) {
          // Parse and format the JSON response
          const jsonData = data.response
            .replace('```json', '')
            .replace('```', '');
          const formattedData = formatJsonResponse(JSON.parse(jsonData));
          setMessages((prev) => [
            ...prev,
            { sender: 'bot', text: formattedData },
          ]);
        } else {
          setMessages((prev) => [
            ...prev,
            { sender: 'bot', text: data.response },
          ]);
        }
      } else {
        setMessages((prev) => [
          ...prev,
          { sender: 'bot', text: 'Sorry, something went wrong.' },
        ]);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => [
        ...prev,
        { sender: 'bot', text: 'Unable to connect to the server.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const formatJsonResponse = (data) => {
    return data
      .map(
        (day) =>
          `**${day.day} (${day.focus})**:\n${day.exercises
            .map(
              (exercise) =>
                `- ${exercise.name}: ${exercise.sets} sets of ${exercise.reps} reps (Rest: ${exercise.rest} seconds)${
                  exercise.notes ? `\n  Notes: ${exercise.notes}` : ''
                }`
            )
            .join('\n')}`
      )
      .join('\n\n');
  };

  const handleInputChange = (e) => setInput(e.target.value);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div className="flex text-black flex-col h-[780px]">
      {/* Header */}
      <div className="p-4 bg-blue-500 text-white text-lg font-semibold">
        Personal Chatbot
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 ">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`mb-2 p-2 rounded-lg ${
              msg.sender === 'user' ? 'bg-blue-200 text-right' : 'bg-gray-200'
            }`}
          >
            {msg.text.split('\n').map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        ))}
        {loading && (
          <div className="mb-2 p-2 rounded-lg bg-gray-200">Typing...</div>
        )}
      </div>

      {/* Input Field */}
      <div className="p-4  flex">
        <input
          type="text"
          value={input}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          className="flex-1 border border-gray-300 p-2 rounded-l-lg focus:outline-none"
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="bg-blue-500 text-white px-4 rounded-r-lg hover:bg-blue-600 transition disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default PersonalBot;

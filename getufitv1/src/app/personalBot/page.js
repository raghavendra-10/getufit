'use client';

import React, { useState, useEffect, useRef } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const PersonalBot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  const messagesEndRef = useRef(null);

  // Retrieve user ID from localStorage safely
  const getUserId = () => {
    try {
      const user = JSON.parse(localStorage.getItem('user'));
      return user?.user_data?.user_id || null;
    } catch (error) {
      console.error('Error parsing user data:', error);
      return null;
    }
  };

  const patientId = getUserId();

  useEffect(() => {
    if (!patientId) {
      toast.error('User not found. Please onboard again.');
      // Optionally, redirect to onboarding page
    }
  }, [patientId]);

  // Function to scroll to the latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) {
      toast.error('Please type a message!');
      return;
    }

    const newMessage = { sender: 'user', text: input };
    setMessages((prev) => [...prev, newMessage]);
    setInput('');
    setLoading(true);

    try {
      if (!patientId) {
        throw new Error('User not found. Please onboard again.');
      }

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

      if (!response.ok) {
        throw new Error('Failed to fetch bot response');
      }

      const data = await response.json();

      if (data.response) {
        // Check if the response contains JSON
        const isJsonResponse = data.response.trim().startsWith('```json');
        if (isJsonResponse) {
          // Parse and format the JSON response
          const jsonData = data.response.replace('```json', '').replace('```', '');
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
      toast.error(error.message || 'Unable to connect to the server.');
      console.error('Error fetching bot response:', error);
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
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
      <ToastContainer />
      <header className="w-full max-w-7xl mb-8">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-center text-blue-800">
          Get<span className="text-orange-400">U</span>Fit
        </h1>
      </header>

      <div className="w-full md:pb-24 max-w-4xl bg-white shadow-lg rounded-lg flex flex-col h-[700px]">
        {/* Chat Header */}
        <h2 className="text-3xl font-bold text-center text-blue-600 py-4 border-b border-gray-200">
          Personal Chatbot <span className='text-sm text-black'>based on your own data</span>
        </h2>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 ? (
            <p className="text-center text-gray-600">
              Start the conversation by typing your query below.
            </p>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${
                    msg.sender === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`p-3 rounded-lg max-w-md ${
                      msg.sender === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-black'
                    }`}
                  >
                    {msg.text.split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="p-3 rounded-lg bg-gray-200 text-black">
                    Typing...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Field */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={input}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={sendMessage}
              disabled={loading}
              className={`px-6 py-3 rounded-lg text-white font-semibold ${
                loading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PersonalBot;

'use client';

import React, { useState } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const ChatPage = () => {
    const [userMessage, setUserMessage] = useState('');
    const [conversation, setConversation] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleSendMessage = async () => {
        if (!userMessage.trim()) {
            toast.error('Please type a message!');
            return;
        }

        const formattedQuery = `${userMessage}`;

        setConversation((prev) => [
            ...prev,
            { sender: 'user', text: userMessage },
        ]);

        setUserMessage('');
        setLoading(true);

        try {
            const user = JSON.parse(localStorage.getItem('user'));
            if (!user) {
                throw new Error('User not found. Please onboard again.');
            }

            const response = await fetch('https://flask-app-58742455872.us-central1.run.app/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user.user_data.user_id,
                    query: formattedQuery,
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to fetch bot response');
            }

            const data = await response.json();

            setConversation((prev) => [
                ...prev,
                { sender: 'bot', text: data.response },
            ]);
        } catch (error) {
            toast.error(error.message || 'Error sending message. Please try again.');
            console.error('Error fetching bot response:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <div className="min-h-screen  bg-slate-100 flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
            <ToastContainer />
            <header className="w-full max-w-7xl mb-8">
                <h1 className="text-4xl sm:text-5xl font-extrabold text-center text-blue-800">
                    Get<span className="text-orange-400">U</span>Fit
                </h1>
            </header>

            <div className="w-full md:pb-24 max-w-4xl bg-white shadow-lg rounded-lg flex flex-col h-[700px]">
                <h2 className="text-3xl font-bold text-center text-blue-600 py-4 border-b border-gray-200">
                    Chat with Your Fitness Bot
                </h2>

                <div className="flex-1 overflow-auto p-4">
                    {conversation.length === 0 ? (
                        <p className="text-center text-gray-600">
                            Start the conversation by typing your query below.
                        </p>
                    ) : (
                        <div className="space-y-4">
                            {conversation.map((message, index) => (
                                <div
                                    key={index}
                                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`p-3 rounded-lg max-w-md ${
                                            message.sender === 'user'
                                                ? 'bg-blue-500 text-white'
                                                : 'bg-gray-200 text-black'
                                        }`}
                                    >
                                        {message.text}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="p-4 border-t border-gray-200">
                    <div className="flex items-center space-x-2">
                        <input
                            type="text"
                            placeholder="Type your message..."
                            value={userMessage}
                            onChange={(e) => setUserMessage(e.target.value)}
                            onKeyPress={handleKeyPress}
                            className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button
                            onClick={handleSendMessage}
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

export default ChatPage;

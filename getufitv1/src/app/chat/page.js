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

        const formattedQuery = `${userMessage}. Give in 30 words.`;

        setConversation((prev) => [
            ...prev,
            { sender: 'user', text: userMessage },
        ]);

        setUserMessage('');
        setLoading(true);

        try {
            const user = JSON.parse(localStorage.getItem('user'));
            const response = await fetch('https://flask-app-58742455872.us-central1.run.app/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user.user_data.user_id, // Replace with dynamic user ID if available
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
            toast.error('Error sending message. Please try again.');
            console.error('Error fetching bot response:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="h-[730px] bg-gradient-to-r text-black flex flex-col p-4">
            <ToastContainer />
            <h1 className="text-3xl font-bold text-center text-blue-600 mb-6">Chat with Your Fitness Bot</h1>

            <div className="flex-1 overflow-auto bg-white shadow-lg rounded-lg p-4">
                {conversation.length === 0 ? (
                    <p className="text-center text-gray-600">Start the conversation by typing your query below.</p>
                ) : (
                    <div className="space-y-4">
                        {conversation.map((message, index) => (
                            <div
                                key={index}
                                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'
                                    }`}
                            >
                                <div
                                    className={`p-3 rounded-lg max-w-md ${message.sender === 'user'
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

            <div className="mt-4 flex items-center space-x-2">
                <input
                    type="text"
                    placeholder="Type your message..."
                    value={userMessage}
                    onChange={(e) => setUserMessage(e.target.value)}
                    className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                    onClick={handleSendMessage}
                    disabled={loading}
                    className={`px-4 py-2 rounded-lg text-white ${loading ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'
                        }`}
                >
                    {loading ? 'Sending...' : 'Send'}
                </button>
            </div>
        </div>
    );
};

export default ChatPage;

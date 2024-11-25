'use client';

import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const Files = () => {
  const [loading, setLoading] = useState(false);
  const [fileUrl, setFileUrl] = useState(null);

  useEffect(() => {
    const fetchFile = async () => {
      setLoading(true);
      try {
        // Fetch user ID from local storage
        const user = JSON.parse(localStorage.getItem('user'));
        if (!user) {
          toast.error('User not found. Please onboard again.');
          return;
        }

        const response = await fetch('https://flask-app-58742455872.us-central1.run.app/generate_pdf', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ user_id: user.user_data.user_id }),
        });

        if (!response.ok) {
          throw new Error('No chat history is found');
        }

        const data = await response.json();
        setFileUrl(data.pdf_url);
        toast.success('File fetched successfully!');
      } catch (error) {
        toast.error(error.message || 'Failed to load files');
        console.error('Error fetching file:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFile();
  }, []);

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
      <ToastContainer />
      <h1 className="text-4xl sm:text-5xl font-extrabold mb-8 text-center text-blue-800">
        Get<span className="text-orange-400">U</span>Fit
      </h1>

      <div className="w-full max-w-md">
        <h2 className="text-3xl font-bold text-center text-blue-600 mb-6">Your Files</h2>

        {loading ? (
          <div className="flex justify-center items-center min-h-[50vh]">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-600"></div>
          </div>
        ) : fileUrl ? (
          <div className="flex flex-col items-center bg-white p-6 rounded-lg shadow-lg">
            <p className="text-lg text-gray-800 mb-4">Your chat history is ready to download:</p>
            <a
              href={fileUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg"
            >
              Download Chat History
            </a>
          </div>
        ) : (
          <p className="text-center text-gray-600">No file available. Please try again later.</p>
        )}
      </div>
    </div>
  );
};

export default Files;

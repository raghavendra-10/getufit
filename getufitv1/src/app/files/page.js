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
          throw new Error('Failed to fetch the file');
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
    <div className="min-h-screen bg-gradient-to-r  p-6">
      <ToastContainer />
      <h1 className="text-3xl font-bold text-center text-blue-600 mb-6">Files</h1>

      {loading ? (
        <div className="flex justify-center items-center min-h-[50vh]">
          <div className="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full" />
        </div>
      ) : fileUrl ? (
        <div className="flex justify-center">
          <a
            href={fileUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline text-lg"
          >
            Download chat histrory
          </a>
        </div>
      ) : (
        <p className="text-center text-gray-600">No file available. Please try again later.</p>
      )}
    </div>
  );
};

export default Files;

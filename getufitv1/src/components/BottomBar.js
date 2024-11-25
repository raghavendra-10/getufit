'use client';

import { useRouter } from 'next/navigation';
import React from 'react';
import { FaComments, FaDownload, FaRunning, FaUser } from 'react-icons/fa';

const BottomBar = () => {
  const router = useRouter();

  const onClickChat = () => {
    router.push('/chat');
  };

  const onClickFiles = () => {
    router.push('/files');
  };

  const onClickActivities = () => {
    router.push('/activities');
  };
  const onClickBot = () => {
    router.push('/personalBot');
  }

  return (
    <div className="fixed bottom-0 left-0 w-full bg-white shadow-lg border-t border-gray-200">
      <div className="max-w-7xl  mx-auto p-4 flex justify-center space-x-10">
        {/* Chat Icon */}
        <button
          onClick={onClickChat}
          className="flex flex-col items-center text-gray-600 hover:text-blue-500 transition"
        >
          <FaComments className="text-2xl" />
          <span className="text-sm">Chat</span>
        </button>

        {/* Activities Icon */}
        <button
          onClick={onClickActivities}
          className="flex flex-col items-center text-gray-600 hover:text-orange-500 transition"
        >
          <FaRunning className="text-2xl" />
          <span className="text-sm">Activities</span>
        </button>

        {/* Files Icon */}
        <button
          onClick={onClickFiles}
          className="flex flex-col items-center text-gray-600 hover:text-green-500 transition"
        >
          <FaDownload className="text-2xl" />
          <span className="text-sm">Files</span>
        </button>
        <button
          onClick={onClickBot}
          className="flex flex-col items-center text-gray-600 hover:text-green-500 transition"
        >
          <FaUser className="text-2xl" />
          <span className="text-sm">own Bot</span>
        </button>
      </div>
    </div>
  );
};

export default BottomBar;

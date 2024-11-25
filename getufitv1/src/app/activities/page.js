'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const Activities = () => {
  const [loading, setLoading] = useState(true);
  const [activities, setActivities] = useState([]);
  const [fitnessPlan, setFitnessPlan] = useState({});
  const router = useRouter();

  useEffect(() => {
    // Fetch user ID from localStorage
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) {
      toast.error('User not found. Please onboard again.');
      router.push('/');
      return;
    }

    const fetchFitnessPlan = async () => {
      try {
        const response = await fetch(
          `https://flask-app-58742455872.us-central1.run.app/generate_fitness_plan_from_bigquery?user_id=${user.user_data.user_id}`
        );

        if (!response.ok) {
          throw new Error('Failed to fetch fitness plan');
        }

        const data = await response.json();

        // Parse raw AI response
        const rawResponse = data.raw_ai_response;
        const parsedResponse = JSON.parse(rawResponse.replace(/```json\n|```/g, ''));

        // Set state with parsed data
        setActivities(parsedResponse.activities || []);
        setFitnessPlan(parsedResponse);
        handleSubmit(parsedResponse);
      } catch (error) {
        toast.error(error.message || 'Failed to load activities');
        console.error('Error fetching fitness plan:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFitnessPlan();
  }, []);

  const handleSubmit = async (data) => {
    const user = JSON.parse(localStorage.getItem('user'));
    try {
      const response = await fetch('https://rag-58742455872.us-central1.run.app/add_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: user.user_data.user_id,
          documents: [{ text: data }],
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to add data');
      }

      toast.success('Data added successfully!');
    } catch (error) {
      toast.error(error.message || 'Error adding data');
    }
  };

  return (
    <div className="min-h-screen pb-32 bg-slate-100 flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
      <ToastContainer />
      <h1 className="text-4xl sm:text-5xl font-extrabold mb-8 text-center text-blue-800">
        Get<span className="text-orange-400">U</span>Fit
      </h1>

      {loading ? (
        <div className="flex justify-center items-center min-h-[50vh]">
          <div className="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full" />
        </div>
      ) : activities.length > 0 ? (
        <div className="w-full max-w-7xl">
          <h2 className="text-3xl font-bold text-center text-blue-600 mb-6">Your Weekly Fitness Plan</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {activities.map((activity, index) => (
              <div
                key={index}
                className="bg-white shadow-lg rounded-lg p-6 flex flex-col justify-between"
              >
                <h3 className="text-2xl font-bold text-blue-600">{activity.day}</h3>
                <p className="mt-2">
                  <span className="font-semibold">Focus:</span> {activity.focus}
                </p>
                {activity.exercises && activity.exercises.length > 0 ? (
                  <div className="mt-4">
                    <h4 className="font-semibold text-lg">Exercises:</h4>
                    <ul className="list-disc list-inside mt-2 space-y-2">
                      {activity.exercises.map((exercise, idx) => (
                        <li key={idx}>
                          <p>
                            <strong>{exercise.name}</strong> - {exercise.sets} sets of {exercise.reps} reps
                            (Rest: {exercise.rest}s)
                          </p>
                          {exercise.notes && (
                            <p className="text-sm text-gray-600 mt-1">Notes: {exercise.notes}</p>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <p className="mt-2 text-gray-600">No exercises for this day.</p>
                )}
              </div>
            ))}
          </div>

          {fitnessPlan.nutrition && (
            <div className="mt-8 bg-white p-6 rounded-lg shadow-lg">
              <h2 className="text-2xl font-bold text-blue-600 mb-4">Additional Recommendations</h2>
              <div className="mt-2">
                <h3 className="font-semibold text-lg">Fitness Goal:</h3>
                <p>{fitnessPlan.fitness_goal}</p>
              </div>
              <div className="mt-4">
                <h3 className="font-semibold text-lg">Nutrition:</h3>
                <p>{fitnessPlan.nutrition}</p>
              </div>
            </div>
          )}
        </div>
      ) : (
        <p className="text-center text-gray-600">No activities available. Please try again later.</p>
      )}
    </div>
  );
};

export default Activities;

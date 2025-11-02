import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [redditPosts, setRedditPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/reddit-sentiment')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        setRedditPosts(data);
        setLoading(false);
      })
      .catch(error => {
        setError(error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="App">
        <header className="App-header">
          <p>Loading Reddit sentiment data...</p>
        </header>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App">
        <header className="App-header">
          <p>Error: {error.message}</p>
        </header>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Reddit Sentiment Analysis</h1>
        {redditPosts.length === 0 ? (
          <p>No Reddit posts found. Run the collector to populate the database.</p>
        ) : (
          <div className="posts-container">
            {redditPosts.map(post => (
              <div key={post.id} className="post-card">
                <h2>{post.title}</h2>
                <p>Sentiment: <strong>{post.sentiment}</strong></p>
                <p>Created: {new Date(post.created_at).toLocaleString()}</p>
              </div>
            ))}
          </div>
        )}
      </header>
    </div>
  );
}

export default App;

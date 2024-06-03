
import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import App from './App';
import './index.css';

ReactDOM.createRoot(
  document.getElementById('root')
).render(
  <React.StrictMode>
    <Router>
      <App />
    </Router>
  </React.StrictMode>
);


// import React from 'react';
// import { createRoot } from 'react-dom';
// import reportWebVitals from './reportWebVitals';
// import './index.css';
// // avoid using index.css split it into per page css
// // e.g. landing.css, finances.css, etc
// // import "./routes/landing/landing.css";
// import App from './App.js';

// createRoot(document.getElementById('root')).render(
//   <React.StrictMode>
//     <App />
//   </React.StrictMode>
// );
// reportWebVitals();

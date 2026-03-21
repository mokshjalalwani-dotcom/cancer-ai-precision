import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { PatientProvider } from './context/PatientContext';
import StepOne from './pages/StepOne';
import StepTwo from './pages/StepTwo';
import ResultPage from './pages/ResultPage';

function App() {
  return (
    <PatientProvider>
      <Router>
        <div className="min-h-screen bg-slate-50 py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto">
            <header className="text-center mb-12">
              <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight sm:text-5xl">
                Cancer Prognosis <span className="text-blue-600">Dashboard</span>
              </h1>
              <p className="mt-4 text-lg text-slate-600">
                AI-driven analysis for survival and recurrence risk.
              </p>
            </header>

            <Routes>
              <Route path="/" element={<Navigate to="/step-1" replace />} />
              <Route path="/step-1" element={<StepOne />} />
              <Route path="/step-2" element={<StepTwo />} />
              <Route path="/results" element={<ResultPage />} />
            </Routes>
          </div>
        </div>
      </Router>
    </PatientProvider>
  );
}

export default App;

import React from 'react';
import { Check } from 'lucide-react';

const StepProgress = ({ currentStep }) => {
  const steps = [
    { id: 1, name: 'General Info' },
    { id: 2, name: 'Clinical Data' },
    { id: 3, name: 'Results' },
  ];

  return (
    <div className="flex items-center justify-center w-full mb-12">
      <div className="flex items-center space-x-4 md:space-x-12">
        {steps.map((step, index) => (
          <React.Fragment key={step.id}>
            <div className="flex flex-col items-center">
              <div
                className={`step-indicator ${
                  currentStep > step.id
                    ? 'step-completed'
                    : currentStep === step.id
                    ? 'step-active'
                    : 'step-inactive'
                }`}
              >
                {currentStep > step.id ? <Check size={20} strokeWidth={3} /> : step.id}
              </div>
              <span className={`mt-2 text-sm font-medium ${
                currentStep === step.id ? 'text-blue-600' : 'text-slate-500'
              }`}>
                {step.name}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div className={`w-12 md:w-24 h-0.5 rounded-full ${
                currentStep > step.id ? 'bg-emerald-500' : 'bg-slate-200'
              }`} />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

export default StepProgress;

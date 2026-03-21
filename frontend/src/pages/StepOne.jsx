import React from 'react';
import { useNavigate } from 'react-router-dom';
import { usePatient } from '../context/PatientContext';
import StepProgress from '../components/StepProgress';
import { ArrowRight, User, Hash, Phone, Building2, Calendar } from 'lucide-react';

const StepOne = () => {
  const { patientData, updateGeneralInfo } = usePatient();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    updateGeneralInfo({ [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    navigate('/step-2');
  };

  return (
    <div className="max-w-2xl mx-auto">
      <StepProgress currentStep={1} />
      
      <div className="medical-card p-8">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-blue-100 text-blue-600 rounded-lg">
            <User size={24} />
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Patient General Information</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="label-text">
              <span className="flex items-center gap-2"><User size={16}/> Full Name</span>
            </label>
            <input
              type="text"
              name="fullName"
              placeholder="e.g. John Doe"
              className="input-field"
              value={patientData.generalInfo.fullName}
              onChange={handleChange}
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="label-text">
                <span className="flex items-center gap-2"><Calendar size={16}/> Age</span>
              </label>
              <input
                type="number"
                name="age"
                placeholder="Years"
                className="input-field"
                value={patientData.generalInfo.age}
                onChange={handleChange}
                required
              />
            </div>
            <div>
              <label className="label-text">Gender</label>
              <select
                name="gender"
                className="input-field"
                value={patientData.generalInfo.gender}
                onChange={handleChange}
                required
              >
                <option value="">Select Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="label-text">
                <span className="flex items-center gap-2"><Phone size={16}/> Contact Number</span>
              </label>
              <input
                type="tel"
                name="contactNumber"
                placeholder="+1 (555) 000-0000"
                className="input-field"
                value={patientData.generalInfo.contactNumber}
                onChange={handleChange}
                required
              />
            </div>
            <div>
              <label className="label-text">
                <span className="flex items-center gap-2"><Building2 size={16}/> Hospital ID</span>
              </label>
              <input
                type="text"
                name="hospitalId"
                placeholder="HOSP-12345"
                className="input-field"
                value={patientData.generalInfo.hospitalId}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="pt-6">
            <button type="submit" className="btn-primary w-full flex items-center justify-center gap-2">
              Proceed to Clinical Data <ArrowRight size={20} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default StepOne;

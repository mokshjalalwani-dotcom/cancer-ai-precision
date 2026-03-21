import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePatient } from '../context/PatientContext';
import StepProgress from '../components/StepProgress';
import { 
  TrendingUp, 
  ShieldCheck, 
  AlertTriangle, 
  Users, 
  Lightbulb, 
  Printer, 
  RefreshCcw,
  ChevronRight,
  Heart
} from 'lucide-react';

const ResultPage = () => {
  const { results, patientData, resetData } = usePatient();
  const navigate = useNavigate();

  useEffect(() => {
    if (!results) {
      navigate('/step-1');
    }
  }, [results, navigate]);

  if (!results) return null;

  const handleStartOver = () => {
    resetData();
    navigate('/step-1');
  };

  const getRiskColor = (prob) => {
    if (prob < 30) return 'text-emerald-600';
    if (prob < 70) return 'text-amber-600';
    return 'text-rose-600';
  };

  return (
    <div className="max-w-4xl mx-auto pb-20">
      <StepProgress currentStep={3} />
      
      <div className="flex items-center justify-between mb-8 px-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-900">Prognosis Analysis</h2>
          <p className="text-slate-500 mt-1">Patient: {patientData.generalInfo.fullName} | ID: {patientData.generalInfo.hospitalId}</p>
        </div>
        <div className="flex gap-3">
          <button className="btn-secondary flex items-center gap-2 px-4 py-2 text-sm" onClick={() => window.print()}>
            <Printer size={16} /> Print Report
          </button>
          <button className="btn-primary flex items-center gap-2 px-4 py-2 text-sm" onClick={handleStartOver}>
            <RefreshCcw size={16} /> New Case
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Survival Probability */}
        <div className="medical-card p-6 flex flex-col items-center text-center">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-full mb-4">
            <Heart size={24} />
          </div>
          <span className="text-slate-500 text-sm font-medium uppercase tracking-wider">Survival Probability</span>
          <div className={`text-4xl font-black mt-2 ${getRiskColor(100 - results.survival_probability)}`}>
            {results.survival_probability}%
          </div>
          <p className="text-xs text-slate-400 mt-2">Estimated 5-year survival rate</p>
        </div>

        {/* Aggressiveness Score */}
        <div className="medical-card p-6 flex flex-col items-center text-center">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-full mb-4">
            <Activity size={24} />
          </div>
          <span className="text-slate-500 text-sm font-medium uppercase tracking-wider">Aggressiveness Score</span>
          <div className={`text-4xl font-black mt-2 ${getRiskColor(results.aggressiveness_score)}`}>
            {results.aggressiveness_score}/100
          </div>
          <p className="text-xs text-slate-400 mt-2">Tumor growth & behavior dynamic</p>
        </div>

        {/* Recurrence Risk */}
        <div className="medical-card p-6 flex flex-col items-center text-center">
          <div className="p-3 bg-amber-50 text-amber-600 rounded-full mb-4">
            <TrendingUp size={24} />
          </div>
          <span className="text-slate-500 text-sm font-medium uppercase tracking-wider">Recurrence Risk</span>
          <div className={`text-4xl font-black mt-2 ${getRiskColor(results.recurrence_probability)}`}>
            {results.recurrence_probability}%
          </div>
          <p className="text-xs text-slate-400 mt-2">Likelihood of tumor return</p>
        </div>
      </div>

      <div className="space-y-6">
        {/* Similar Patients Summary */}
        <div className="medical-card">
          <div className="p-6 border-b border-slate-100 flex items-center gap-3">
            <div className="p-2 bg-purple-50 text-purple-600 rounded-lg">
              <Users size={20} />
            </div>
            <h3 className="text-xl font-bold text-slate-900">Similar Patients Summary</h3>
          </div>
          <div className="p-6">
            <p className="text-slate-600 leading-relaxed mb-6">
              {results.treatment_insight?.interpretation || "Based on the biological profile provided, we analyzed historical cases with similar genomic signatures and clinical markers."}
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {results.similar_patients?.map((patient, idx) => (
                <div key={idx} className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-100">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center text-xs font-bold text-slate-400 border border-slate-200">
                      #{idx + 1}
                    </div>
                    <div>
                      <div className="text-sm font-bold text-slate-800">{patient.case_id}</div>
                      <div className="text-xs text-slate-500">{(patient.similarity * 100).toFixed(1)}% match</div>
                    </div>
                  </div>
                  <div className="flex gap-2 text-[10px] font-bold uppercase tracking-tight">
                    <span className={`px-2 py-1 rounded ${patient.survival_label ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                      {patient.survival_label ? 'Survived' : 'Deceased'}
                    </span>
                    {patient.high_risk_flag && (
                      <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded">High Risk</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Treatment Insight */}
        <div className="medical-card bg-blue-600 text-white border-none">
          <div className="p-6 flex items-start gap-4">
            <div className="p-3 bg-white/20 backdrop-blur-md rounded-2xl">
              <Lightbulb size={28} className="text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold mb-2">Treatment Insight</h3>
              <p className="text-blue-50 leading-relaxed">
                {results.treatment_insight?.interpretation ? 
                  `The analysis suggests a ${results.survival_probability > 75 ? 'positive' : 'guarded'} prognosis. Historical patterns indicate that patients with this genomic profile often respond well to early intervention and targeted therapies. Regular monitoring for recurrence is recommended every 3 months.` :
                  "Standard care protocols for this profile include combined chemotherapy and radiation. Consult with an oncology specialist to discuss these data points."}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 p-4 bg-slate-100 rounded-xl flex items-center gap-3 text-slate-500 text-xs">
        <AlertTriangle size={14} className="shrink-0" />
        <p>
          <strong>Medical Disclaimer:</strong> This system is for exploratory research and clinical decision support purposes only. It does not constitute a medical diagnosis. All predictions should be verified by a qualified oncology professional.
        </p>
      </div>
    </div>
  );
};

export default ResultPage;

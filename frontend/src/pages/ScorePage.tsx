import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Award, RefreshCw, FileText, ChevronRight } from 'lucide-react';
import api from '../lib/api';
import { tierColor } from '../lib/types';
import type { ScoreResult } from '../lib/types';
import { PageLoader, Spinner } from '../components/Spinner';

function ScoreGauge({ score, tier }: { score: number; tier: string }) {
  const pct = Math.min(score / 850, 1);
  const radius = 80;
  const circumference = Math.PI * radius;
  const offset = circumference * (1 - pct);
  const color = tierColor(tier);

  return (
    <div className="relative w-48 h-28 mx-auto mb-2">
      <svg viewBox="0 0 200 110" className="w-full h-full">
        {/* Background arc */}
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="12"
          strokeLinecap="round"
        />
        {/* Score arc */}
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={`${circumference}`}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 1.5s ease-out' }}
        />
        {/* Score text */}
        <text x="100" y="85" textAnchor="middle" className="text-3xl font-bold" fill={color} fontSize="36">
          {score}
        </text>
        <text x="100" y="103" textAnchor="middle" fill="#6b7280" fontSize="12">
          / 850
        </text>
      </svg>
    </div>
  );
}

export default function ScorePage() {
  const [score, setScore] = useState<ScoreResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [reportMsg, setReportMsg] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.get('/score/latest');
        setScore(data);
      } catch {
        // No score yet
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const calculateScore = async () => {
    setCalculating(true);
    try {
      const { data } = await api.post('/score/calculate');
      setScore(data);
    } finally {
      setCalculating(false);
    }
  };

  const generateReport = async () => {
    if (!score) return;
    setGenerating(true);
    setReportMsg('');
    try {
      const { data } = await api.post('/report/generate', null, {
        params: { score_id: score.score_id },
        responseType: 'blob',
      });
      const url = URL.createObjectURL(data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `bizscore-report-${score.score_id}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      setReportMsg('Report downloaded!');
    } catch {
      setReportMsg('Failed to generate report.');
    } finally {
      setGenerating(false);
    }
  };

  if (loading) return <PageLoader />;

  return (
    <div className="px-5 pt-6 pb-4">
      <h1 className="text-xl font-bold text-gray-900 mb-5">Business Score</h1>

      {score ? (
        <>
          {/* Score Display */}
          <div className="bg-white rounded-2xl border border-gray-100 p-5 mb-5 text-center">
            <ScoreGauge score={score.total_score} tier={score.tier} />
            <span
              className="inline-block px-3 py-1 rounded-full text-sm font-semibold text-white"
              style={{ backgroundColor: tierColor(score.tier) }}
            >
              {score.tier}
            </span>
            <p className="text-xs text-gray-400 mt-2">
              Last calculated: {new Date(score.generated_at).toLocaleDateString()}
            </p>
          </div>

          {/* Components */}
          <div className="bg-white rounded-xl border border-gray-100 p-4 mb-5">
            <h2 className="text-sm font-semibold text-gray-900 mb-3">Score Breakdown</h2>
            <div className="space-y-3">
              {score.components.map((comp) => {
                const pct = (comp.score / comp.max_score) * 100;
                return (
                  <div key={comp.name}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-700 font-medium">{comp.name}</span>
                      <span className="text-gray-500">{comp.score}/{comp.max_score}</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-1000"
                        style={{
                          width: `${pct}%`,
                          backgroundColor: pct >= 70 ? '#059669' : pct >= 40 ? '#d97706' : '#dc2626',
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* AI Explanation */}
          {score.explanation && (
            <div className="bg-primary-50 rounded-xl p-4 mb-5">
              <h2 className="text-sm font-semibold text-primary-800 mb-2">AI Analysis</h2>
              <p className="text-sm text-primary-700 whitespace-pre-line leading-relaxed">{score.explanation}</p>
            </div>
          )}

          {/* Actions */}
          <div className="space-y-3">
            <button
              onClick={calculateScore}
              disabled={calculating}
              className="w-full flex items-center justify-center gap-2 bg-primary-500 text-white py-3 rounded-xl font-semibold hover:bg-primary-600 disabled:opacity-50"
            >
              {calculating ? <Spinner /> : <RefreshCw size={18} />}
              Recalculate Score
            </button>
            <button
              onClick={generateReport}
              disabled={generating}
              className="w-full flex items-center justify-center gap-2 bg-white border-2 border-primary-500 text-primary-500 py-3 rounded-xl font-semibold hover:bg-primary-50 disabled:opacity-50"
            >
              {generating ? <Spinner /> : <FileText size={18} />}
              Download PDF Report
            </button>
            {reportMsg && (
              <p className="text-sm text-center text-success">{reportMsg}</p>
            )}
          </div>

          {/* Score History Link */}
          <Link
            to="/score/history"
            className="flex items-center justify-between bg-gray-50 rounded-xl p-4 mt-5 hover:bg-gray-100 transition-colors"
          >
            <span className="text-sm font-medium text-gray-700">View Score History</span>
            <ChevronRight size={18} className="text-gray-400" />
          </Link>
        </>
      ) : (
        <div className="text-center py-16">
          <div className="w-16 h-16 bg-primary-50 rounded-full flex items-center justify-center mx-auto mb-4">
            <Award size={32} className="text-primary-300" />
          </div>
          <h2 className="text-lg font-bold text-gray-900 mb-2">No Score Yet</h2>
          <p className="text-sm text-gray-500 mb-6 max-w-xs mx-auto">
            Start using your wallet to build your business transaction history, then calculate your score.
          </p>
          <button
            onClick={calculateScore}
            disabled={calculating}
            className="bg-primary-500 text-white px-8 py-3 rounded-xl font-semibold hover:bg-primary-600 disabled:opacity-50 flex items-center justify-center gap-2 mx-auto"
          >
            {calculating ? <><Spinner /> Calculating...</> : 'Calculate My Score'}
          </button>
        </div>
      )}
    </div>
  );
}

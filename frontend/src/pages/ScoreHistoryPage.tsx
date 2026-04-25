import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';
import api from '../lib/api';
import { tierColor } from '../lib/types';
import type { ScoreResult } from '../lib/types';
import { PageLoader } from '../components/Spinner';

export default function ScoreHistoryPage() {
  const navigate = useNavigate();
  const [scores, setScores] = useState<ScoreResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.get('/score/history');
        setScores(data.scores || []);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <PageLoader />;

  return (
    <div className="px-5 pt-6 pb-4">
      <button onClick={() => navigate(-1)} className="inline-flex items-center text-gray-500 text-sm mb-4">
        <ChevronLeft size={18} /> Back
      </button>
      <h1 className="text-xl font-bold text-gray-900 mb-5">Score History</h1>

      {scores.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-16">No score history yet.</p>
      ) : (
        <div className="space-y-3">
          {scores.map((s) => (
            <div key={s.score_id} className="bg-white rounded-xl border border-gray-100 p-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {new Date(s.generated_at).toLocaleDateString()}
                </p>
                <span
                  className="text-xs font-medium px-2 py-0.5 rounded-full text-white mt-1 inline-block"
                  style={{ backgroundColor: tierColor(s.tier) }}
                >
                  {s.tier}
                </span>
              </div>
              <span className="text-2xl font-bold" style={{ color: tierColor(s.tier) }}>
                {s.total_score}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

import { RecommendationCard } from "./RecommendationCard";
import type { Recommendation } from "../types/chat";

interface RecommendationListProps {
  recommendations: Recommendation[];
}

export function RecommendationList({ recommendations }: RecommendationListProps) {
  return (
    <aside className="flex min-h-[320px] flex-col rounded-2xl border border-slate-200 bg-white shadow-soft">
      <div className="border-b border-slate-200 px-5 py-4">
        <h2 className="text-sm font-semibold text-slate-950">Recommended assessments</h2>
        <p className="mt-1 text-xs leading-5 text-slate-500">
          Latest catalog-backed matches from the assistant.
        </p>
      </div>

      <div className="flex-1 space-y-3 p-4">
        {recommendations.length > 0 ? (
          recommendations.map((recommendation) => (
            <RecommendationCard
              key={`${recommendation.name}-${recommendation.url}`}
              recommendation={recommendation}
            />
          ))
        ) : (
          <div className="flex h-full min-h-[220px] items-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-5 text-sm leading-6 text-slate-500">
            Recommendations will appear here when the assistant has enough role context.
            Clarification and refusal turns intentionally keep this area empty.
          </div>
        )}
      </div>
    </aside>
  );
}

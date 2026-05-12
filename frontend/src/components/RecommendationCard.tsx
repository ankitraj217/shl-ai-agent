import type { Recommendation } from "../types/chat";

interface RecommendationCardProps {
  recommendation: Recommendation;
}

export function RecommendationCard({ recommendation }: RecommendationCardProps) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-blue-200 hover:shadow-md">
      <h3 className="text-sm font-semibold leading-6 text-slate-950">
        {recommendation.name}
      </h3>
      <p className="mt-2 inline-flex rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
        {recommendation.test_type}
      </p>
      <a
        href={recommendation.url}
        target="_blank"
        rel="noreferrer"
        className="mt-4 block text-sm font-medium text-blue-700 underline decoration-blue-200 underline-offset-4 hover:text-blue-900 hover:decoration-blue-700"
      >
        Open SHL catalog page
      </a>
    </article>
  );
}

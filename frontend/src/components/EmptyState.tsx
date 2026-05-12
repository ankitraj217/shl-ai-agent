export function EmptyState() {
  return (
    <div className="flex min-h-[360px] items-center justify-center px-6 py-12 text-center">
      <div className="max-w-md">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-blue-100 bg-blue-50 text-sm font-semibold text-blue-700">
          SHL
        </div>
        <h2 className="mt-5 text-lg font-semibold text-slate-950">
          Start with a hiring scenario
        </h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Describe the role, seniority, and skills you are hiring for. You can also ask
          to refine or compare assessments.
        </p>
        <div className="mt-5 rounded-xl border border-slate-200 bg-white p-4 text-left text-sm text-slate-600 shadow-sm">
          <p className="font-medium text-slate-900">Example prompt</p>
          <p className="mt-1">
            Hiring a mid-level Java developer. Need technical skill checks and something
            suitable for remote screening.
          </p>
        </div>
      </div>
    </div>
  );
}

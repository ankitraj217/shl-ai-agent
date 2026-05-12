export function Header() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">
            SHL Assessment Recommender
          </p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">
            Recruiter Copilot
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            Describe the role, seniority, and hiring signals you care about. Get
            catalog-grounded assessment recommendations without leaving your workflow.
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm shadow-sm">
          <p className="font-medium text-slate-950">Stateless by design</p>
          <p className="mt-1 text-slate-600">This tab sends conversation history with every request.</p>
        </div>
      </div>
    </header>
  );
}

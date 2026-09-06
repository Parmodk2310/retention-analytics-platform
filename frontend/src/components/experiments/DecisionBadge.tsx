export function DecisionBadge({decision}:{decision:string}){return <span className="rounded-full bg-muted px-2 py-1 text-xs font-medium">{decision.replaceAll('_',' ')}</span>}

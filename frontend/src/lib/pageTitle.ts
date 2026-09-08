const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

export function pageTitle(pathname: string): string {
  const segments = pathname.split('/').filter(Boolean)

  if (segments.length === 0) {
    return 'Overview'
  }

  if (
    segments[0] === 'experiments' &&
    segments.length === 2 &&
    UUID_PATTERN.test(segments[1])
  ) {
    return 'Experiment Analysis'
  }

  const titles: Record<string, string> = {
  metrics: 'Product Metrics',
  funnel: 'Funnel Analysis',
  cohorts: 'Cohort Retention',
  experiments: 'Experiments',
  churn: 'Churn Intelligence',
  'model-health': 'Model Health',
  settings: 'Settings',
}

  return titles[segments[0]] ?? 'RetentionOS'
}
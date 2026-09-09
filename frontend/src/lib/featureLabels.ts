const FEATURE_LABELS: Record<string, string> = {
  sessions_90d: "Sessions · last 90 days",
  sessions_30d: "Sessions · last 30 days",
  searches_30d: "Searches · last 30 days",
  carts_30d: "Cart adds · last 30 days",
  checkouts_30d: "Checkouts · last 30 days",
  purchases_90d: "Purchases · last 90 days",
  revenue_90d: "Revenue · last 90 days",
  days_since_last_activity: "Days since last activity",
};

function titleCase(value: string): string {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function featureLabel(
  feature: string,
  providedLabel?: string | null,
): string {
  const explicit = providedLabel?.trim();

  if (explicit) {
    return explicit;
  }

  if (FEATURE_LABELS[feature]) {
    return FEATURE_LABELS[feature];
  }

  if (feature.startsWith("acquisition_channel_")) {
    const channel = feature.replace("acquisition_channel_", "");
    return `${titleCase(channel)} acquisition`;
  }

  if (feature.startsWith("device_type_")) {
    const device = feature.replace("device_type_", "");
    return `${titleCase(device)} device`;
  }

  return titleCase(feature);
}

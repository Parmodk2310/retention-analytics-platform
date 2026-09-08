import type {
  FeatureImportance,
} from '@/types/api'

function displayFeature(
  feature: string,
) {
  return feature
    .replaceAll('_', ' ')
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase(),
    )
}

export function DriverList({
  drivers,
}: {
  drivers: FeatureImportance[]
}) {
  const topDrivers =
    drivers.slice(0, 8)

  return (
    <div>
      <div className="mb-5">
        <h3 className="font-semibold">
          Global risk drivers
        </h3>

        <p className="mt-1 text-xs opacity-50">
          Relative importance from the
          underlying XGBoost model.
        </p>
      </div>

      {topDrivers.length === 0 ? (
        <p className="text-sm opacity-50">
          Driver importance is not
          available.
        </p>
      ) : (
        <div className="space-y-3">
          {topDrivers.map(
            (
              driver,
              index,
            ) => (
              <div
                key={
                  driver.feature
                }
                className="flex items-center gap-3"
              >
                <span className="w-5 text-xs opacity-40">
                  {index + 1}
                </span>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-3">
                    <span className="truncate text-sm">
                      {displayFeature(
                        driver.feature,
                      )}
                    </span>

                    <span className="text-xs tabular-nums opacity-60">
                      {(
                        driver.importance *
                        100
                      ).toFixed(1)}
                      %
                    </span>
                  </div>

                  <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-primary"
                      style={{
                        width:
                          `${Math.min(
                            driver.importance *
                              100,
                            100,
                          )}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            ),
          )}
        </div>
      )}
    </div>
  )
}
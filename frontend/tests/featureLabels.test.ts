import { describe, expect, it } from "vitest";
import { featureLabel } from "@/lib/featureLabels";

describe("featureLabel", () => {
  it("uses a supplied API label when available", () => {
    expect(featureLabel("revenue_90d", "Revenue activity")).toBe(
      "Revenue activity",
    );
  });

  it("humanizes numeric feature windows", () => {
    expect(featureLabel("revenue_90d")).toBe("Revenue · last 90 days");

    expect(featureLabel("sessions_30d")).toBe("Sessions · last 30 days");
  });

  it("humanizes acquisition channels", () => {
    expect(featureLabel("acquisition_channel_paid_social")).toBe(
      "Paid Social acquisition",
    );
  });

  it("humanizes device categories", () => {
    expect(featureLabel("device_type_mobile")).toBe("Mobile device");
  });

  it("provides a readable fallback", () => {
    expect(featureLabel("unknown_feature_name")).toBe("Unknown Feature Name");
  });
});

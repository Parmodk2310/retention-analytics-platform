import { describe, expect, it } from 'vitest'
import { monthsForDays } from '@/hooks/useAnalytics'
import { analyticsKeys } from '@/lib/queryKeys'

describe('analytics frontend contracts', () => {
  it('maps global day windows to revenue month windows', () => {
    expect(monthsForDays(7)).toBe(1)
    expect(monthsForDays(30)).toBe(1)
    expect(monthsForDays(90)).toBe(3)
    expect(monthsForDays(365)).toBe(12)
  })

  it('includes acquisition channel in cache identity', () => {
    expect(analyticsKeys.overview(30, 'organic')).not.toEqual(
      analyticsKeys.overview(30, 'paid_social'),
    )
  })
})

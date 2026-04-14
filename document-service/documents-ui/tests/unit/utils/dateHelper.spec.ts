import { describe, it, expect } from 'vitest'
import {
  formatDateToISO,
  formatToReadableDate,
  formatIsoToYYYYMMDD,
  calculatePreviousDate
} from '~/utils/dateHelper'

describe('dateHelper', () => {
  describe('formatDateToISO', () => {
    it('returns undefined for an empty string', () => {
      expect(formatDateToISO('')).toBeUndefined()
    })

    it('returns a string with a timezone offset replacing Z', () => {
      const result = formatDateToISO('2024-08-15')
      expect(typeof result).toBe('string')
      expect(result).not.toMatch(/Z$/)
      expect(result).toMatch(/[+-]\d{2}:\d{2}$/)
    })

    it('returns a valid date portion in the result', () => {
      const result = formatDateToISO('2024-06-01')
      expect(result).toBeDefined()
      expect(result.length).toBeGreaterThan(10)
    })
  })

  describe('formatToReadableDate', () => {
    it('returns a falsy value for an empty string', () => {
      expect(formatToReadableDate('')).toBeFalsy()
    })

    it('includes the year in the formatted output', () => {
      const result = formatToReadableDate('2024-08-13T17:21:29+00:00')
      expect(result).toContain('2024')
    })

    it('includes Pacific time when time is not omitted', () => {
      const result = formatToReadableDate('2024-08-13T17:21:29+00:00')
      expect(result).toContain('Pacific time')
    })

    it('omits time info when omitTime is true', () => {
      const result = formatToReadableDate('2024-08-13T17:21:29+00:00', true)
      expect(result).not.toContain('Pacific time')
      expect(result).toContain('2024')
    })

    it('returns a non-empty string for a valid ISO date', () => {
      const result = formatToReadableDate('2024-01-01T00:00:00+00:00')
      expect(result.length).toBeGreaterThan(0)
    })
  })

  describe('formatIsoToYYYYMMDD', () => {
    it('returns a string in YYYY-MM-DD format', () => {
      const result = formatIsoToYYYYMMDD('2024-08-15T12:00:00.000Z')
      expect(result).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    })

    it('returns a string in YYYY-MM-DD format for another date', () => {
      const result = formatIsoToYYYYMMDD('2023-03-20T12:00:00.000Z')
      expect(result).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    })
  })

  describe('calculatePreviousDate', () => {
    it('returns a Date earlier than now when subtracting days', () => {
      const now = new Date()
      const result = calculatePreviousDate('d-7')
      expect(result).toBeInstanceOf(Date)
      expect(result < now).toBe(true)
    })

    it('subtracts approximately the right number of days', () => {
      const before = new Date()
      const result = calculatePreviousDate('d-7')
      const after = new Date()
      const midNow = (before.getTime() + after.getTime()) / 2
      const diffDays = Math.round((midNow - result.getTime()) / (1000 * 60 * 60 * 24))
      expect(diffDays).toBe(7)
    })

    it('subtracts months correctly', () => {
      const now = new Date()
      const result = calculatePreviousDate('m-3')
      expect(result).toBeInstanceOf(Date)
      expect(result < now).toBe(true)
    })

    it('subtracts years correctly', () => {
      const now = new Date()
      const result = calculatePreviousDate('y-1')
      expect(result.getFullYear()).toBe(now.getFullYear() - 1)
    })

    it('throws for an invalid format string', () => {
      expect(() => calculatePreviousDate('invalid')).toThrow('Invalid input format')
    })

    it('throws for a numeric-only string', () => {
      expect(() => calculatePreviousDate('7')).toThrow('Invalid input format')
    })
  })
})

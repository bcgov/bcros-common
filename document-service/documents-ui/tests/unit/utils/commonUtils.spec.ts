import { describe, it, expect } from 'vitest'
import { insensitiveStrCompare, deepChangesComparison } from '~/utils/commonUtils'

describe('commonUtils', () => {
  describe('insensitiveStrCompare', () => {
    it('returns true for identical strings', () => {
      expect(insensitiveStrCompare('hello', 'hello')).toBe(true)
    })

    it('returns true for strings differing only in case', () => {
      expect(insensitiveStrCompare('Hello', 'hello')).toBe(true)
      expect(insensitiveStrCompare('WORLD', 'world')).toBe(true)
    })

    it('returns false for different strings', () => {
      expect(insensitiveStrCompare('hello', 'world')).toBe(false)
    })

    it('returns true when first argument is null/undefined (optional chaining returns undefined, !undefined is true)', () => {
      expect(insensitiveStrCompare(null, 'hello')).toBe(true)
      expect(insensitiveStrCompare(undefined, 'hello')).toBe(true)
    })

    it('returns true for two empty strings', () => {
      expect(insensitiveStrCompare('', '')).toBe(true)
    })
  })

  describe('deepChangesComparison', () => {
    it('returns false when two identical objects are compared', () => {
      expect(deepChangesComparison({ a: 1 }, { a: 1 })).toBe(false)
    })

    it('returns true when objects differ', () => {
      expect(deepChangesComparison({ a: 1 }, { a: 2 })).toBe(true)
    })

    it('returns false for case-insensitive string differences by default', () => {
      expect(deepChangesComparison({ name: 'Alice' }, { name: 'alice' })).toBe(false)
    })

    it('returns true for case-sensitive string differences when isCaseSensitive is true', () => {
      expect(deepChangesComparison({ name: 'Alice' }, { name: 'alice' }, true)).toBe(true)
    })

    it('returns true when boolean current differs from base', () => {
      expect(deepChangesComparison(false as any, true as any)).toBe(true)
    })

    it('returns false when boolean current equals base', () => {
      expect(deepChangesComparison(true as any, true as any)).toBe(false)
    })

    it('ignores null/empty properties when cleanEmptyProperties is true', () => {
      const base = { a: 1, b: null }
      const current = { a: 1 }
      expect(deepChangesComparison(base, current)).toBe(false)
    })

    it('detects differences in nested objects', () => {
      expect(deepChangesComparison({ a: { b: 1 } }, { a: { b: 2 } })).toBe(true)
    })

    it('returns false for two identical strings', () => {
      expect(deepChangesComparison('hello' as any, 'hello' as any)).toBe(false)
    })
  })
})

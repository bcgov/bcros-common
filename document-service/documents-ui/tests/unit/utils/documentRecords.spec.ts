import { describe, it, expect, vi } from 'vitest'
import { truncate, pageSize, documentPreview } from '~/utils/documentRecords'

describe('documentRecords', () => {
  describe('pageSize', () => {
    it('is 100', () => {
      expect(pageSize).toBe(100)
    })
  })

  describe('documentPreview', () => {
    it('calls URL.createObjectURL and returns the result', () => {
      const mockUrl = 'blob:mock-url'
      const createObjectURLSpy = vi.spyOn(URL, 'createObjectURL').mockReturnValue(mockUrl)
      const mockFile = new File(['content'], 'test.pdf', { type: 'application/pdf' })

      const result = documentPreview(mockFile)
      expect(createObjectURLSpy).toHaveBeenCalledWith(mockFile)
      expect(result).toBe(mockUrl)
      createObjectURLSpy.mockRestore()
    })
  })

  describe('truncate', () => {
    it('returns the original string when it does not exceed maxLength', () => {
      expect(truncate('hello', 10, 5)).toBe('hello')
    })

    it('truncates from the end when backChars is not provided', () => {
      const result = truncate('hello world', 8, 5)
      expect(result).toBe('hello...')
    })

    it('truncates from the middle when backChars is provided', () => {
      const result = truncate('hello world foo', 10, 3, 3)
      expect(result).toBe('hel...foo')
    })

    it('returns original string when length equals maxLength', () => {
      expect(truncate('abcde', 5, 3)).toBe('abcde')
    })

    it('keeps front characters correctly in end truncation', () => {
      const result = truncate('abcdefghij', 6, 4)
      expect(result).toBe('abcd...')
    })

    it('keeps back characters correctly in middle truncation', () => {
      const result = truncate('abcdefghij', 6, 2, 2)
      expect(result).toBe('ab...ij')
    })

    it('handles long strings with end truncation', () => {
      const long = 'a'.repeat(100)
      const result = truncate(long, 10, 7)
      expect(result).toBe('aaaaaaa...')
      expect(result.length).toBe(10)
    })
  })
})

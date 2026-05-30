import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { copyToClipboard } from '~/utils/copyToClipboard'

describe('copyToClipboard', () => {
  let originalClipboard: Clipboard

  beforeEach(() => {
    originalClipboard = navigator.clipboard
  })

  afterEach(() => {
    Object.defineProperty(navigator, 'clipboard', {
      value: originalClipboard,
      writable: true,
      configurable: true
    })
  })

  it('calls navigator.clipboard.writeText with the provided text', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText },
      writable: true,
      configurable: true
    })

    copyToClipboard('hello world')
    expect(writeText).toHaveBeenCalledWith('hello world')
  })

  it('logs an error when clipboard API is not supported', () => {
    Object.defineProperty(navigator, 'clipboard', {
      value: undefined,
      writable: true,
      configurable: true
    })

    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    copyToClipboard('test')
    expect(consoleSpy).toHaveBeenCalledWith('Clipboard API not supported')
    consoleSpy.mockRestore()
  })
})

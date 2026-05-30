import { describe, it, expect } from 'vitest'
import {
  documentTypes,
  documentResultColumns,
  documentRecordHelpContent
} from '~/utils/documentTypes'

describe('documentTypes', () => {
  describe('documentTypes array', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(documentTypes)).toBe(true)
      expect(documentTypes.length).toBeGreaterThan(0)
    })

    it('each entry has required class, description, prefixes and documents fields', () => {
      for (const entry of documentTypes) {
        expect(typeof entry.class).toBe('string')
        expect(typeof entry.description).toBe('string')
        expect(Array.isArray(entry.prefixes)).toBe(true)
        expect(Array.isArray(entry.documents)).toBe(true)
      }
    })

    it('each document entry has type, description and productCode', () => {
      for (const entry of documentTypes) {
        for (const doc of entry.documents) {
          expect(typeof doc.type).toBe('string')
          expect(typeof doc.description).toBe('string')
          expect(typeof doc.productCode).toBe('string')
        }
      }
    })

    it('contains expected classes', () => {
      const classes = documentTypes.map(d => d.class)
      expect(classes).toContain('CORP')
      expect(classes).toContain('NR')
      expect(classes).toContain('MHR')
    })
  })

  describe('documentResultColumns', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(documentResultColumns)).toBe(true)
      expect(documentResultColumns.length).toBeGreaterThan(0)
    })

    it('each column has key and label', () => {
      for (const col of documentResultColumns) {
        expect(typeof col.key).toBe('string')
        expect(typeof col.label).toBe('string')
      }
    })

    it('contains the consumerDocumentId column', () => {
      const keys = documentResultColumns.map(c => c.key)
      expect(keys).toContain('consumerDocumentId')
    })
  })

  describe('documentRecordHelpContent', () => {
    it('is a non-empty string', () => {
      expect(typeof documentRecordHelpContent).toBe('string')
      expect(documentRecordHelpContent.trim().length).toBeGreaterThan(0)
    })
  })
})

import { describe, expect, test } from 'vitest'
import { API_BASE } from '../apiBase'

describe('API_BASE', () => {
  test('is same-origin /api so Vite ports other than 5173 do not CORS-fail', () => {
    expect(API_BASE).toBe('/api')
    expect(API_BASE).not.toMatch(/localhost:8000/)
    expect(API_BASE).not.toMatch(/127\.0\.0\.1:8000/)
  })
})

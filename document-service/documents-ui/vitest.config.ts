import { fileURLToPath } from 'node:url'
import { defineVitestConfig } from '@nuxt/test-utils/config'

export default defineVitestConfig({
  test: {
    dir: 'tests',
    environment: 'nuxt',
    environmentOptions: {
      nuxt: {
        rootDir: fileURLToPath(new URL('./', import.meta.url)),
        domEnvironment:
          (process.env.VITEST_DOM_ENV as 'happy-dom' | 'jsdom') ?? 'happy-dom'
      }
    },
    setupFiles: ['./tests/setup.ts'],
    globals: true,
    coverage: {
      provider: 'v8',
      enabled: true,
      reporter: ['text', ['cobertura', { file: 'coverage.xml' }]],
      reportsDirectory: './tests/coverage',
      // Only measure testable utility files; exclude API layer, composables, stores,
      // pages, layouts, and other files requiring full browser/server context.
      include: ['src/utils/**/*.ts'],
      exclude: [
        'src/utils/documentRequests.ts',
        'src/utils/breadcrumbs.ts'
      ]
    }
  }
})
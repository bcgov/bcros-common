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
      reporter: ['text', 'cobertura'],
      reportsDirectory: './tests/coverage',
      include: ['src/**/*.{ts,vue}'],
      exclude: [
        'src/interfaces/**',
        'src/enums/**',
        'src/shims.vue.d.ts',
        'src/app.config.ts',
        'src/app/router.options.ts',
        'src/middleware/**',
        'src/**/*.d.ts'
      ]
    }
  }
})
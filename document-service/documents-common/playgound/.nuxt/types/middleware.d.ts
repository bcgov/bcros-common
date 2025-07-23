import type { NavigationGuard } from 'vue-router'
export type MiddlewareKey = never
declare module "../../node_modules/.pnpm/nuxt@3.16.0_@netlify+blobs@9.1.2_@parcel+watcher@2.5.1_@types+node@24.0.14_db0@0.3.2_eslint@9_fjsihgf6ny5hjmwdlo6khn5oea/node_modules/nuxt/dist/pages/runtime/composables" {
  interface PageMeta {
    middleware?: MiddlewareKey | NavigationGuard | Array<MiddlewareKey | NavigationGuard>
  }
}
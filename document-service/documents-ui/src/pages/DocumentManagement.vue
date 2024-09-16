<script setup lang="ts">
const { searchDocuments, hasMinimumSearchCriteria } = useDocuments()
const { validateDocumentSearch } = storeToRefs(useBcrosDocuments())
const { documentSearchResults } = storeToRefs(useBcrosDocuments())
</script>
<template>
  <div data-cy="document-management">
    <BcrosSection
      name="documentManagement"
      class="mt-12"
    >
      <template #header>
        <div class="items-center">

          <div>
            <h1 class="text-[32px] pb-2">{{ $t('title.documentManagement') }}</h1>
            <span class="text-gray-700 font-normal text-base">{{ $t('descriptions.documentManagement') }}</span>
          </div>
          <!-- Help content -->
          <HelpToggleContainer>
            <template #content>
              <p>
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque maximus turpis luctus, finibus dolor non, cursus nulla. Nulla laoreet neque vestibulum malesuada luctus. Donec fringilla metus neque, et hendrerit mi lacinia sed. Mauris eu euismod purus. In lacinia nunc vel est placerat sodales a porttitor sem. Sed tincidunt ligula nec odio iaculis, in imperdiet dolor facilisis. Nam in varius turpis. Vestibulum dignissim ipsum vel dui feugiat rhoncus. Cras hendrerit lacinia arcu vitae posuere. Phasellus vitae erat vel diam congue semper. Nam vel mollis ex. Pellentesque augue augue, blandit vestibulum arcu sit amet, interdum lacinia lectus. Suspendisse eleifend lectus lorem, tristique tincidunt lorem egestas non. Sed et rutrum justo. Proin est nunc, luctus at est eget, rhoncus auctor enim.
Mauris eget nunc ut dolor rhoncus vehicula. Curabitur molestie eu ante et egestas. Etiam vitae laoreet tellus, et interdum elit. Fusce vitae rhoncus lorem, id mattis purus. Sed porttitor magna nec urna bibendum, sit amet blandit justo tristique. Suspendisse at turpis vel elit posuere elementum et quis libero. Aliquam vehicula dignissim maximus. Quisque accumsan iaculis euismod. Maecenas magna eros, auctor et consequat ac, pretium eget leo. Pellentesque in mauris dictum, elementum purus sed, sollicitudin dui. Donec purus odio, commodo sed commodo a, rhoncus eu turpis. Nullam porta maximus orci non ullamcorper. Donec non mollis nisi. Nulla diam ex, efficitur vitae semper a, vehicula vitae mi.
              </p>
            </template>
          </HelpToggleContainer>
          <div>
            <UButton
              class="mt-5 py-2 px-6 text-base font-bold"
              outlined
              color="primary"
              @click="navigateTo({ name: RouteNameE.DOCUMENT_INDEXING })"
            >
              {{ $t('button.documentIndexing') }}
              <UIcon
                name="i-mdi-chevron-right"
                class="bg-white text-xl"
              />
            </UButton>
          </div>
        </div>
      </template>
      <template #default>
        <DocumentSearch />
      </template>
    </BcrosSection>

    <div class="grid grid-cols-6 gap-4 mt-6">
      <div class="col-end-7 col-span-1">
        <UButton
          class="px-7 text-base font-bold h-[44px] float-right"
          outlined
          color="primary"
          @click="searchDocuments"
        >
          <UIcon
            name="i-mdi-search"
            class="bg-white text-xl"
          />
          Search
        </UButton>
      </div>
    </div>
    <span
      v-if="validateDocumentSearch && !hasMinimumSearchCriteria"
      class="text-red-500 float-right text-sm mt-3"
    >
      Enter or select search criteria
    </span>

    <!-- Document Search Results -->
    <UDivider v-if="documentSearchResults.length" class="pt-[60px] pb-4" />
    <DocumentsTable />
  </div>
</template>
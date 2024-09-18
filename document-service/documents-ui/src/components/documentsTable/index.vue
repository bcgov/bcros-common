<script setup lang="ts">
import { formatToReadableDate } from "~/utils/dateHelper";
import { documentTypes, documentResultColumns } from "~/utils/documentTypes";
import type { DocumentInfoIF } from "~/interfaces/document-types-interface";
const { getDocumentDescription, downloadFileFromUrl } = useDocuments();
const { documentList, documentRecord, documentSearchResults } = storeToRefs(
  useBcrosDocuments()
);

const {
  searchDocumentId,
  searchEntityId,
  searchDocuments,
  searchDocumentClass,
  searchDateRange,
  isLoading,
} = storeToRefs(useBcrosDocuments());

const openDocumentRecord = (searchResult: DocumentInfoIF) => {
  documentRecord.value = { ...searchResult };
  documentList.value = searchResult.consumerFilenames?.map((file) => ({
    name: file,
  }));
  navigateTo({
    name: RouteNameE.DOCUMENT_RECORDS,
    params: { identifier: searchResult.consumerDocumentId },
  });
};

const documentRecordColumns = ref([]);

onMounted(() => {
  documentRecordColumns.value = documentResultColumns();
});
</script>
<template>
  <ContentWrapper
    name="document-search-results"
    class="my-12"
    data-cy="document-search-results"
  >
    <template #header>
      <div class="flex justify-between items-center">
        <span>{{ $t("documentSearch.table.title") }} (123)</span>
      </div>
    </template>
    <template #content>
      <UTable
        class="mt-8"
        :columns="documentRecordColumns"
        :rows="documentSearchResults || []"
        :sort-button="{
          class: 'font-bold text-sm',
          size: '2xs',
          square: false,
          ui: { rounded: 'rounded-full' },
        }"
        :loading="isLoading"
        :empty-state="{
          icon: null,
          label: $t('documentSearch.table.noResult'),
        }"
      >
        <template #emptyColumn-header="{ column }">
          <div class="uppercase font-light text-gray-600">
            <div class="flex align-center px-2">
              {{ column.label }}
            </div>
            <UDivider class="my-3 w-full" />
            <div class="flex align-center px-2 h-8">
              {{ $t("documentSearch.table.headers.filterBy") }}
            </div>
          </div>
        </template>
        <template #consumerDocumentId-header="{ column }">
          <DocumentsTableInputHeader
            :column="column"
            v-model="searchDocumentId"
          />
        </template>
        <template #consumerIdentifier-header="{ column }">
          <DocumentsTableInputHeader
            :column="column"
            v-model="searchEntityId"
          />
        </template>
        <template #documentURL-header="{ column }">
          <DocumentsTableInputHeader
            :column="column"
            v-model="searchDocuments"
          />
        </template>
        <template #consumerFilingDateTime-header="{ column }">
          <div class="px-2">
            {{ column.label }}
          </div>
          <UDivider class="my-3" />
          <div>
            <div class="h-8">
              <InputDatePicker
                v-model="searchDateRange"
                class="w-full px-2 font-light"
                is-ranged-picker
                is-left-bar
                is-filter
                size="md"
              />
            </div>
          </div>
        </template>
        <template #documentTypeDescription-header="{ column }">
          <div class="px-2">
            {{ column.label }}
          </div>
          <UDivider class="my-3" />
          <div>
            <div class="h-8">
              <USelectMenu
                v-model="searchDocumentClass"
                class="w-full px-2 font-light"
                select-class="text-gray-700"
                :options="documentTypes"
                value-attribute="class"
                option-attribute="description"
                size="md"
                :placeholder="column.label"
                :ui="{ icon: { trailing: { pointer: '' } } }"
              >
                <template #trailing>
                  <UButton
                    v-show="searchDocumentClass !== ''"
                    color="gray"
                    variant="link"
                    icon="i-mdi-cancel-circle text-primary"
                    :padded="false"
                    @click="searchDocumentClass = ''"
                  />
                </template>
              </USelectMenu>
            </div>
          </div>
        </template>
        <template #actions-header="{ column }">
          <div class="px-2">
            {{ column.label }}
          </div>
          <UDivider class="my-3" />
          <div>
            <div class="h-8" />
          </div>
        </template>

        <!-- Document URL -->
        <template #documentClass-data="{ row }">
          {{ getDocumentDescription(row.documentClass) }}
        </template>

        <!-- Consumer DateTime -->
        <template #consumerFilingDateTime-data="{ row }">
          {{ formatToReadableDate(row.consumerFilingDateTime, true) }}
        </template>

        <!-- Document URL -->
        <template #documentURL-data="{ row }">
          <div v-if="row.consumerFilenames.length > 1">
            <span
              v-for="(file, i) in row.consumerFilenames"
              :key="`file-${i}`"
              class="block my-1"
            >
              <ULink
                inactive-class="text-primary"
                class="flex align-center"
                @click="downloadFileFromUrl(row.documentUrls[i], file)"
              >
                <UIcon name="i-mdi-file-download" class="w-5 h-5" />
                {{ file }}
              </ULink>
            </span>
            <span>
              <ULink inactive-class="text-primary" class="flex align-center">
                <UIcon name="i-mdi-download" class="w-5 h-5" />
                {{ $t("documentSearch.table.downloadAll") }}
              </ULink>
            </span>
          </div>
          <div v-else>
            <span class="block my-1">
              <ULink
                inactive-class="text-primary"
                class="flex align-center"
                @click="
                  downloadFileFromUrl(
                    row.documentUrls[0],
                    row.consumerFilenames[0]
                  )
                "
              >
                <UIcon name="i-mdi-file-download" class="w-5 h-5" />
                {{ row.consumerFilenames[0] }}
              </ULink>
            </span>
          </div>
        </template>
        <!-- Actions -->
        <template #actions-data="{ row }">
          <UButton
            class="h-[35px] px-8 text-base"
            outlined
            color="primary"
            @click="openDocumentRecord(row)"
          >
            {{ $t("button.open") }}
          </UButton>
        </template>
      </UTable>
    </template>
  </ContentWrapper>
</template>

<script setup lang="ts">
import { documentTypes } from '~/utils/documentTypes'
import { useBcrosDocuments } from '~/stores/documents'

const props = defineProps({
  validate: {
    type: Boolean,
    default: false
  }
})

const {
  consumerIdentifier,
  noIdCheckbox,
  documentClass,
  documentType,
  consumerFilingDate
} = storeToRefs(useBcrosDocuments())

const hasIdError = computed(() => {
  return props.validate && !consumerIdentifier.value && !noIdCheckbox.value
})
const hasClassError = computed(() => {
  return props.validate && !documentClass.value
})
const hasTypeError = computed(() => {
  return props.validate && !documentType.value
})
const hasDateError = computed(() => {
  return props.validate && !consumerFilingDate.value
})

/**
 * Returns an array of all root keys (categories) from the documentTypes object
 */
function getCategories(): string[] {
  return Object.keys(documentTypes)
}

/**
 * Retrieves document descriptions for the specified category
 * @param category - The category for which to retrieve documents
 * @returns An array of document descriptions or an empty array if the category is not found
 */
function getDocumentsByCategory(category: string): string[]|null {
  const categoryData = documentTypes[category]
  return categoryData ? categoryData.documents.map(doc => doc.description ) : []
}

/**
 * Finds the category based on the prefix of the entity identifier
 * @param identifier - The entity identifier to search
 * @returns The category associated with the prefix or null if no match is found
 */
function findCategoryByPrefix(identifier: string): void {
  const match = identifier.match(/^([A-Za-z]+)\d*/)
  const prefix = match ? match[1].toUpperCase() : '' // Extract prefix

  for (const [category, { prefixes }] of Object.entries(documentTypes)) {
    if (prefixes.includes(prefix)) documentClass.value = category
  }
}

/** Watch the entity identifier and pre-populate document category when there is a prefix match **/
watch(() => consumerIdentifier.value, (id: string) => {
  // Format Entity Identifier
  consumerIdentifier.value = id.replace(/\s+/g, '')?.toUpperCase()
  // Assign and populate a prefix if a match is found
  if (id.length >= 1) findCategoryByPrefix(id)
})

/** Reset Entity Identifier when No Id Checkbox is selected **/
watch(() => noIdCheckbox.value, (hasNoId: boolean) => {
  if (hasNoId) consumerIdentifier.value = ''
})

/** Reset Document Type when Category Changes **/
watch(() => documentClass.value, () => {
 documentType.value = ''
})
</script>
<template>
  <FormWrapper
    id="document-indexing-form"
    name="document-indexing-form"
    class="rounded"
  >
    <template #label>
      <h2 class="text-[16px] leading-6 font-bold">{{ $t('documentIndexing.label') }}</h2>
    </template>

    <template #form>
      <div class="grid grid-flow-row auto-rows-max">
        <UFormGroup
          :label="$t('documentIndexing.form.id.label')"
          :description="$t('documentIndexing.form.id.description')"
          :help="$t('documentIndexing.form.id.help')"
          :error="hasIdError && 'Enter entity ID'"
        >
          <UInput
            v-model="consumerIdentifier"
            class="mt-3"
            type="text"
            required
            :disabled="noIdCheckbox"
            :placeholder="$t('documentIndexing.form.id.label')"
            :ui="{ placeholder: hasIdError ? 'placeholder:text-red-500' : 'text-gray-700' }"
          />
        </UFormGroup>

        <UCheckbox
          v-model="noIdCheckbox"
          class="mt-5"
          name="unknown-id-checkbox"
          :label="$t('documentIndexing.form.checkbox.label')"
        />

        <UDivider class="my-7" />

        <UFormGroup
          :label="$t('documentIndexing.form.selectMenu.label')"
        >
          <div class="grid grid-cols-4 gap-5 mt-3">
            <div class="col-span-2">
              <UFormGroup :error="hasClassError && 'Select document category'">
                <USelectMenu
                  v-model="documentClass"
                  :placeholder="$t('documentIndexing.form.selectMenu.categoryLabel')"
                  select-class="text-gray-700"
                  :options="getCategories()"
                  :ui="{ placeholder: hasClassError ? 'placeholder:text-red-500' : 'text-gray-700' }"
                />
              </UFormGroup>
            </div>

            <div class="col-span-2">
              <UFormGroup :error="hasTypeError && 'Select document type'">
                <USelectMenu
                  v-model="documentType"
                  :placeholder="$t('documentIndexing.form.selectMenu.typeLabel')"
                  select-class="text-gray-700"
                  :disabled="!documentClass"
                  :options="getDocumentsByCategory(documentClass)"
                  :ui="{ placeholder: hasTypeError ? 'placeholder:text-red-500' : 'text-gray-700' }"
                />
              </UFormGroup>
            </div>
          </div>
        </UFormGroup>

        <UDivider class="my-7" />

        <UFormGroup
          :label="$t('documentIndexing.form.dateSelect.label')"
          :description="$t('documentIndexing.form.dateSelect.description')"
          :error="hasDateError && 'Select a filing date'"
        >
          <InputDatePicker
            v-model="consumerFilingDate"
            class="mt-3"
            :ui="{ placeholder: hasDateError ? 'placeholder:text-red-500' : 'text-gray-700' }"
          />
        </UFormGroup>

      </div>
    </template>
  </FormWrapper>
</template>
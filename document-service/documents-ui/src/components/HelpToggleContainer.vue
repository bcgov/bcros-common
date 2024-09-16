<script setup lang="ts">
const isHelpContentOpen = ref(false)
const hasBottomHideToggle = ref(true)
</script>
<template>
  <div class="my-2">
    <ULink
      class="flex items-center text-primary font-bold"
      @click="isHelpContentOpen = !isHelpContentOpen"
    >
    <UIcon
      name="i-mdi-help-circle-outline"
      class="font-bold w-5 h-5 mx-2"
    ></UIcon>
      <p>{{ $t('documentSearch.helpTitle.inactive') }}</p>
    </ULink>
    <div>
      <div v-show="isHelpContentOpen">
        <slot
          name="content"
          class="text-light"
        />
        <div
          v-if="hasBottomHideToggle"
          class="float-right"
        >
          <ULink
            class="text-primary text-light underline"
            @click="isHelpContentOpen = !isHelpContentOpen"
          >
          {{ $t('documentSearch.helpTitle.active') }}
          </ULink>
        </div>
      </div>
    </div>
  </div>
</template>

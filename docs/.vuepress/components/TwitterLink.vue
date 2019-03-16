<template>
  <custom-link href="https://twitter.com/bocadillopy" :text="text"/>
</template>

<script>
export default {
  props: {
    text: {
      default: `@bocadillopy`
    }
  }
};
</script>

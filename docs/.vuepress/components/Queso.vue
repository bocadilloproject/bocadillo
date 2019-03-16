<template>
  <custom-link :href="$project.queso" :text="text"/>
</template>

<script>
export default {
  props: {
    text: {
      default: "Queso"
    }
  }
};
</script>

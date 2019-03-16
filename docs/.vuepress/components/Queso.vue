<template>
  <custom-link href="https://bocadilloproject.github.io/queso" :text="text"/>
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

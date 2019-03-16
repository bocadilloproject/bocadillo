<template>
  <custom-link :href="$project.issues" :text="text"/>
</template>

<script>
export default {
  props: ["text"]
};
</script>

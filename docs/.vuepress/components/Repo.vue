<template>
  <custom-link :href="$project.repoLink" :text="text"/>
</template>

<script>
export default {
  props: ["text"]
};
</script>

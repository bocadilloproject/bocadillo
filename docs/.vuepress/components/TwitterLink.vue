<template>
  <custom-link :href="$project.twitter" :text="text"/>
</template>

<script>
import project from "../project";
export default {
  props: {
    text: {
      default: `@${project.twitterUser}`
    }
  }
};
</script>

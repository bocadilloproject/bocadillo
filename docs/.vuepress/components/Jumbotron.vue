<template>
  <section class="wrapper header">
    <h1>{{ title }}</h1>
    <p v-if="description">{{ description }}</p>
  </section>
</template>

<script>
export default {
  props: {
    title: {
      type: String
    },
    description: {
      type: String
    }
  }
};
</script>


<style lang="stylus" scoped>
h1 {
  padding-bottom: 0;
  margin-bottom: 0;
  font-size: 3.5em;
}

.header {
  text-align: center;
  padding-top: 0.5em;
  padding-bottom: 0.5em;
}
</style>

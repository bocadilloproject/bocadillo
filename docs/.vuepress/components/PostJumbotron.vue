<template>
  <section class="wrapper">
    <h1>{{ post.title }}</h1>
    <PostMeta :post="post"/>
    <p v-if="post.description">{{ post.description }}</p>
  </section>
</template>

<script>
export default {
  props: {
    post: {
      type: Object
    }
  }
};
</script>


<style lang="stylus" scoped>
h1 {
  padding: 0;
  margin: 0;
  font-size: 3em;
  font-weight: bolder;
}
</style>

<template>
  <div>
    <b-ul v-for="item in items" :key="item.title">
      <li>
        <b-link :icon="item.icon || icons" :to="item.path">{{ item.title }}</b-link>
      </li>
    </b-ul>
  </div>
</template>

<script>
export default {
  props: ["items", "icons"]
};
</script>

<style scoped>
li {
  padding-top: 0.3rem;
}
</style>

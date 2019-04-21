<template>
  <div class="home">
    <div class="hero">
      <img id="hero-image" v-if="data.heroImage" :src="$withBase(data.heroImage)" alt="hero">

      <h1 id="title">{{ data.heroText || $title || 'Hello' }}</h1>

      <p
        id="description"
        class="description"
      >{{ data.tagline || $description || 'Welcome to your VuePress site' }}</p>

      <p>
        <iframe
          src="https://ghbtns.com/github-btn.html?user=bocadilloproject&repo=bocadillo&type=star&count=true&size=large"
          frameborder="0"
          scrolling="0"
          width="130px"
          height="30px"
        ></iframe>
      </p>

      <p class="action" v-if="data.actionText && data.actionLink">
        <NavLink class="action-button" :item="actionLink"/>
      </p>
    </div>

    <div class="features" v-if="data.features && data.features.length">
      <div class="feature" v-for="(feature, index) in data.features" :key="index">
        <h2>{{ feature.title }}</h2>
        <p>{{ feature.details }}</p>
      </div>
    </div>

    <Content custom/>

    <div class="footer" v-if="data.footer">{{ data.footer }}</div>
  </div>
</template>

<script>
import NavLink from "@theme/NavLink.vue";

export default {
  components: { NavLink },

  computed: {
    data() {
      return this.$page.frontmatter;
    },

    actionLink() {
      return {
        link: this.data.actionLink,
        text: this.data.actionText
      };
    }
  }
};
</script>

<style lang="stylus" scoped>
.home {
  padding-top: 0 !important;
}

#hero-image {
  margin-top: 1em;
  margin-bottom: 0;
}

#title {
  margin-top: 0;
  margin-bottom: 0;
}

#description {
  margin-top: 0.5rem;
}
</style>

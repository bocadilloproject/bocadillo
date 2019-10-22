<template>
  <main class="home" aria-labelledby="main-title">
    <DeprecationWarning style="margin-top: 1rem;" />

    <header class="hero">
      <img v-if="data.heroImage" :src="$withBase(data.heroImage)" alt="hero" />

      <h1 id="main-title">{{ data.heroText || $title }}</h1>

      <p class="description" v-html="data.tagline || $description"></p>

      <p>
        <StarButton />
      </p>

      <b-action-link
        :to="data.actionLink"
        :text="data.actionText"
        :primary="true"
      />

      <p>
        Latest release:
        <strong>{{ $version }}</strong>
      </p>
    </header>

    <div id="home-main">
      <Content class="theme-default-content custom home-content" />
      <HomeSideBar />
    </div>

    <div class="footer" v-if="data.footer">{{ data.footer }}</div>
  </main>
</template>

<script>
import Home from "@theme/components/Home.vue";

export default {
  extends: Home, // Get default styles
  computed: {
    data() {
      return this.$page.frontmatter;
    }
  }
};
</script>

<style lang="stylus" scoped>
@import './config.styl';

.hero img {
  margin-top: 1em;
  margin-bottom: 0;
}

#main-title {
  margin-top: 0;
  margin-bottom: 0;
}

.description {
  margin-top: 0.5rem;
}

#home-main {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-column-gap: 4rem;
  margin-top: 3rem;
}

@media (max-width: $MQMobile) {
  .home-content {
    padding: 0 2rem;
  }

  #home-main {
    display: block;
  }
}
</style>

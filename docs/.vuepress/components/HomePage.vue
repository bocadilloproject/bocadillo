<template>
  <div class="home">
    <div class="hero">
      <img id="hero-image" v-if="data.heroImage" :src="$withBase(data.heroImage)" alt="hero">

      <h1 id="title">{{ data.heroText || $title }}</h1>

      <p id="description" class="description" v-html="data.tagline || $description"></p>

      <p>
        <StarButton/>
      </p>

      <b-action-link :to="data.actionLink" :text="data.actionText" :primary="true"/>

      <p>
        Latest release:
        <strong>{{ $version }}</strong>
      </p>
    </div>

    <div id="home-main">
      <Content custom class="home-content"/>
      <HomeSideBar/>
    </div>

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
    }
  }
};
</script>

<style lang="stylus" scoped>
@import './config.styl';

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

#home-main {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-column-gap: 4rem;
  margin-top: 3rem;
}

@media (max-width: $MQMobile) {
  .home {
    padding: 0 !important;
  }

  .home-content {
    padding: 0 2rem;
  }

  #home-main {
    display: block;
  }
}
</style>

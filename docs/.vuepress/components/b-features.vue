<template>
  <b-ul>
    <li v-for="feature in displayedFeatures" :key="feature.title" class="b-feature">
      <div>
        <b-icon :name="feature.icon" size="lg" :circle="true" class="feature-icon"/>
      </div>
      <div>
        <h4>{{ feature.title }}</h4>
        <p>{{ feature.details }}</p>
      </div>
    </li>
  </b-ul>
</template>

<script>
import { FEATURES } from "./constants";

export default {
  props: {
    summary: {
      type: Boolean
    }
  },
  computed: {
    displayedFeatures() {
      return this.summary ? FEATURES.slice(0, 3) : FEATURES;
    }
  }
};
</script>

<style lang="stylus" scoped>
@import './config.styl';

.b-feature {
  display: grid;
  grid-template-columns: auto 1fr;
  grid-column-gap: 1.5rem;
  align-items: center;

  h4 {
    margin-bottom: 0;
    color: $textDarkColor;
  }

  p {
    color: textLight;
  }
}

.feature-icon {
  color: $accentColor;
}
</style>

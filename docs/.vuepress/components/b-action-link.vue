<template>
  <p class="b-action">
    <NavLink class="b-action-button" :class="{ primary }" :item="item"/>
  </p>
</template>

<script>
import NavLink from "@theme/components/NavLink.vue";
export default {
  components: { NavLink },
  props: {
    to: {
      type: String
    },
    text: {
      type: String
    },
    primary: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    item() {
      return {
        link: this.to,
        text: this.text
      };
    }
  }
};
</script>

<style lang="stylus" scoped>
@import './config.styl';

.b-action {
  text-align: center;
  margin-bottom: 3rem;
}

.b-action-button {
  display: inline-block;
  font-size: 1.2rem;
  padding: 0.8rem 1.6rem;
  border-radius: 4px;
  transition: background-color 0.1s ease, color 0.1s ease;
  box-sizing: border-box;
  border-bottom: 1px solid darken($accentColor, 10%);

  &.primary {
    color: #fff;
    background-color: $accentColor;

    &:hover {
      background-color: lighten($accentColor, 10%);
    }
  }

  &:not(.primary) {
    color: $textLightColor;
    border: 1px solid $textLighterColor;

    &:hover {
      color: $accentColor;
      border-color: $accentColor;
    }
  }
}
</style>

<template>
  <router-link v-if="!isExternal(link)" class="nav-link" :to="link" :exact="true">
    <template v-if="icon">
      <b-icon :name="icon"/>&nbsp;
    </template>
    <span :class="{ more }">
      <slot></slot>
    </span>
  </router-link>
  <a v-else class="nav-link external" :href="link" target="_blank" rel="noopener noreferrer">
    <template v-if="icon">
      <b-icon :name="icon"/>&nbsp;
    </template>
    <span :class="{ more }">
      <slot></slot>
    </span>
    <OutboundLink/>
  </a>
</template>

<script>
import { ensureExt, isExternal } from "@theme/util";

export default {
  props: {
    to: {
      type: String,
      required: true
    },
    icon: {
      type: String
    },
    more: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    link() {
      return ensureExt(this.to);
    }
  },
  methods: { isExternal }
};
</script>

<style lang="stylus" scoped>
.more {
  text-transform: uppercase;
  font-size: small;
  font-weight: bold;

  &::after {
    content: ' →';
  }
}
</style>

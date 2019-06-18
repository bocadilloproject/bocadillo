<template>
  <i :class="{ circle }" v-if="octicon" v-html="svg"/>
</template>

<script>
import * as octicons from "octicons";

const SIZE_TO_WIDTH = {
  md: null,
  lg: 20
};

export default {
  props: {
    name: {
      type: String
    },
    size: {
      type: String,
      default: "md"
    },
    circle: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    octicon() {
      return octicons[this.name];
    },
    width() {
      return SIZE_TO_WIDTH[this.size];
    },
    svg() {
      const options = this.width
        ? { width: this.width, height: this.width }
        : {};
      return this.octicon.toSVG(options);
    }
  }
};
</script>

<style lang="stylus" scoped>
.circle {
  border: 1px solid;
  border-radius: 50%;
  padding: 1rem;
}
</style>

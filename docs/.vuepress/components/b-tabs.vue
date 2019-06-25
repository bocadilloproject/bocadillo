<template>
  <div class="button-group">
    <button
      v-for="tab in tabs"
      :key="tab.label"
      @click="onSelect(tab)"
      :class="{selected: isSelected(tab)}"
    >{{ tab.label }}</button>
  </div>
</template>

<script>
export default {
  props: {
    tabs: {
      type: Array
    },
    initialIndex: {
      type: Number,
      default: 0
    }
  },
  data: () => ({ selectedTab: null }),
  mounted() {
    this.onSelect(this.tabs[this.initialIndex]);
  },
  methods: {
    isSelected(tab) {
      return this.selectedTab ? tab.label === this.selectedTab.label : false;
    },
    onSelect(tab) {
      this.selectedTab = tab;
      this.$emit("selected", tab);
    }
  }
};
</script>

<style lang="stylus" scoped>
.button-group {
  width: fit-content;
  width: -moz-fit-content;

  button.selected {
    border-bottom: 3px solid $accentColor;
  }
}
</style>

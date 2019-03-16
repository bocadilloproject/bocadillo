<template>
  <a :href="href" target="_blank">
    {{text}}
    <OutboundLink/>
  </a>
</template>

<script>
export default {
  props: {
    href: {
      type: String,
      required: true
    },
    text: {
      type: String,
      required: true
    }
  }
};
</script>

<template>
  <div class="content deprecation-warning">
    <p>
      <strong>Warning:</strong> Bocadillo is now <strong>UNMAINTAINED</strong>.
      Users are recommended to migrate to a supported alternative, such as
      <a href="https://www.starlette.io" target="_blank" rel="noreferrer"
        >Starlette</a
      >
      or
      <a href="https://fastapi.tiangolo.com" target="_blank" rel="noreferrer"
        >FastAPI</a
      >. Please see
      <a
        href="https://github.com/bocadilloproject/bocadillo/issues/334"
        target="_blank"
        rel="noreferrer"
        >#344</a
      >
      for more information.
    </p>
  </div>
</template>

<script>
export default {
  name: "DeprecationWarning"
};
</script>

<style lang="stylus" scoped>
.deprecation-warning {
  $bg = #fa6b5a;
  padding: 0 2rem;
  border: 1px solid $bg;
  background-color: rgba($bg, 20%);
  border-radius: 4px;
}
</style>

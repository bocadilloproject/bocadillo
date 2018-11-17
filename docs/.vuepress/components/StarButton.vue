<template>
    <iframe class="star-button" :src="src"
            frameborder="0"
            scrolling="0"
            width="150px"
            height="30px"></iframe>
</template>

<script>
    export default {
        props: ['repo'],
        computed: {
            src() {
                const [user, repo] = this.repo.split('/');
                return `https://ghbtns.com/github-btn.html?user=${user}&repo=${repo}&type=star&count=true&size=large`;
            },
        },
    };
</script>

<style>
    .star-button {
        position: absolute;
        right: 1em;
        top: 4.5em;
    }
</style>